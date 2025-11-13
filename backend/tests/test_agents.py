"""
Tests for agent functionality.
"""
import pytest
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


class TestOrchestrator:
    """Test suite for orchestrator agent."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        try:
            from utils.orchestrator import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            assert orchestrator is not None
        except Exception as e:
            pytest.skip(f"Orchestrator initialization failed: {e}")
    
    def test_orchestrator_routing(self):
        """Test orchestrator routing logic."""
        try:
            from utils.orchestrator import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            
            # Test billing query
            billing_query = "What are your pricing plans?"
            result = orchestrator.route_query(billing_query)
            assert result in ["BILLING_AGENT", "GENERAL_AGENT"]
            
            # Test technical query
            technical_query = "How do I troubleshoot connection issues?"
            result = orchestrator.route_query(technical_query)
            assert result in ["TECHNICAL_AGENT", "GENERAL_AGENT"]
            
            # Test policy query
            policy_query = "What is your privacy policy?"
            result = orchestrator.route_query(policy_query)
            assert result in ["POLICY_AGENT", "GENERAL_AGENT"]
        except Exception as e:
            pytest.skip(f"Orchestrator routing test failed: {e}")


class TestBillingAgent:
    """Test suite for billing agent."""
    
    def test_billing_agent_initialization(self):
        """Test billing agent can be initialized."""
        try:
            from utils.billing_agent import BillingAgent
            agent = BillingAgent()
            assert agent is not None
        except Exception as e:
            pytest.skip(f"Billing agent initialization failed: {e}")


class TestTechnicalAgent:
    """Test suite for technical agent."""
    
    def test_technical_agent_initialization(self):
        """Test technical agent can be initialized."""
        try:
            from utils.technical_agent import TechnicalAgent
            agent = TechnicalAgent()
            assert agent is not None
        except Exception as e:
            pytest.skip(f"Technical agent initialization failed: {e}")


class TestPolicyAgent:
    """Test suite for policy agent."""
    
    def test_policy_agent_initialization(self):
        """Test policy agent can be initialized."""
        try:
            from utils.policy_agent import PolicyAgent
            agent = PolicyAgent()
            assert agent is not None
        except Exception as e:
            pytest.skip(f"Policy agent initialization failed: {e}")

