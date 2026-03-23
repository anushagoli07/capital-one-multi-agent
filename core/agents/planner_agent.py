import time
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from core.agent_state import AgentState
from utils.logger import metrics_logger

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def node_planner(state: AgentState) -> dict:
    query = state["query"]
    
    prompt = f"""
    You are a financial AI planner. 
    Analyze the user query: "{query}" and the conversation history.
    Devise a short, step-by-step plan for the Reasoning Agent.
    """
    
    start_time = time.time()
    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        latency = time.time() - start_time
        plan = response.content
        
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        metrics_logger.log_event({
            "query": query,
            "latency": latency,
            "tokens": tokens,
            "cost": tokens * 0.000002,
            "agent": "planner"
        })
        
        return {"plan": plan, "steps": [f"Planner: Generated plan"]}
    except Exception as e:
        return {"plan": f"Plan bypassed due to error: {e}", "steps": ["Planner: Failed/Skipped"]}
