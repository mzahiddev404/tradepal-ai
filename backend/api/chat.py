"""
Chat API endpoints.
"""
from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest, ChatResponse
from utils.langchain_agent import chat_agent

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


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "tradepal-ai-backend"}





