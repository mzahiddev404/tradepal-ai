"""
Tests for chat API endpoints.
"""
import pytest
from fastapi import status


class TestChatAPI:
    """Test suite for chat endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "tradepal-ai-backend"
    
    def test_chat_endpoint_success(self, client, sample_chat_request):
        """Test successful chat request."""
        response = client.post("/api/chat", json=sample_chat_request)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "success"
        assert "agent_name" in data
    
    def test_chat_endpoint_with_history(self, client):
        """Test chat request with conversation history."""
        request = {
            "message": "What did I just say?",
            "history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        response = client.post("/api/chat", json=request)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert data["status"] == "success"
    
    def test_chat_endpoint_multi_agent_enabled(self, client, sample_chat_request):
        """Test chat with multi-agent system enabled."""
        response = client.post(
            "/api/chat?use_multi_agent=true",
            json=sample_chat_request
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "agent_name" in data
        assert data["agent_name"] in [
            "BILLING_AGENT",
            "TECHNICAL_AGENT",
            "POLICY_AGENT",
            "GENERAL_AGENT"
        ]
    
    def test_chat_endpoint_multi_agent_disabled(self, client, sample_chat_request):
        """Test chat with multi-agent system disabled."""
        response = client.post(
            "/api/chat?use_multi_agent=false",
            json=sample_chat_request
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["agent_name"] == "GENERAL_AGENT"
    
    def test_chat_endpoint_empty_message(self, client):
        """Test chat endpoint with empty message."""
        request = {"message": "", "history": []}
        response = client.post("/api/chat", json=request)
        # Should still process but may return empty or error
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_chat_endpoint_missing_message(self, client):
        """Test chat endpoint with missing message field."""
        request = {"history": []}
        response = client.post("/api/chat", json=request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

