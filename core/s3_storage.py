import boto3
import os
from botocore.exceptions import NoCredentialsError

class S3Manager:
    def __init__(self, bucket_name: str = None):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = bucket_name or os.environ.get('S3_BUCKET_NAME')

    def upload_file(self, local_path: str, s3_path: str = None) -> bool:
        """
        Uploads a local file to S3.
        """
        if s3_path is None:
            s3_path = os.path.basename(local_path)
            
        try:
            self.s3.upload_file(local_path, self.bucket_name, s3_path)
            print(f"File {local_path} uploaded to s3://{self.bucket_name}/{s3_path}")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

    def download_file(self, s3_path: str, local_path: str) -> bool:
        """
        Downloads a file from S3 to a local path.
        """
        try:
            self.s3.download_file(self.bucket_name, s3_path, local_path)
            print(f"File s3://{self.bucket_name}/{s3_path} downloaded to {local_path}")
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

    def list_files(self):
        """
        Lists files in the S3 bucket.
        """
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
