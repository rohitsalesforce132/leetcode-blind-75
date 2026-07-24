# System Design — From Zero to Expert

> **Goal:** Master system design interviews — from fundamental concepts to designing AI-powered systems at scale.

## How to Use This Guide

1. Start with **Fundamentals** (Tier 1) — learn the building blocks
2. Move to **Classic Problems** (Tier 2) — practice the standard interview questions
3. Master **AI Problems** (Tier 3) — the cutting edge that sets you apart

## Tier 1: Fundamentals

| # | Topic | File |
|---|-------|------|
| 1 | Scaling Basics (1 → millions of users) | [01-scaling-basics.md](01-fundamentals/01-scaling-basics.md) |
| 2 | Databases & Caching | [02-databases-and-caching.md](01-fundamentals/02-databases-and-caching.md) |
| 3 | Microservices & APIs | [03-microservices-and-apis.md](01-fundamentals/03-microservices-and-apis.md) |
| 4 | Reliability & Monitoring | [04-reliability-and-monitoring.md](01-fundamentals/04-reliability-and-monitoring.md) |
| 5 | Messaging & Streaming | [05-messaging-and-streaming.md](01-fundamentals/05-messaging-and-streaming.md) |

## Tier 2: Classic Problems

| # | Problem | File |
|---|---------|------|
| 1 | URL Shortener (bit.ly) | [01-url-shortener.md](02-classic-problems/01-url-shortener.md) |
| 2 | Rate Limiter | [02-rate-limiter.md](02-classic-problems/02-rate-limiter.md) |
| 3 | Twitter/X News Feed | [03-twitter-news-feed.md](02-classic-problems/03-twitter-news-feed.md) |
| 4 | WhatsApp Chat | [04-whatsapp-chat.md](02-classic-problems/04-whatsapp-chat.md) |
| 5 | Video Streaming (Netflix) | [05-video-streaming.md](02-classic-problems/05-video-streaming.md) |

## Tier 3: AI Systems

| # | Problem | File |
|---|---------|------|
| 1 | AI Chatbot / LLM Service | [01-ai-chatbot-llm-service.md](03-ai-problems/01-ai-chatbot-llm-service.md) |
| 2 | RAG System | [02-rag-system.md](03-ai-problems/02-rag-system.md) |
| 3 | Recommendation Engine | [03-recommendation-engine.md](03-ai-problems/03-recommendation-engine.md) |
| 4 | Real-time AI Search | [04-realtime-ai-search.md](03-ai-problems/04-realtime-ai-search.md) |
| 5 | AI Content Moderation | [05-ai-content-moderation.md](03-ai-problems/05-ai-content-moderation.md) |

## The System Design Interview Framework

Every problem follows this 6-step framework:

```
1. CLARIFY REQUIREMENTS (5 min)
   ├── Functional: What must the system DO?
   └── Non-functional: Scale, latency, availability, consistency

2. BACK-OF-ENVELOPE ESTIMATION (3 min)
   ├── Users, requests/sec, storage, bandwidth, memory
   └── Shows you can think about scale

3. HIGH-LEVEL DESIGN (10 min)
   ├── Draw boxes and arrows (Client → LB → API → DB → Cache)
   └── Get interviewer agreement before diving deeper

4. DEEP DIVE (15 min)
   ├── Pick the hardest part and design it in detail
   └── Data model, algorithms, specific technologies

5. BOTTLENECKS & SCALING (5 min)
   ├── Single points of failure, SPOF
   ├── Sharding, replication, caching
   └── Tradeoffs (CAP theorem)

6. WRAP UP (2 min)
   ├── Summarize the architecture
   └── Mention monitoring, alerting, disaster recovery
```

---

> Start at Tier 1. Each tier builds on the previous. By Tier 3, you'll be
> designing AI systems that most candidates can't.
