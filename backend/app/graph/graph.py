"""
LangGraph agent workflow for the AI CRM assistant.

Flow:
  User Input → Intent Detection → Router → Tool Execution → LLM Response → Output

This implements a genuine multi-step agent with routing, tool calling,
and response synthesis — not a simple prompt-response wrapper.
"""

import json
from typing import TypedDict, Annotated, Literal, Sequence
from datetime import date

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.utils.llm import get_llm
from app.prompts.prompts import SYSTEM_PROMPT, INTENT_CLASSIFICATION_PROMPT
from app.tools.tools import (
    log_interaction,
    edit_interaction,
    search_hcp,
    interaction_history,
    followup_recommendation,
)


# ─── Agent State ──────────────────────────────────────────────────────

class AgentState(TypedDict):
    """State that flows through the LangGraph workflow."""
    user_input: str
    conversation_history: list[dict]
    intent: str
    tool_output: str
    final_response: str
    extracted_entities: dict
    interaction_id: int | None
    tool_used: str


# ─── Node Functions ───────────────────────────────────────────────────

def understand_intent(state: AgentState) -> AgentState:
    """
    Node 1: Classify the user's intent to determine which tool to route to.
    Uses the LLM to understand what the user wants to do.
    """
    llm = get_llm(temperature=0.0)

    # Build conversation context
    history_text = ""
    for msg in (state.get("conversation_history") or [])[-6:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        history_text += f"{role}: {content}\n"

    prompt = INTENT_CLASSIFICATION_PROMPT.format(
        user_input=state["user_input"],
        conversation_history=history_text or "No previous context.",
    )

    response = llm.invoke(prompt)
    intent = response.content.strip().lower().strip('"').strip("'")

    # Validate intent
    valid_intents = [
        "log_interaction", "edit_interaction", "search_hcp",
        "interaction_history", "followup_recommendation", "general",
    ]
    if intent not in valid_intents:
        # Fuzzy match
        for valid in valid_intents:
            if valid in intent:
                intent = valid
                break
        else:
            intent = "general"

    state["intent"] = intent
    return state


def route_intent(state: AgentState) -> str:
    """
    Conditional edge: Route to the appropriate tool node based on intent.
    """
    intent = state.get("intent", "general")

    routing_map = {
        "log_interaction": "execute_log",
        "edit_interaction": "execute_edit",
        "search_hcp": "execute_search",
        "interaction_history": "execute_history",
        "followup_recommendation": "execute_recommendation",
        "general": "generate_response",
    }

    return routing_map.get(intent, "generate_response")


def execute_log(state: AgentState) -> AgentState:
    """Node: Execute the log_interaction tool."""
    result = log_interaction.invoke({"user_input": state["user_input"]})
    state["tool_output"] = result
    state["tool_used"] = "log_interaction"

    # Parse entities from result
    try:
        parsed = json.loads(result)
        if parsed.get("success"):
            state["extracted_entities"] = {
                "doctor_name": parsed.get("doctor_name"),
                "doctor_id": parsed.get("doctor_id"),
                "summary": parsed.get("summary"),
                "sentiment": parsed.get("sentiment"),
                "outcome": parsed.get("outcome"),
                "follow_up": parsed.get("follow_up"),
                "topics": parsed.get("topics"),
                "products": parsed.get("products", []),
                "materials": parsed.get("materials", []),
                "samples": parsed.get("samples", []),
                "interaction_type": parsed.get("interaction_type"),
                "date": parsed.get("date"),
            }
            state["interaction_id"] = parsed.get("interaction_id")
    except json.JSONDecodeError:
        pass

    return state


def execute_edit(state: AgentState) -> AgentState:
    """Node: Execute the edit_interaction tool."""
    # Check if there's an interaction_id from context
    interaction_id = state.get("interaction_id")
    result = edit_interaction.invoke({
        "user_input": state["user_input"],
        "interaction_id": interaction_id,
    })
    state["tool_output"] = result
    state["tool_used"] = "edit_interaction"
    return state


def execute_search(state: AgentState) -> AgentState:
    """Node: Execute the search_hcp tool."""
    # Extract search query from user input
    user_input = state["user_input"]
    result = search_hcp.invoke({"query": user_input})
    state["tool_output"] = result
    state["tool_used"] = "search_hcp"
    return state


def execute_history(state: AgentState) -> AgentState:
    """Node: Execute the interaction_history tool."""
    # Extract doctor name from user input
    user_input = state["user_input"]
    result = interaction_history.invoke({"doctor_name": user_input, "limit": 5})
    state["tool_output"] = result
    state["tool_used"] = "interaction_history"
    return state


def execute_recommendation(state: AgentState) -> AgentState:
    """Node: Execute the followup_recommendation tool."""
    user_input = state["user_input"]
    result = followup_recommendation.invoke({"doctor_name": user_input})
    state["tool_output"] = result
    state["tool_used"] = "followup_recommendation"
    return state


def generate_response(state: AgentState) -> AgentState:
    """
    Final node: Generate a natural language response from the tool output
    or handle general conversation.
    """
    llm = get_llm(temperature=0.3)

    tool_output = state.get("tool_output", "")
    tool_used = state.get("tool_used", "")

    # Build messages
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add conversation history
    for msg in (state.get("conversation_history") or [])[-8:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    if tool_output:
        # Synthesize response from tool output
        synthesis_prompt = f"""The user said: "{state['user_input']}"

I used the "{tool_used}" tool and got this result:
{tool_output}

Based on this result, provide a clear, helpful, and conversational response to the user.
If the tool logged an interaction, confirm what was saved and mention key details.
If the tool searched for a doctor, present the results clearly.
If the tool showed history, summarize the key interactions.
If the tool gave recommendations, present them as actionable steps.
If there was an error, explain it and suggest what the user can do.

Be concise but informative. Use bullet points for lists."""

        messages.append(HumanMessage(content=synthesis_prompt))
    else:
        # General conversation
        messages.append(HumanMessage(content=state["user_input"]))

    response = llm.invoke(messages)
    state["final_response"] = response.content
    return state


# ─── Build the Graph ──────────────────────────────────────────────────

def build_agent_graph() -> StateGraph:
    """
    Construct the LangGraph workflow.

    Graph structure:
        understand_intent → route → tool_node → generate_response → END
                                  ↘ (general) → generate_response → END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("understand_intent", understand_intent)
    workflow.add_node("execute_log", execute_log)
    workflow.add_node("execute_edit", execute_edit)
    workflow.add_node("execute_search", execute_search)
    workflow.add_node("execute_history", execute_history)
    workflow.add_node("execute_recommendation", execute_recommendation)
    workflow.add_node("generate_response", generate_response)

    # Set entry point
    workflow.set_entry_point("understand_intent")

    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "understand_intent",
        route_intent,
        {
            "execute_log": "execute_log",
            "execute_edit": "execute_edit",
            "execute_search": "execute_search",
            "execute_history": "execute_history",
            "execute_recommendation": "execute_recommendation",
            "generate_response": "generate_response",
        },
    )

    # All tool nodes lead to response generation
    workflow.add_edge("execute_log", "generate_response")
    workflow.add_edge("execute_edit", "generate_response")
    workflow.add_edge("execute_search", "generate_response")
    workflow.add_edge("execute_history", "generate_response")
    workflow.add_edge("execute_recommendation", "generate_response")

    # Response generation leads to END
    workflow.add_edge("generate_response", END)

    return workflow.compile()


# ─── Compiled Graph Instance ─────────────────────────────────────────

agent_graph = build_agent_graph()


def run_agent(user_input: str, conversation_history: list = None, interaction_id: int = None, current_doctor: str = None) -> dict:
    """
    Run the agent graph with user input and return the result.

    Args:
        user_input: The user's message.
        conversation_history: List of previous messages.
        interaction_id: Optional interaction ID for context.

    Returns:
        Dict with final_response, extracted_entities, tool_used, interaction_id.
    """
    initial_state: AgentState = {
        "user_input": f"[Context: The user currently has doctor {current_doctor} selected in the UI] {user_input}" if current_doctor else user_input,
        "conversation_history": conversation_history or [],
        "intent": "",
        "tool_output": "",
        "final_response": "",
        "extracted_entities": {},
        "interaction_id": interaction_id,
        "tool_used": "",
    }

    result = agent_graph.invoke(initial_state)

    return {
        "message": result.get("final_response", "I couldn't process your request."),
        "extracted_entities": result.get("extracted_entities"),
        "tool_used": result.get("tool_used", ""),
        "interaction_id": result.get("interaction_id"),
        "intent": result.get("intent", ""),
    }
