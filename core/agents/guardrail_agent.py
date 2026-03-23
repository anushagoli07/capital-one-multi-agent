import time
from core.agent_state import AgentState
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from utils.logger import metrics_logger
from governance.policy import GovernancePolicy

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
governance = GovernancePolicy()

def node_input_guardrail(state: AgentState) -> dict:
    query = state["query"]
    
    # 1. PII/Governance
    is_safe, detail = governance.validate_query(query)
    if not is_safe:
        return {"safety_status": f"Blocked: {detail}", "steps": ["Input Guardrail: Blocked by PII"]}
        
    # 2. LLM Hybrid Validation
    prompt = f"""
    Is the following query related to financial products, credit cards, banking, accounts, or just casual greeting?
    If it is a safe greeting or financial question, answer YES.
    If it is off-topic (e.g., cooking, jokes, completely unrelated), answer NO.
    Query: "{query}"
    Answer YES or NO only.
    """
    
    start_time = time.time()
    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        latency = time.time() - start_time
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        
        metrics_logger.log_event({
            "query": query,
            "latency": latency,
            "tokens": tokens,
            "cost": tokens * 0.000002,
            "agent": "input_guardrail_validator"
        })
        
        if "NO" in response.content.upper():
            return {"safety_status": "Blocked: Off-Topic", "steps": ["Input Guardrail: Blocked Off-Topic"]}
            
    except Exception as e:
        return {"safety_status": "Cleared", "steps": [f"Input Guardrail: LLM Validator fallback error {e}"]}
        
    return {"safety_status": "Cleared", "steps": ["Input Guardrail: Cleared"]}

def node_output_guardrail(state: AgentState) -> dict:
    answer = state.get("final_answer", "")
    
    # Output fairness/policy check could go here
    # Since we use LLM for output, we just log and pass through for now or perform basic checks
    
    return {"steps": ["Output Guardrail: Cleared"]}
