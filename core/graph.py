from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from core.agent_state import AgentState
from core.agents.guardrail_agent import node_input_guardrail, node_output_guardrail
from core.agents.planner_agent import node_planner
from core.agents.reasoning_agent import node_reasoning, tools

def route_input_guardrail(state: AgentState):
    if "Blocked" in state.get("safety_status", ""):
        return "blocked"
    return "cleared"

def route_reasoning(state: AgentState):
    messages = state.get("messages", [])
    if not messages:
        return "end" # early exit if failed
        
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "output_guardrail"

def finalize_answer(state: AgentState):
    messages = state.get("messages", [])
    if messages and hasattr(messages[-1], "content"):
        return {"final_answer": messages[-1].content, "steps": ["Finalized Answer"]}
    return {"steps": ["Finalize Fallback"]}

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("input_guardrail", node_input_guardrail)
workflow.add_node("planner", node_planner)
workflow.add_node("reasoning", node_reasoning)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("finalize", finalize_answer)
workflow.add_node("output_guardrail", node_output_guardrail)

# Edges
workflow.add_edge(START, "input_guardrail")

workflow.add_conditional_edges(
    "input_guardrail",
    route_input_guardrail,
    {
        "blocked": END,
        "cleared": "planner"
    }
)

workflow.add_edge("planner", "reasoning")

# The ReAct Loop
workflow.add_conditional_edges(
    "reasoning",
    route_reasoning,
    {
        "tools": "tools",
        "output_guardrail": "finalize",
        "end": END
    }
)

workflow.add_edge("tools", "reasoning")
workflow.add_edge("finalize", "output_guardrail")
workflow.add_edge("output_guardrail", END)

# Compile with memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
