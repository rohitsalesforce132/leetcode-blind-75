# Chapter 3: Context Engineering

> **Interview questions:** "What is context engineering?" / "How do you manage prompt context for agents?" / "How do you handle long conversations?"

---

## 1. What Is Context Engineering?

**Analogy:** Imagine you're a consultant giving a client presentation. You wouldn't walk in and dump 10,000 pages of raw data on the table. You'd curate the MOST relevant information, structure it clearly, and present only what helps the client make decisions.

**Context engineering is the discipline of deciding what goes into the LLM's context window and how it's structured.** It's the successor to "prompt engineering" — more systematic and engineering-focused.

```
PROMPT ENGINEERING:
  "Write a clever system prompt that makes the LLM behave well."
  Focus: word choice, tone, instructions.

CONTEXT ENGINEERING:
  "Design the entire information pipeline that feeds the LLM."
  Focus: what information to include, what to exclude, how to structure it,
         how to manage token budget, how to handle long conversations.
```

### Why Context Engineering Matters

```
┌───────────────────────────────────────────────────────┐
│  The context window is FINITE and EXPENSIVE.          │
│                                                       │
│  GPT-4o: 128K tokens (~100K words, ~300 pages)        │
│  Cost: $2.50 per 1M input tokens                      │
│                                                       │
│  If you stuff 100K tokens of context per request:     │
│    100K tokens × $2.50/1M = $0.25 PER REQUEST         │
│    1M requests/day = $250,000/DAY                    │
│                                                       │
│  BAD context engineering = burning money              │
│  GOOD context engineering = 10× cheaper, better quality│
└───────────────────────────────────────────────────────┘
```

---

## 2. The Context Budget

Every LLM call has a token budget. You must allocate it wisely.

```
TOTAL CONTEXT WINDOW (e.g., 128K tokens)
│
├── System Prompt ──────────────── 2-5K tokens (2-4%)
│   "You are a helpful assistant..."
│
├── Tool Definitions ───────────── 1-3K tokens (1-2%)
│   JSON schemas for each available tool
│
├── Retrieved Context (RAG) ────── 10-50K tokens (10-40%)
│   Documents, search results, database records
│
├── Conversation History ───────── 10-50K tokens (10-40%)
│   Previous messages in the conversation
│
├── Current User Message ───────── 0.1-2K tokens (<1%)
│   "What were our Q3 revenue numbers?"
│
└── OUTPUT SPACE ───────────────── 2-8K tokens (2-6%)
    Reserved for the LLM's response

    REMAINING (headroom) ───────── Should be left empty
    Don't max out the window. Leave room for the model to think.
```

### Budget Allocation Strategy

```python
# Context budget calculator
class ContextBudget:
    def __init__(self, model="gpt-4o"):
        self.limits = {
            "gpt-4o": 128_000,
            "claude-3.5-sonnet": 200_000,
            "gpt-4o-mini": 128_000,
        }
        self.max_tokens = self.limits.get(model, 128_000)

    def calculate_budget(self, conversation_length="short"):
        """Allocate token budget across components."""
        output_reserve = 4_000  # Reserve for LLM output

        available = self.max_tokens - output_reserve

        # Allocate based on conversation maturity
        if conversation_length == "short":  # < 5 messages
            return {
                "system_prompt": 2_000,
                "tool_defs": 1_500,
                "rag_context": min(50_000, available * 0.50),
                "history": min(20_000, available * 0.20),
                "user_message": 2_000,
            }
        elif conversation_length == "medium":  # 5-20 messages
            return {
                "system_prompt": 2_000,
                "tool_defs": 1_500,
                "rag_context": min(30_000, available * 0.30),
                "history": min(50_000, available * 0.50),
                "user_message": 2_000,
            }
        else:  # long conversation, 20+ messages → must compress
            return {
                "system_prompt": 2_000,
                "tool_defs": 1_500,
                "rag_context": min(20_000, available * 0.20),
                "history": min(60_000, available * 0.60),
                "user_message": 2_000,
            }
```

---

## 3. Managing Conversation History

### The Problem: Conversations Grow Forever

```
Message 1:   User asks question (100 tokens)
Message 2:   LLM answers (200 tokens)
Message 3:   User follows up (150 tokens)
...
Message 100: Context is now 50K tokens → expensive + slow + hits context limit
```

### Strategy 1: Sliding Window (Simplest)

```
Keep only the LAST N messages. Drop older ones.

[old messages dropped] [msg 95] [msg 96] [msg 97] [msg 98] [msg 99] [msg 100]
                       └──────────── keep last 5 ────────────┘

Pros: Simple, predictable cost.
Cons: Loses early context. If user references something from message 5, it's gone.
```

### Strategy 2: Summarization (Best Quality)

```
Compress old messages into a SUMMARY. Keep recent messages verbatim.

[SUMMARY: "User discussed Q3 revenue ($12M, up 15% YoY). Asked about API costs. Wants to compare GPT-4o vs Llama 3.1 pricing."]
[msg 97] [msg 98] [msg 99] [msg 100]

How:
  When history exceeds threshold:
    1. Take messages 1 through N-5
    2. Send them to a CHEAP model (GPT-4o-mini) to summarize
    3. Replace those messages with the summary
    4. Keep last 5 messages verbatim

Result: Full context in 500 tokens instead of 50K tokens.
```

```python
class ConversationManager:
    """Manages conversation context with summarization."""

    def __init__(self, max_history_tokens=50_000, keep_recent=6):
        self.messages = []
        self.summary = ""
        self.max_history_tokens = max_history_tokens
        self.keep_recent = keep_recent

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

        # Check if we need to compress
        if self._estimate_tokens() > self.max_history_tokens:
            self._compress()

    def _compress(self):
        """Summarize old messages, keep recent ones."""
        # Split: old messages to summarize + recent to keep
        to_summarize = self.messages[:-self.keep_recent]
        to_keep = self.messages[-self.keep_recent:]

        # Summarize old messages using a cheap model
        summary_prompt = f"Summarize this conversation concisely, keeping key facts:\n"
        for msg in to_summarize:
            summary_prompt += f"{msg['role']}: {msg['content']}\n"

        self.summary = call_llm(
            model="gpt-4o-mini",  # CHEAP model for summarization
            messages=[{"role": "user", "content": summary_prompt}]
        )

        # Rebuild: summary + recent messages
        self.messages = []
        if self.summary:
            self.messages.append({
                "role": "system",
                "content": f"Previous conversation summary:\n{self.summary}"
            })
        self.messages.extend(to_keep)

    def get_context(self):
        """Get the messages to send to the LLM."""
        return self.messages

    def _estimate_tokens(self):
        """Rough estimate: 1 token ≈ 4 chars."""
        total_chars = sum(len(m["content"]) for m in self.messages)
        return total_chars // 4
```

### Strategy 3: Hybrid (Best of Both)

```
┌──────────────────────────────────────────────────┐
│            CONVERSATION MEMORY                    │
│                                                  │
│  ┌──────────────────────┐                        │
│  │ Summary (500 tokens) │  ← Compressed old msgs │
│  │ "User is analyzing   │                        │
│  │  Q3 revenue..."      │                        │
│  └──────────────────────┘                        │
│                                                  │
│  ┌──────────────────────┐                        │
│  │ Recent Messages      │  ← Last 6-10 messages │
│  │ (5K tokens)          │                        │
│  └──────────────────────┘                        │
│                                                  │
│  ┌──────────────────────┐                        │
│  │ RAG Retrieved Docs   │  ← For current question│
│  │ (10K tokens)         │                        │
│  └──────────────────────┘                        │
│                                                  │
│  ┌──────────────────────┐                        │
│  │ System Prompt        │  ← Role, rules, tools  │
│  │ (2K tokens)          │                        │
│  └──────────────────────┘                        │
│                                                  │
│  TOTAL: ~18K tokens (not 100K!)                  │
└──────────────────────────────────────────────────┘
```

---

## 4. RAG Context — Quality Over Quantity

### The RAG Context Pipeline

```
User asks: "What was our Q3 revenue?"
    │
    ▼
┌──────────────────┐
│ STEP 1: RETRIEVE │  Search knowledge base for relevant documents
│                  │  Vector search + keyword search (hybrid)
│                  │  Get top 20 candidate documents
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ STEP 2: RERANK   │  Score and reorder by actual relevance
│                  │  Use a cross-encoder model to score each doc
│                  │  Keep top 5 (drop the other 15)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ STEP 3: COMPRESS │  Extract only the relevant parts of each doc
│                  │  Remove headers, footers, boilerplate
│                  │  Extract the 2-3 paragraphs that answer the question
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ STEP 4: FORMAT   │  Structure the context for the LLM
│                  │
│                  │  Context:
│                  │  [Source 1: Q3 Financial Report]
│                  │  Total revenue: $12.4M (up 15% YoY)...
│                  │
│                  │  [Source 2: Board Meeting Notes]
│                  │  Q3 saw strong growth driven by...
└──────────────────┘
```

### Why Not Just Dump Everything?

```
BAD (dump 20 documents, 50K tokens):
  "Here's 20 documents. Find the answer yourself."
  → LLM gets confused. Lost in the middle. Costs $0.12/request.

GOOD (5 curated, reranked, compressed docs, 8K tokens):
  "Here are the 5 most relevant passages. [clearly formatted]"
  → LLM answers accurately. Costs $0.02/request. 6× cheaper.
```

---

## 5. System Prompt Engineering

### The Anatomy of a Great System Prompt

```
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM PROMPT ANATOMY                                       │
│                                                             │
│ 1. ROLE                                                     │
│    "You are an expert financial analyst assistant for       │
│     AT&T. You help employees query internal data."          │
│                                                             │
│ 2. CAPABILITIES                                             │
│    "You have access to these tools:                         │
│     - query_revenue_db: Search financial records            │
│     - search_docs: Search internal documentation            │
│     - send_email: Send an email on behalf of the user"      │
│                                                             │
│ 3. RULES / CONSTRAINTS                                      │
│    "RULES:                                                  │
│     1. ALWAYS use tools to get real data. Never guess.      │
│     2. If you don't know, say 'I need to look that up.'     │
│     3. Never make up numbers. Every number must come from   │
│        a tool result.                                       │
│     4. Maximum 3 tool calls per question.                   │
│     5. If asked about competitors, decline politely."       │
│                                                             │
│ 4. OUTPUT FORMAT                                            │
│    "Format your answer as:                                  │
│     - Direct answer first (1 sentence)                      │
│     - Supporting details below                              │
│     - Source citation: [From: tool_name]"                   │
│                                                             │
│ 5. EXAMPLES (Few-shot)                                      │
│    "Example interaction:                                    │
│     User: 'What was Q2 revenue?'                            │
│     You: [calls query_revenue_db('Q2 revenue')]             │
│          'Q2 revenue was $11.2M. [Source: revenue_db]'"     │
│                                                             │
│ 6. CURRENT CONTEXT                                          │
│    "Current date: 2024-07-24. User: Rohit (DevOps Lead)."   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Few-Shot Prompting vs Zero-Shot

```
ZERO-SHOT (no examples):
  System: "Classify this email as urgent, normal, or low priority."
  User: "The server is down! Production is offline!"
  → Works for simple tasks. LLM figures it out from instructions alone.

FEW-SHOT (with examples):
  System: "Classify email priority. Examples:
    Email: 'Server down, production offline' → URGENT
    Email: 'Please review this PR when you have time' → NORMAL
    Email: 'Weekly newsletter subscription' → LOW
    Email: 'The dashboard is showing old data' → URGENT  ← edge case example
    Email: 'Update your profile photo' → LOW"
  User: "Need help with password reset"
  → Better for tasks with edge cases or specific classification criteria.
```

### When to Use Few-Shot

```
Use few-shot when:
  - Task has specific formatting requirements
  - Edge cases need to be demonstrated
  - Accuracy is critical (>95% needed)
  - Classification with custom categories

Use zero-shot when:
  - Task is straightforward
  - Model is already good at this (GPT-4o is smart)
  - Token budget is tight
```

---

## ular 7. Structured Output (JSON Mode)

### Why Structured Output Matters

```
UNSTRUCTURED (bad for agents):
  LLM: "Sure! The weather in Mumbai is 32°C. Have a great day!"
  → Your code must parse this natural language. Fragile.

STRUCTURED (JSON):
  LLM: {
    "city": "Mumbai",
    "temperature": 32,
    "unit": "celsius",
    "summary": "Sunny and warm"
  }
  → Your code parses JSON directly. Reliable. Programmable.
```

### How to Enforce Structured Output

```python
# OpenAI approach: response_format with JSON schema
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "weather_response",
            "schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "temperature": {"type": "number"},
                    "conditions": {"type": "string"}
                },
                "required": ["city", "temperature", "conditions"]
            }
        }
    }
)
# Response is GUARANTEED to be valid JSON matching the schema.
```

```python
# Pydantic approach (for open-source / local models)
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    conditions: str

# Use with instructor library or LangChain
response = client.chat.completions.create(
    model="gpt-4o",
    response_model=WeatherResponse,  # Pydantic enforces the schema
    messages=[...]
)
# response is a validated WeatherResponse object
```

---

## 8. Advanced: Prompt Chaining

### What Is Prompt Chaining?

Instead of one massive prompt, break the task into multiple LLM calls, each specialized:

```
SINGLE PROMPT (hard to get right):
  "Read this 100-page contract, identify risks, summarize key terms,
   compare to standard contract template, and generate a risk report."
  → LLM struggles with everything at once. Quality drops.

PROMPT CHAINING (specialized stages):
  Stage 1 LLM: "Extract key terms from this contract" → structured output
  Stage 2 LLM: "Given these terms, identify risks" → risk list
  Stage 3 LLM: "Compare these risks to standard template" → comparison
  Stage 4 LLM: "Generate a risk report from this analysis" → final report

  Each stage is simpler → higher quality at each step → better final result.
```

### When to Chain vs Single Call

```
Use CHAINING when:
  - Task has multiple distinct steps
  - Each step needs different instructions
  - You want to validate/correct between steps
  - Quality > cost (chaining costs more)

Use SINGLE CALL when:
  - Task is simple and well-defined
  - Latency matters (one call is faster)
  - Cost matters (one call is cheaper)
```

---

## Interview Q&A

**Q: "What is context engineering and how is it different from prompt engineering?"**
A: Context engineering is the systematic design of everything that goes into the LLM's context window — not just the system prompt, but the retrieved documents, conversation history, tool definitions, and output format. Prompt engineering focuses on wording the instructions well. Context engineering manages the entire information budget: deciding what to include, what to summarize, what to drop, and how to structure it for maximum LLM performance at minimum cost.

**Q: "How do you handle long conversations that exceed the context window?"**
A: I use a hybrid strategy: (1) Summarization — when history exceeds a threshold, I send old messages to a cheap model to summarize, then replace them with the summary. (2) Sliding window — I always keep the most recent 6-10 messages verbatim for immediate context. (3) RAG — I store key facts from the conversation in a vector database and retrieve them on demand if the user references old topics. This keeps context under 20K tokens even for conversations spanning thousands of messages.

**Q: "How do you structure RAG context for best results?"**
A: Quality over quantity. I retrieve 20 candidate documents, then use a cross-encoder to rerank by actual relevance, keeping only the top 3-5. I compress each document to extract only relevant paragraphs. I format them clearly with source citations. I also add a system instruction: "Answer based ONLY on the provided context. If the context doesn't contain the answer, say you don't know." This grounds the model and reduces hallucinations.

**Q: "When do you use few-shot vs zero-shot?"**
A: Zero-shot for straightforward tasks where the model already has strong capabilities — GPT-4o doesn't need examples to summarize text. Few-shot for tasks with custom categories, specific formatting requirements, or tricky edge cases. For example, classifying incidents by severity needs few-shot because the severity criteria are domain-specific. I always include 1-2 edge-case examples in few-shot to calibrate the model.

**Q: "How do you minimize token costs?"**
A: Four strategies: (1) Summarize old conversation history with a cheap model. (2) Rerank RAG results and keep only top 3-5 documents instead of 20. (3) Use GPT-4o-mini for simple steps in a chain, reserve GPT-4o for complex reasoning. (4) Cache tool results and common queries — if 1000 users ask the same question, retrieve the answer from cache instead of re-running the LLM.
