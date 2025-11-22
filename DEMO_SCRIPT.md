# TradePal AI - YouTube Demo Script

**Target Length:** 5-7 minutes  
**Tone:** Confident, conversational, engaging

---

## [0:00 - 0:25] HOOK & INTRODUCTION

Hey everyone, I'm Muhammad. I built TradePal AI—a multi-agent system where specialized agents handle different types of questions, orchestrated using LangGraph. Each agent is an expert in its domain.

---

## [0:25 - 2:30] VISUAL DEMO - BILLING AGENT (Hybrid RAG/CAG)

**[Type and send: "What are typical trading platform fees at brokerages?"]**

**[Point to screen as response streams]** The orchestrator routes this to the Billing Agent. Watch—it's hitting ChromaDB, our vector store, pulling relevant fee information. That's RAG search happening right now.

**[Wait for response to complete]**

**[Type and send: "What payment methods do brokerages accept for deposits?"]**

**[Point to screen]** Notice how fast this is? It's not hitting the database again—it's pulling from cached context from the first query. That's Hybrid RAG/CAG: first query does RAG search and caches the context, subsequent billing questions reuse that cache. Faster, cheaper, and makes sense because billing questions reference the same policies repeatedly.

---

## [2:30 - 3:15] VISUAL DEMO - TECHNICAL AGENT (Pure RAG)

**[Type and send: "How do I use TradePal's educational features to analyze trading patterns?"]**

**[Point to screen]** This routes to Technical Support Agent. See it pulling from technical documentation? Pure RAG—every query hits the vector database, always fresh retrieval, no caching. Technical docs change constantly—bug reports get updated, forum posts get new answers—so we want the most current information every single time. Trade-off is speed versus accuracy, and for technical support, accuracy wins.

---

## [3:15 - 3:45] VISUAL DEMO - POLICY AGENT (Pure CAG)

**[Type and send: "What is the PDT rule?"]**

**[Point to screen]** Policy Agent—instant response. Pure CAG: pre-loaded static documents, no vector search, no retrieval calls. SEC/FINRA regulations don't change mid-conversation, so why pay for vector search when we can load the context once at startup? Pure cost optimization.

**[Show chat interface]** You're typing into one chat box. The orchestrator and LangGraph handle routing automatically—you never pick an agent manually. Everyone shares ChromaDB, but each agent uses it differently based on its domain.

---

## [3:45 - 4:45] FRONTEND FEATURES

**[Click on Settings in navigation]**

Settings page—API key management. Keys are encrypted client-side using Web Crypto API, stored in browser localStorage. They never touch my servers. Security-first approach.

**[Click on Market in navigation]**

Market page—real-time stock data for SPY and TSLA. Options chains, market overview, event studies. All pulling from the backend API.

**[Click back to Standard Chat, show Documents button]**

Document upload—upload PDFs, they get processed and stored in ChromaDB. The agents can then reference them in responses. That's how RAG works—vector search over your documents.

**[Point to Crisis Support button]**

Crisis Support button—always accessible. National Suicide Prevention Lifeline and Crisis Text Line. This domain touches on trading psychology, and I want to acknowledge that trading doesn't always work out—that's understandable, it's part of the process. If you find yourself struggling or need support, these resources are here. This is a technical project demonstrating AI architecture, not a tool for trading decisions.

---

## [4:45 - 5:00] CLOSING

That's TradePal AI—multi-agent system with LangGraph, different retrieval strategies, cost optimization. Code is on GitHub, fully documented. I'd love to hear your thoughts. If you found this useful, drop a comment, hit subscribe.

I'm Muhammad, thanks for watching.

---

## NOTES FOR DELIVERY

- Speak naturally, not reading word-for-word
- Point to screen when showing responses
- Wait for responses to complete before explaining
- Each agent demo is complete before moving to next
- Frontend features: click through navigation, show each page briefly
- When discussing trading psychology/gambling, keep tone natural and caring, not abrupt
- End with confidence and energy
