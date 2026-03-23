from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    plan: str
    context: list
    safety_status: str
    final_answer: str
    steps: list[str]  # Agent Trace: ["retrieved data", "reasoned response", ...]
    metadata: dict    # For LLM metrics (tokens, cost, latency)
