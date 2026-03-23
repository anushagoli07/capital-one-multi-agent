import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage

@pytest.fixture
def mock_llm_invoke():
    with patch('core.agents.planner_agent.ChatOpenAI.invoke') as mock_invoke_planner, \
         patch('core.agents.guardrail_agent.ChatOpenAI.invoke') as mock_invoke_guardrail, \
         patch('core.agents.reasoning_agent.ChatOpenAI.invoke') as mock_invoke_reasoner:
        
        mock_msg = MagicMock(spec=AIMessage)
        mock_msg.content = "Mocked LLM Response"
        mock_msg.response_metadata = {"token_usage": {"total_tokens": 10}}
        
        mock_invoke_planner.return_value = mock_msg
        mock_invoke_guardrail.return_value = mock_msg
        mock_invoke_reasoner.return_value = mock_msg
        
        yield {
            "planner": mock_invoke_planner,
            "guardrail": mock_invoke_guardrail,
            "reasoner": mock_invoke_reasoner
        }

def test_planner_agent(mock_llm_invoke):
    from core.agents.planner_agent import node_planner
    state = {"query": "Test query", "messages": []}
    result = node_planner(state)
    assert "plan" in result
    assert "steps" in result
    assert result["plan"] == "Mocked LLM Response"

def test_input_guardrail_safe(mock_llm_invoke):
    from core.agents.guardrail_agent import node_input_guardrail
    mock_msg = MagicMock(spec=AIMessage)
    mock_msg.content = "YES"
    mock_msg.response_metadata = {"token_usage": {"total_tokens": 5}}
    mock_llm_invoke["guardrail"].return_value = mock_msg

    with patch('governance.policy.GovernancePolicy.validate_query') as mock_gov:
        mock_gov.return_value = (True, "Safe")
        state = {"query": "Tell me about Venture X."}
        result = node_input_guardrail(state)
        assert result["safety_status"] == "Cleared"

def test_input_guardrail_unsafe_llm(mock_llm_invoke):
    from core.agents.guardrail_agent import node_input_guardrail
    mock_msg = MagicMock(spec=AIMessage)
    mock_msg.content = "NO, this is about a joke."
    mock_msg.response_metadata = {"token_usage": {"total_tokens": 5}}
    mock_llm_invoke["guardrail"].return_value = mock_msg

    with patch('governance.policy.GovernancePolicy.validate_query') as mock_gov:
        mock_gov.return_value = (True, "Safe")
        state = {"query": "Tell me a joke."}
        result = node_input_guardrail(state)
        assert "Blocked: Off-Topic" in result["safety_status"]

@patch('core.agents.retriever_agent.retrieve_financial_docs.invoke')
def test_retriever_tool(mock_invoke):
    mock_invoke.return_value = "Mocked credit card info"
    from core.agents.retriever_agent import retrieve_financial_docs
    result = retrieve_financial_docs.invoke({"query": "credit cards"})
    assert "Mocked" in result
