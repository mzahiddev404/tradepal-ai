# Multi-Agent System Implementation

## Overview

The TradePal AI backend implements a multi-agent system using LangGraph for intelligent query routing. The system consists of:

1. **Orchestrator Agent** - Routes queries to appropriate specialized agents
2. **Billing Support Agent** - Hybrid RAG/CAG approach for billing questions
3. **Technical Support Agent** - Pure RAG approach for technical questions
4. **Policy & Compliance Agent** - Pure CAG approach for policy questions
5. **General Agent** - Handles general queries and stock market questions

## Architecture

### Orchestrator Agent (`utils/orchestrator.py`)

- **Purpose**: Analyzes incoming queries and routes them to the most appropriate agent
- **LLM**: AWS Bedrock (Claude 3 Haiku) for fast, cost-effective routing (falls back to OpenAI if not configured)
- **Strategy**: Classification-based routing with low temperature (0.1) for consistency

### Billing Support Agent (`utils/billing_agent.py`)

- **Purpose**: Handles billing, payment, pricing, and subscription questions
- **Strategy**: **Hybrid RAG/CAG**
  - First query: Uses RAG to retrieve billing documents from ChromaDB
  - Subsequent queries: Uses CAG (cached context) for faster responses
- **Caching**: Session-based context caching for improved performance

### Technical Support Agent (`utils/technical_agent.py`)

- **Purpose**: Handles technical support, API usage, troubleshooting, and platform features
- **Strategy**: **Pure RAG**
  - Always retrieves fresh documents from ChromaDB
  - No caching - ensures up-to-date information
- **Use Case**: Dynamic knowledge base that may change frequently

### Policy & Compliance Agent (`utils/policy_agent.py`)

- **Purpose**: Handles Terms of Service, Privacy Policy, compliance, and legal questions
- **Strategy**: **Pure CAG**
  - Pre-loaded policy context (no vector search needed)
  - Fast, consistent answers from static documents
- **Use Case**: Static documents that don't change frequently

### General Agent (`utils/langchain_agent.py`)

- **Purpose**: Handles general queries, stock market questions, and fallback
- **Strategy**: Existing LangChain agent with RAG and stock data integration
- **Use Case**: Stock queries, general conversation, fallback for unclear routing

## LangGraph Workflow

The multi-agent system uses LangGraph to orchestrate the workflow:

```
User Query
    ↓
Orchestrator Node (routes query)
    ↓
    ├─→ Billing Agent → END
    ├─→ Technical Agent → END
    ├─→ Policy Agent → END
    └─→ General Agent → END
```

### State Schema

```python
class AgentState(TypedDict):
    message: str
    history: List[Dict[str, str]]
    session_id: Optional[str]
    agent_name: str
    response: str
```

## API Changes

### Chat Endpoint

The `/api/chat` endpoint now supports multi-agent routing:

**Request:**
```json
POST /api/chat?use_multi_agent=true
{
  "message": "What are your pricing plans?",
  "history": []
}
```

**Response:**
```json
{
  "message": "Our pricing plans include...",
  "status": "success",
  "agent_name": "BILLING_AGENT"
}
```

### Query Parameters

- `use_multi_agent` (boolean, default: `true`): Enable/disable multi-agent routing

## Configuration

### Environment Variables

Add to `backend/.env`:

```bash
# AWS Bedrock (optional, for orchestrator)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

**Note**: AWS Bedrock is optional. If not configured, the orchestrator will use OpenAI GPT-3.5-turbo.

## Dependencies

New dependencies added to `requirements.txt`:

```
langgraph==0.2.40
langchain-aws==0.1.0
boto3==1.35.0
```

## Installation

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Enable Multi-Agent System

The multi-agent system is enabled by default. To disable:

```python
# In API call
POST /api/chat?use_multi_agent=false
```

### Testing Agents

**Billing Agent:**
```
"What are your pricing plans?"
"How do I pay for my subscription?"
"What are the fees?"
```

**Technical Agent:**
```
"How do I use the API?"
"How do I troubleshoot connection issues?"
"What features are available?"
```

**Policy Agent:**
```
"What is your privacy policy?"
"What are the terms of service?"
"What are your compliance requirements?"
```

**General Agent:**
```
"What's the current Tesla stock price?"
"Hello, how are you?"
```

## Fallback Behavior

The system includes multiple fallback mechanisms:

1. **LangGraph unavailable**: Falls back to simple routing without LangGraph
2. **AWS Bedrock unavailable**: Orchestrator uses OpenAI
3. **ChromaDB unavailable**: Agents work without RAG (using general knowledge)
4. **Agent error**: Falls back to General Agent

## Performance Considerations

- **Billing Agent**: Uses caching for faster subsequent responses
- **Technical Agent**: Always fresh retrieval (no caching)
- **Policy Agent**: Pre-loaded context (fastest, no retrieval)
- **Orchestrator**: Uses lightweight model (Claude 3 Haiku) for cost efficiency

## Future Enhancements

- [ ] Session persistence across restarts
- [ ] Agent performance metrics
- [ ] Custom routing rules
- [ ] Multi-language support
- [ ] Agent handoff capabilities
- [ ] Streaming responses for all agents

## Files Created

- `backend/utils/orchestrator.py` - Orchestrator agent
- `backend/utils/billing_agent.py` - Billing support agent
- `backend/utils/technical_agent.py` - Technical support agent
- `backend/utils/policy_agent.py` - Policy & compliance agent
- `backend/utils/multi_agent_system.py` - LangGraph workflow
- `backend/core/config.py` - Updated with AWS Bedrock config
- `backend/api/chat.py` - Updated to use multi-agent system
- `backend/models/chat.py` - Updated response model with agent_name

## Status

✅ **Step 6 Complete**: Multi-Agent System implemented and integrated

All implementation steps (1-6) are now complete!

