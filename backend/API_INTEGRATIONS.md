# API Integrations - TradePal AI

Documentation for external API integrations used in the TradePal AI backend.

## Overview

The backend integrates with multiple external APIs to provide stock market data, sentiment analysis, and AI capabilities. This document describes each integration, its configuration, and usage patterns.

## OpenAI API

### Purpose
Primary LLM provider for agent responses and general AI capabilities.

### Configuration
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Usage
- General agent responses
- Agent routing (fallback when AWS Bedrock unavailable)
- Embedding generation for ChromaDB
- Text processing and generation

### Rate Limits
- Standard tier: 3,500 RPM, 10,000 TPM
- Monitor usage in OpenAI dashboard

### Error Handling
- Automatic retry logic implemented
- Fallback to alternative models if available
- Graceful degradation on rate limit errors

## Alpha Vantage API

### Purpose
Primary source for stock market data including quotes, historical prices, and market overview.

### Configuration
```bash
ALPHA_VANTAGE_API_KEY=your-key-here
```

### Endpoints Used
- `GLOBAL_QUOTE` - Current stock quotes
- `TIME_SERIES_DAILY` - Historical daily prices
- `NEWS_SENTIMENT` - News sentiment analysis

### Rate Limits
- Free tier: 5 API calls per minute, 500 per day
- Premium tier: Higher limits available

### Fallback Strategy
If Alpha Vantage is unavailable or rate limited, the system automatically falls back to yfinance library.

### Error Handling
- Rate limit detection and handling
- Automatic fallback to yfinance
- Clear error messages for users

## AWS Bedrock

### Purpose
Cost-effective routing decisions for the orchestrator agent using Claude 3 Haiku.

### Configuration
```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

### Usage
- Orchestrator agent query classification
- Fast, low-cost routing decisions
- Optional - falls back to OpenAI if not configured

### Cost Optimization
- Uses lightweight model (Haiku) for routing
- Lower cost compared to GPT-4 for classification
- Only used for routing, not response generation

### Error Handling
- Automatic fallback to OpenAI if Bedrock unavailable
- Region-specific error handling
- Credential validation

## yfinance Library

### Purpose
Fallback and primary source for stock data when Alpha Vantage unavailable.

### Configuration
No API key required - uses public Yahoo Finance data.

### Usage
- Stock quotes
- Historical price data
- Options chain data
- Market overview

### Limitations
- Rate limiting may apply
- Data availability depends on Yahoo Finance
- Less reliable than paid APIs

### Error Handling
- JSON parsing error handling
- Network error retry logic
- Graceful degradation

## Reddit API

### Purpose
Sentiment analysis from Reddit WallStreetBets posts.

### Configuration
Uses public Reddit API (no authentication required for basic access).

### Usage
- Sentiment analysis for stocks
- Social media sentiment correlation
- Market sentiment indicators

### Rate Limits
- Public API: 60 requests per minute
- Consider authentication for higher limits

### Error Handling
- Rate limit detection
- Fallback to news-only sentiment
- Error logging for debugging

## Integration Patterns

### Retry Logic
All API integrations implement retry logic:
- Exponential backoff
- Maximum retry attempts
- Timeout handling

### Caching Strategy
- Stock quotes cached for short duration
- Sentiment data cached per symbol
- Agent responses not cached (fresh responses)

### Error Propagation
- User-friendly error messages
- Detailed logging for debugging
- Fallback mechanisms where possible

## Best Practices

### API Key Management
- Never commit API keys to repository
- Use environment variables
- Rotate keys regularly
- Monitor usage and costs

### Rate Limit Handling
- Implement exponential backoff
- Monitor rate limit headers
- Queue requests when necessary
- Use caching to reduce API calls

### Cost Optimization
- Use appropriate models for tasks
- Cache responses when possible
- Monitor usage dashboards
- Set up billing alerts

## Monitoring

### Metrics to Track
- API call counts per service
- Error rates
- Response times
- Rate limit hits
- Cost per request

### Logging
All API calls are logged with:
- Timestamp
- Endpoint called
- Response status
- Error details (if any)

## Future Enhancements

### Potential Additions
- Additional stock data providers
- Alternative LLM providers
- Enhanced caching strategies
- Webhook support for real-time updates
- API usage analytics dashboard

## Notes for Production

- Set up API key rotation procedures
- Implement comprehensive monitoring
- Configure rate limit alerts
- Set up cost tracking
- Plan for API deprecations
- Maintain fallback strategies
