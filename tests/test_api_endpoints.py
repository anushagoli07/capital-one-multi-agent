import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "agent_mode" in response.json()

@patch('api.main.graph_app.invoke')
def test_query_endpoint(mock_invoke):
    # Mock the LangGraph response
    mock_invoke.return_value = {
        "final_answer": "This is a mocked answer for Venture X.",
        "safety_status": "Cleared",
        "steps": ["Input Cleared", "Planner: Generated plan", "Reasoning: LLM Invoked", "Finalized Answer"]
    }

    payload = {
        "question": "What is Venture X?",
        "thread_id": "test_thread_1"
    }

    response = client.post("/query", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a mocked answer for Venture X."
    assert data["safety_status"] == "Cleared"
    assert "latency_ms" in data
    assert "trace" in data
    assert len(data["trace"]["steps"]) == 4

@patch('api.main.graph_app.invoke')
def test_query_endpoint_cached(mock_invoke):
    # Second call should be cached (assuming the previous test populated the cache in the global logger)
    from utils.logger import metrics_logger
    metrics_logger.set_cache("Cached Question", {"answer": "Cached Answer", "safety_status": "Cleared", "trace": {}})
    
    payload = {
        "question": "Cached Question",
        "thread_id": "test_thread_2"
    }

    response = client.post("/query", json=payload)
    
    assert response.status_code == 200
    assert response.json()["answer"] == "Cached Answer"
    # Ensure invoke wasn't called for the cached query
    mock_invoke.assert_not_called()
