import boto3
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
ECR_REPO_NAME = "capital-one-ai-assistant"
IMAGE_TAG = "latest"
SERVICE_NAME = "capital-one-ai-langgraph"

def execute_cmd(cmd):
    print(f"Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error Output: {result.stderr}")
        raise Exception(f"Command failed with exit code {result.returncode}")
    return result.stdout.strip()

def deploy():
    print("[*] Initiating Cloud Deployment to AWS AppRunner...")
    
    sts = boto3.client('sts', region_name=REGION)
    try:
        account_id = sts.get_caller_identity()['Account']
    except Exception as e:
        print("[-] AWS Credentials not found or invalid. Please configure AWS CLI.")
        return

    ecr = boto3.client('ecr', region_name=REGION)
    
    # 1. Create ECR Repo if not exists
    try:
        ecr.describe_repositories(repositoryNames=[ECR_REPO_NAME])
        print(f"[+] ECR repository '{ECR_REPO_NAME}' already exists.")
    except ecr.exceptions.RepositoryNotFoundException:
        print(f"[*] Creating ECR repository '{ECR_REPO_NAME}'...")
        ecr.create_repository(repositoryName=ECR_REPO_NAME)
        print("[+] Repository created.")
        
    ecr_uri = f"{account_id}.dkr.ecr.{REGION}.amazonaws.com/{ECR_REPO_NAME}"
    full_image_name = f"{ecr_uri}:{IMAGE_TAG}"
    
    # 2. Authenticate Docker to ECR
    print("[*] Authenticating Docker with ECR...")
    try:
        # Get ECR auth token via boto3 instead of AWS CLI
        auth_response = ecr.get_authorization_token()
        auth_data = auth_response['authorizationData'][0]
        token = auth_data['authorizationToken']
        import base64
        # Decode token (format is AWS:password)
        decoded_token = base64.b64decode(token).decode('utf-8')
        password = decoded_token.split(':')[1]
        
        # Run docker login
        login_cmd = f"docker login --username AWS --password {password} {auth_data['proxyEndpoint']}"
        execute_cmd(login_cmd)
        print("[+] Docker authenticated.")
    except Exception as e:
        print(f"[-] Docker authentication failed: {e}")
        print("[!] Ensure Docker Desktop is running.")
        return
    
    # 3. Build & Push Docker Image
    print("[*] Building Docker image (this may take a few minutes)...")
    try:
        execute_cmd(f"docker build -t {ECR_REPO_NAME} .")
        execute_cmd(f"docker tag {ECR_REPO_NAME}:{IMAGE_TAG} {full_image_name}")
        print("[+] Image built successfully. Pushing to ECR...")
        execute_cmd(f"docker push {full_image_name}")
        print("[+] Image pushed to ECR.")
    except Exception as e:
        print("[-] Docker build or push failed.")
        return
    
    # 4. Deploy to AppRunner
    print("[*] Deploying to AWS AppRunner...")
    apprunner = boto3.client('apprunner', region_name=REGION)
    
    services = apprunner.list_services()
    service_arn = None
    for s in services.get('ServiceSummaryList', []):
        if s['ServiceName'] == SERVICE_NAME:
            service_arn = s['ServiceArn']
            break
            
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        print("[!] Warning: OPENAI_API_KEY is not set. AppRunner service will likely fail at runtime.")

    source_config = {
        'ImageRepository': {
            'ImageIdentifier': full_image_name,
            'ImageConfiguration': {
                'Port': '8000',
                'RuntimeEnvironmentVariables': {
                    'OPENAI_API_KEY': api_key
                }
            },
            'ImageRepositoryType': 'ECR'
        },
        'AutoDeploymentsEnabled': True
    }
    
    iam = boto3.client('iam')
    try:
        role = iam.get_role(RoleName='AppRunnerECRAccessRole')
        source_config['AuthenticationConfiguration'] = {'AccessRoleArn': role['Role']['Arn']}
    except Exception:
        print("[!] Warning: 'AppRunnerECRAccessRole' not found. AppRunner might not have permission to pull the ECR image.")

    try:
        if service_arn:
            print(f"[*] Updating existing AppRunner service '{SERVICE_NAME}'...")
            apprunner.update_service(ServiceArn=service_arn, SourceConfiguration=source_config)
            print(f"[+] Service update initiated!")
        else:
            print(f"[*] Creating new AppRunner service '{SERVICE_NAME}'...")
            response = apprunner.create_service(
                ServiceName=SERVICE_NAME,
                SourceConfiguration=source_config,
                InstanceConfiguration={'Cpu': '1 vCPU', 'Memory': '2 GB'}
            )
            service_arn = response['Service']['ServiceArn']
            print(f"[+] Service creation initiated!")
            
        print(f"\n[+] Deployment is rolling out. Service ARN:\n{service_arn}")
        print("Check the AWS Console -> AppRunner for the public frontend URL.")
    except Exception as e:
        print(f"[-] AppRunner deployment failed: {e}")

if __name__ == "__main__":
    deploy()
