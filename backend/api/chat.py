"""
Chat API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from models.chat import ChatRequest, ChatResponse
from utils.langchain_agent import chat_agent
from utils.multi_agent_system import multi_agent_system
import json
import asyncio
import uuid

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    use_multi_agent: bool = Query(True, description="Use multi-agent system for routing")
):
    """
    Handle chat requests with optional multi-agent routing.
    
    Args:
        request: ChatRequest with message and optional history
        use_multi_agent: Whether to use multi-agent system (default: True)
        
    Returns:
        ChatResponse with AI-generated message and agent info
    """
    try:
        # Convert history to dict format for agent
        history = [msg.model_dump() for msg in request.history]
        
        # Generate session ID if not provided (for caching in billing agent)
        session_id = str(uuid.uuid4())
        
        # Use multi-agent system if enabled
        if use_multi_agent:
            result = await multi_agent_system.process_message(
                message=request.message,
                history=history,
                session_id=session_id,
                use_multi_agent=True
            )
            response_text = result["response"]
            agent_name = result.get("agent_name", "GENERAL_AGENT")
        else:
            # Use direct agent (backward compatibility)
            response_text = await chat_agent.get_response(
                message=request.message,
                history=history
            )
            agent_name = "GENERAL_AGENT"
        
        return ChatResponse(
            message=response_text,
            status="success",
            agent_name=agent_name
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Handle chat requests with streaming response.
    
    Args:
        request: ChatRequest with message and optional history
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    async def generate():
        try:
            # Convert history to dict format for agent
            history = [msg.model_dump() for msg in request.history]
            
            # Get streaming response from agent
            async for chunk in chat_agent.get_response_stream(
                message=request.message,
                history=history
            ):
                # Format as Server-Sent Event
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
            
        except Exception as e:
            error_data = json.dumps({'error': str(e), 'done': True})
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "tradepal-ai-backend"}










