"""
Chat / AI Agent API routes.
"""

from fastapi import APIRouter
from app.schemas.schemas import ChatRequest, ChatResponse
from app.graph.graph import run_agent

router = APIRouter(prefix="/api", tags=["AI Agent"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest):
    """
    Send a message to the AI CRM assistant.
    The agent will classify intent, route to the appropriate tool,
    and return a structured response.
    """
    # Convert conversation history to list of dicts
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in (request.conversation_history or [])
    ]

    # Run the LangGraph agent
    result = run_agent(
        user_input=request.message,
        conversation_history=history,
        current_doctor=request.current_doctor
    )

    return ChatResponse(
        message=result["message"],
        extracted_entities=result.get("extracted_entities"),
        tool_used=result.get("tool_used"),
        interaction_id=result.get("interaction_id"),
        data={"intent": result.get("intent", "")},
    )


@router.post("/agent", response_model=ChatResponse)
def invoke_agent(request: ChatRequest):
    """
    Direct agent invocation endpoint.
    Same as /chat but semantically indicates a direct agent call.
    """
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in (request.conversation_history or [])
    ]

    result = run_agent(
        user_input=request.message,
        conversation_history=history,
        current_doctor=request.current_doctor
    )

    return ChatResponse(
        message=result["message"],
        extracted_entities=result.get("extracted_entities"),
        tool_used=result.get("tool_used"),
        interaction_id=result.get("interaction_id"),
        data={"intent": result.get("intent", "")},
    )
