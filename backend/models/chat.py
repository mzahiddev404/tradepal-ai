"""
Data models for chat API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str = Field(..., description="User message", min_length=1)
    history: Optional[List[ChatMessage]] = Field(
        default=[], 
        description="Conversation history"
    )


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    message: str = Field(..., description="AI response message")
    status: str = Field(default="success", description="Response status")






