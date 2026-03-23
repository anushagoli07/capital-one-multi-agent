import time
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.agents.retriever_agent import retrieve_financial_docs
from core.agent_state import AgentState
from utils.logger import metrics_logger

load_dotenv()

tools = [retrieve_financial_docs]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)

def node_reasoning(state: AgentState):
    messages = state.get("messages", [])
    query = state.get("query", "")
    plan = state.get("plan", "")
    
    # Initialize system message if it's the first time
    if not any(isinstance(m, SystemMessage) for m in messages):
        sys_msg = SystemMessage(content=f"You are a Capital One financial assistant. Execution Plan: {plan}")
        # We assume the user's query is already the last message or manually inject it
        messages = [sys_msg] + messages
        
    start_time = time.time()
    try:
        response = llm.invoke(messages)
        latency = time.time() - start_time
        tokens = response.response_metadata.get("token_usage", {}).get("total_tokens", 0)
        
        metrics_logger.log_event({
            "query": query,
            "latency": latency,
            "tokens": tokens,
            "cost": tokens * 0.000002,
            "agent": "reasoning_agent"
        })
        
        return {"messages": [response], "steps": ["Reasoning: LLM Invoked"]}
        
    except Exception as e:
        error_msg = f"Error in reasoning: {str(e)}. Fallback: Please try again."
        return {"final_answer": error_msg, "steps": [f"Reasoning Failed: {e}"]}
