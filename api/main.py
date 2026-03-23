import os
import uuid
import time
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from core.graph import app as graph_app
from mlops.experiment_tracker import ExperimentTracker
from utils.logger import metrics_logger

app = FastAPI(title="Capital One Next-Gen AI Assistant API")

# Initialize MLOps tracker
tracker = ExperimentTracker()

class QueryRequest(BaseModel):
    question: str
    thread_id: str = "default_thread"

from sdk.monitor import monitor

@app.post("/query")
@monitor.log_trace
async def query_assistant(request: QueryRequest):
    """
    LangGraph-based query endpoint with ReAct and Agentic workflows.
    """
    start_time = time.time()
    
    # Feature: Caching optimization
    cached_response = metrics_logger.get_cache(request.question)
    if cached_response:
        return cached_response

    inputs = {
        "query": request.question,
        "messages": [HumanMessage(content=request.question)]
    }
    
    # Feature: Memory / Thread handling
    config = {"configurable": {"thread_id": request.thread_id}}
    
    try:
        # Run the Multi-Agent Flow
        result = graph_app.invoke(inputs, config=config)
    except Exception as e:
        # Failure handling / Robustness
        raise HTTPException(status_code=500, detail=f"Multi-Agent backend error: {str(e)}")
        
    duration = time.time() - start_time
    
    final_answer = result.get("final_answer", "I could not generate an answer.")
    safety_status = result.get("safety_status", "Cleared")
    steps = result.get("steps", [])
    
    # Feature: Observability & MLflow Metrics tracking
    tracker.track_latency("query_endpoint", duration)
    # Estimate sources retrieved based on context or steps (just logging success for now)
    tracker.log_retrieval_success(request.question, len(steps))
    
    response = {
        "answer": final_answer,
        "safety_status": safety_status,
        "latency_ms": int(duration * 1000),
        "model": "gpt-4o-mini (ReAct Agent)",
        "trace": {
            "plan": result.get("plan", "No plan generated"),
            "steps": steps
        }
    }
    
    # Add to cache
    metrics_logger.set_cache(request.question, response)
    
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "gpt-4o-mini", "agent_mode": "LangGraph"}
