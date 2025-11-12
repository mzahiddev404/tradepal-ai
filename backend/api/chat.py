"""
Chat API endpoints.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models.chat import ChatRequest, ChatResponse
from utils.langchain_agent import chat_agent
import json
import asyncio

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat requests.
    
    Args:
        request: ChatRequest with message and optional history
        
    Returns:
        ChatResponse with AI-generated message
    """
    try:
        # Convert history to dict format for agent
        history = [msg.model_dump() for msg in request.history]
        
        # Get response from agent
        response_text = await chat_agent.get_response(
            message=request.message,
            history=history
        )
        
        return ChatResponse(
            message=response_text,
            status="success"
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










