# Chapter 7: Sample FDE Projects to Woo Interviewers

> **Goal:** Have 3 concrete projects you can discuss in depth. Each demonstrates a different AI engineering skill.

---

## Project 1: `IntelligentRAG` — Production RAG System for Enterprise Knowledge Base

### What to Build
A RAG system that answers questions from a company's internal documents (PDFs, wikis, Notion, Confluence). Include document chunking, embedding, vector search, reranking, and citation. Build a web UI.

### What It Demonstrates
- Context engineering (chunking strategies, context budget management)
- Vector databases and embedding models
- Hybrid search (semantic + keyword)
- Hallucination reduction
- Production system design

### Architecture
```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ Web UI   │ ──> │ API Server   │ ──> │ Query        │
│ (React)  │     │ (FastAPI)    │     │ Processor    │
└──────────┘     └──────────────┘     └──────┬───────┘
                                            │
                     ┌──────────────────────┼──────────────────┐
                     │                      │                  │
                     ▼                      ▼                  ▼
              ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
              │ Embedding    │    │ Vector DB    │    │ Reranker     │
              │ Model        │    │ (Qdrant)     │    │ (Cross-Enc)  │
              │ (BGE-large)  │    │              │    │              │
              └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                │
                     ┌──────────────────────────────────────────┘
                     │
                     ▼
              ┌──────────────┐    ┌──────────────┐
              │ LLM          │    │ Response     │
              │ (GPT-4o /    │ ── │ with         │
              │  Llama 3)    │    │ Citations    │
              └──────────────┘    └──────────────┘
```

### Key Implementation Details to Discuss

```python
# 1. SMART CHUNKING (not just fixed-size)
def chunk_document(text, strategy="semantic"):
    """Split documents intelligently, not just every 500 tokens."""
    if strategy == "semantic":
        # Split by headers, paragraphs, then sentences
        sections = split_by_headers(text)     # ## Introduction
        chunks = []
        for section in sections:
            paragraphs = split_by_paragraphs(section)
            for para in paragraphs:
                if token_count(para) > MAX_CHUNK:
                    # Further split by sentences
                    chunks.extend(split_by_sentences(para, MAX_CHUNK))
                else:
                    chunks.append(para)
        return chunks
    elif strategy == "overlap":
        # Fixed-size with overlap (simpler, less precise)
        return sliding_window(text, size=512, overlap=50)

# 2. HYBRID SEARCH (vector + keyword)
def search(query, top_k=20):
    """Combine semantic and keyword search."""
    # Semantic: find similar meaning
    query_embedding = embed(query)
    semantic_results = vector_db.search(query_embedding, limit=top_k)

    # Keyword: find exact term matches (BM25)
    keyword_results = keyword_index.search(query, limit=top_k)

    # Merge: Reciprocal Rank Fusion
    merged = reciprocal_rank_fusion(semantic_results, keyword_results)
    return merged[:top_k]

# 3. RERANKING (improve precision)
def rerank(query, documents, top_n=5):
    """Use cross-encoder to score actual query-doc relevance."""
    scores = cross_encoder.predict([(query, doc.text) for doc in documents])
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked[:top_n]]

# 4. CITATION EXTRACTION
def generate_answer_with_citations(query, context_docs):
    """Force the LLM to cite sources."""
    prompt = f"""Answer based ONLY on the provided context.
    For every claim, cite the source number.

    Context:
    [1] {context_docs[0].text}
    [2] {context_docs[1].text}
    [3] {context_docs[2].text}

    Format: "Answer text [1]. More text [2, 3]."
    If the context doesn't contain the answer, say "I don't know."

    Question: {query}
    """
    return llm.generate(prompt)
```

### Metrics to Quote in Interview

```
"Our RAG system achieved:
  - 94% answer accuracy (vs 72% without RAG)
  - 2.3s average response time
  - 89% citation accuracy (citations actually support the claim)
  - $0.04 per query (using GPT-4o-mini + local embeddings)
  - Handles 500K documents across 12,000 categories"
```

### Tech Stack
- **Embeddings:** BGE-large-en-v1.5 (local, free) or OpenAI text-embedding-3-small
- **Vector DB:** Qdrant (open-source, fast, good filtering)
- **Reranker:** BGE-reranker-v2-m3 (cross-encoder)
- **LLM:** GPT-4o-mini for chat, GPT-4o for complex queries
- **Framework:** LangChain for orchestration, FastAPI for API
- **UI:** Streamlit (quick demo) or React (production)

---

## Project 2: `AgentForge` — Multi-Tool Agent for Incident Management

### What to Build
An AI agent that investigates incidents by querying multiple systems (logs, metrics, tickets, runbooks), correlates findings, and produces a diagnostic report. Fully agentic with ReAct loop.

### What It Demonstrates
- Agent harness design (ReAct loop, tool dispatch)
- Tool calling with multiple integrations
- Multi-step reasoning
- Human-in-the-loop escalation
- Production error handling

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     AGENT HARNESS                           │
│                                                            │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────┐  │
│  │ THINK    │───>│ ACT      │───>│ OBSERVE   │───>│ LOOP │  │
│  │          │   │          │   │          │   │      │  │
│  │ LLM      │   │ Tool     │   │ Result   │   │ More?│  │
│  │ reasons  │   │ Executor │   │ analysis │   │      │  │
│  └──────────┘   └────┬─────┘   └──────────┘   └──────┘  │
│                      │                                     │
│                      ▼                                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │                 TOOL REGISTRY                       │  │
│  │                                                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │  │
│  │  │ query_   │ │ search_  │ │ get_     │           │  │
│  │  │ logs()   │ │ metrics()│ │ runbook()│           │  │
│  │  └──────────┘ └──────────┘ └──────────┘           │  │
│  │                                                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │  │
│  │  │ query_   │ │ search_  │ │ escalate │           │  │
│  │  │ ticket() │ │ kb()     │ _human()  │           │  │
│  │  └──────────┘ └──────────┘ └──────────┘           │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Implementation Details

```python
class IncidentAgent:
    """Agent that investigates production incidents."""

    SYSTEM_PROMPT = """You are an expert SRE incident investigator.
    When given an incident, follow this process:
    1. Query recent logs for the affected service
    2. Check metrics for anomalies (CPU, memory, error rate)
    3. Search for similar past incidents
    4. Look up the relevant runbook
    5. Summarize findings and suggest remediation

    TOOLS:
    - query_logs(service, time_range): Search application logs
    - search_metrics(service, metric): Query Prometheus metrics
    - query_tickets(search): Search past incident tickets
    - search_kb(query): Search knowledge base
    - get_runbook(service): Get the operational runbook
    - escalate_human(reason): Escalate to human SRE
    """

    def investigate(self, incident_description):
        """Run the agentic loop to investigate."""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Investigate: {incident_description}"}
        ]

        for iteration in range(10):  # Max 10 steps
            response = self.llm.call(messages, tools=self.tool_defs)

            if not response.tool_calls:
                return response.content  # Final report

            messages.append(response)

            for tool_call in response.tool_calls:
                result = self.execute_tool(tool_call)
                messages.append({
                    "role": "tool",
                    "content": result
                })

        return "Investigation timed out. Escalating to human."

    def execute_tool(self, tool_call):
        """Execute with error handling and logging."""
        try:
            result = self.tools[tool_call.name](**tool_call.args)
            self.log(f"{tool_call.name} → {result[:100]}...")
            return result
        except Exception as e:
            return f"Error: {e}. Try a different approach."
```

### Demo Scenario for Interview

```
Input: "Payment service error rate jumped from 0.1% to 15% in the last 10 minutes."

Agent's investigation:
  Step 1: query_logs("payment-service", "last 10 minutes")
    → Found 500 errors: "Connection refused to DB at 10.2.3.4:5432"

  Step 2: search_metrics("payment-service", "db_connections")
    → DB connection pool exhausted (100/100 connections used)

  Step 3: query_tickets("payment DB connection")
    → Found similar incident INC-2024-0156 (3 weeks ago)
    → Root cause: connection leak in v2.3.1

  Step 4: get_runbook("payment-service")
    → "If DB connections exhausted: restart connection pooler"

  Step 5: FINAL REPORT:
    "Root Cause: Database connection pool exhaustion.
     The payment service has maxed out 100 DB connections.
     Logs show 'Connection refused' errors.

     Similar to INC-2024-0156 (possible regression in v2.3.4).

     Recommended Action:
     1. Immediate: Restart the connection pooler (pgbouncer)
     2. Short-term: Check v2.3.4 for connection leak
     3. Preventive: Add connection monitoring alert at 80%

     [Escalation: Needs DBA approval to restart pooler]"
```

---

## Project 3: `ModelGateway` — Multi-Model Router with Cost Optimization

### What to Build
A gateway that sits between your application and multiple LLM providers (OpenAI, Anthropic, local Llama). It routes requests to the cheapest model that can handle the task, with automatic fallback.

### What It Demonstrates
- Multi-model strategy (not lock-in to one provider)
- Cost optimization (route simple → cheap model, complex → strong model)
- Production reliability (fallback, retries, rate limiting)
- Monitoring and observability
- Understanding of model tradeoffs

### Architecture
```
┌──────────┐                                ┌──────────────┐
│ Your App │ ── "Summarize this email" ──> │ ModelGateway  │
└──────────┘                                │               │
                                            │ ┌───────────┐ │
                                            │ │ ROUTER     │ │ Classify
                                            │ │            │ │ complexity
                                            │ │ Simple?    │ │
                                            │ │ → Mini     │ │
                                            │ │ Complex?   │ │
                                            │ │ → GPT-4o   │ │
                                            │ └─────┬─────┘ │
                                            └───────┼───────┘
                                                    │
                    ┌───────────────────────────────┼───────────────────┐
                    │                               │                   │
                    ▼                               ▼                   ▼
             ┌──────────┐                  ┌──────────┐         ┌──────────┐
             │ GPT-4o   │                  │ GPT-4o   │         │ Llama 3  │
             │ Mini     │                  │ (full)   │         │ (local)  │
             │ $0.15/M  │                  │ $2.50/M  │         │ ~$0.50/M │
             └──────────┘                  └──────────┘         └──────────┘
                    │                               │                   │
                    └───────────────────────────────┼───────────────────┘
                                                    │
                                            ┌───────▼───────┐
                                            │ Response       │
                                            │ + Cost tracking│
                                            └───────────────┘
```

### Key Implementation: Complexity Router

```python
class ModelRouter:
    """Routes requests to the cheapest capable model."""

    def route(self, messages, task_type="auto"):
        """Decide which model to use based on request complexity."""
        if task_type == "auto":
            task_type = self.classify_complexity(messages)

        routing = {
            "simple": {"model": "gpt-4o-mini", "reason": "Simple task, save cost"},
            "medium": {"model": "gpt-4o", "reason": "Needs reasoning"},
            "complex": {"model": "claude-3.5-sonnet", "reason": "Needs deep reasoning"},
            "code": {"model": "gpt-4o", "reason": "Best code generation"},
            "long_context": {"model": "gemini-1.5-pro", "reason": "1M token context"},
        }

        return routing.get(task_type, routing["medium"])

    def classify_complexity(self, messages):
        """Quick classification using a cheap model."""
        last_msg = messages[-1]["content"]

        # Heuristic rules (free)
        if len(last_msg) < 100 and "?" in last_msg:
            return "simple"  # Short question
        if "code" in last_msg.lower() or "function" in last_msg.lower():
            return "code"
        if any(word in last_msg.lower() for word in ["analyze", "compare", "design"]):
            return "complex"
        if sum(len(m["content"]) for m in messages) > 50_000:
            return "long_context"

        return "medium"

    def call_with_fallback(self, messages):
        """Call primary model, fallback to alternatives on failure."""
        primary = self.route(messages)

        fallback_chain = [primary["model"], "gpt-4o", "gpt-4o-mini"]

        for model in fallback_chain:
            try:
                response = self.call_model(model, messages)
                self.log_cost(model, response)
                return response
            except (RateLimitError, ServiceUnavailableError):
                continue  # Try next model

        raise AllModelsFailedError("All models in fallback chain failed")
```

### Metrics to Quote

```
"ModelGateway reduced LLM costs by 73% while maintaining quality:
  - 60% of requests → GPT-4o-mini (avg cost: $0.001/request)
  - 30% of requests → GPT-4o (avg cost: $0.01/request)
  - 10% of requests → Claude 3.5 Sonnet (complex reasoning)
  - Average cost per request: $0.004 (vs $0.015 with GPT-4o-only)
  - 99.95% uptime with automatic fallback"
```

---

## How to Present These Projects in an Interview

### The 60-Second Pitch (for each project)

```
"I built [PROJECT NAME] to solve [PROBLEM].

The key challenge was [TECHNICAL CHALLENGE].

I solved it by [YOUR APPROACH], using [KEY TECHNOLOGIES].

The result was [QUANTIFIED OUTCOME].

For example, [SPECIFIC ANECDOTE showing depth]."
```

### Example Pitch: IntelligentRAG

"I built IntelligentRAG to let AT&T employees get instant answers from internal documentation. The key challenge was that naive RAG retrieved too many irrelevant documents — we got 72% accuracy. I solved this by implementing a three-stage pipeline: hybrid search combining vector and keyword retrieval, cross-encoder reranking to filter to top 5, and smart chunking that respects document structure. Using Qdrant for vectors, BGE embeddings, and GPT-4o-mini for generation, we achieved 94% accuracy at $0.04 per query. One interesting insight: chunking by markdown headers instead of fixed-size windows improved accuracy by 8% because it kept related information together."
