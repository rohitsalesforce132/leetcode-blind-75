# Hands-On LLMs — Advanced Generation, RAG & Multimodal (Ch 7-9)

> **Source:** "Hands-On Large Language Models" by Jay Alammar & Maarten Grootendorst (O'Reilly, 2024)
> **Pages:** 598 | **This file covers:** Ch 7 (Advanced Generation & Tools), Ch 8 (Semantic Search & RAG), Ch 9 (Multimodal LLMs)
> **Why these 3 chapters:** They cover the three most in-demand LLM engineering skills — agent frameworks, RAG systems, and multimodal models.

---

## TABLE OF CONTENTS

1. [Chapter 7: Advanced Text Generation Techniques and Tools](#chapter-7)
2. [Chapter 8: Semantic Search and RAG](#chapter-8)
3. [Chapter 9: Multimodal LLMs](#chapter-9)
4. [Cross-Book Comparison: HoLM vs Huyen vs Sinha](#comparison)

---

## Chapter 7: Advanced Text Generation Techniques and Tools

### The LangChain Stack Overview

```
┌──────────────────────────────────────────────────────────────────┐
│              THE LANGCHAIN COMPONENT STACK                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐          │
│  │ AGENTS                                              │          │
│  │ LLM decides what to do + uses external tools       │          │
│  │ (ReAct, tool calling, function calling)            │          │
│  └───────────────────────┬────────────────────────────┘          │
│                          │                                        │
│  ┌───────────────────────▼────────────────────────────┐          │
│  │ MEMORY                                              │          │
│  │ Conversation buffer, windowed, summary              │          │
│  │ (short-term context management)                     │          │
│  └───────────────────────┬────────────────────────────┘          │
│                          │                                        │
│  ┌───────────────────────▼────────────────────────────┐          │
│  │ CHAINS                                              │          │
│  │ Prompt templates → LLM → output parsers            │          │
│  │ (sequential or parallel pipelines)                  │          │
│  └───────────────────────┬────────────────────────────┘          │
│                          │                                        │
│  ┌───────────────────────▼────────────────────────────┐          │
│  │ MODEL I/O                                           │          │
│  │ Load LLM (quantized GGUF, API, local)              │          │
│  │ Generate text, manage tokens                        │          │
│  └────────────────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────────────┘

ALTERNATIVE FRAMEWORKS:
  LangChain  → Most popular, broadest ecosystem, steepest learning curve
  LlamaIndex → RAG-focused, simpler for search/retrieval pipelines
  DSPy       → Prompt optimization via compilation (academic origin)
  Haystack   → Production-focused, good for enterprise search
```

### Quantization for Local Model Loading

```
GGUF FORMAT (GPT-Generated Unified Format):
  Compressed model file for running LLMs on consumer hardware.

QUANTIZATION LEVELS:
  ┌────────────┬─────────┬──────────────┬────────────────────────┐
  │ Precision  │ Size    │ Quality      │ Use Case               │
  ├────────────┼─────────┼──────────────┼────────────────────────┤
  │ FP32       │ 100%    │ Best         │ Training (not inference)│
  │ FP16/BF16  │ 50%     │ Excellent    │ Full-quality inference  │
  │ INT8 (8-bit│ 25%     │ Very good    │ Server inference        │
  │ INT4 (4-bit│ 12.5%   │ Good         │ Consumer GPU inference  │
  │ INT3 (3-bit│ 9%      │ Noticeable   │ Last resort (small GPU) │
  │ INT2 (2-bit│ 6%      │ Poor         │ Experimental only       │
  └────────────┴─────────┴──────────────┴────────────────────────┘

  RULE OF THUMB (Alammar):
  "Look for at least 4-bit quantized models. Good balance between
   compression and accuracy. Below 4-bit, performance degrades noticeably.
   Better to use a SMALLER model with HIGHER precision."

  Example: Phi-3-mini-4k-instruct
    FP16: 7.6 GB VRAM
    INT8: 3.8 GB VRAM (GGUF Q8_0)
    INT4: 2.0 GB VRAM (GGUF Q4_K_M) ← sweet spot
```

### Chains: Connecting LLM Components

```
A "chain" connects multiple steps into a pipeline:

SIMPLE CHAIN (Single Prompt → LLM → Output):
  prompt_template → LLM → output_parser

  Template: "Translate '{text}' to French."
  Input:    text = "Hello world"
  → LLM generates → "Bonjour le monde"
  → Output parser extracts the translation

MULTI-PROMPT CHAIN (Sequential Steps):
  Step 1: "Extract key topics from this article: {article}"
  Step 2: "Write a summary for each topic: {topics}"
  Step 3: "Format as bullet points: {summaries}"

  Each step's output feeds into the next step's input.

PARALLEL CHAINS (Fan-out/Fan-in):
  ┌→ Chain A: "Analyze sentiment"     ─┐
  ├→ Chain B: "Extract entities"      ─┤
  └→ Chain C: "Detect language"       ─┘
                                        ▼
                            Combine all results

  Use case: Process one document through multiple analyses simultaneously.
```

### Memory: Helping LLMs Remember Conversations

```
┌──────────────────────────────────────────────────────────────────┐
│              MEMORY TYPES IN LANGCHAIN                            │
│                                                                  │
│  1. CONVERSATION BUFFER (Simplest)                               │
│     Stores entire conversation history as raw text.              │
│     Pros: Complete context, simple                               │
│     Cons: Token count grows linearly → eventually exceeds        │
│           context window                                         │
│                                                                  │
│     Token cost: O(n) where n = conversation length               │
│                                                                  │
│  2. WINDOWED CONVERSATION BUFFER                                 │
│     Keeps only last K turns of conversation.                     │
│     Pros: Fixed token cost, fast                                 │
│     Cons: Forgets early context                                  │
│                                                                  │
│     Token cost: O(K) — constant                                  │
│                                                                  │
│  3. CONVERSATION SUMMARY                                         │
│     Periodically summarizes older conversation.                   │
│     "Summarize the conversation so far into 1 paragraph."        │
│     Pros: Retains key info, controlled token cost                │
│     Cons: LLM call for summarization (latency + cost)            │
│     Implementation:                                              │
│       - Use a separate LLM call to summarize                     │
│       - Replace old messages with summary                        │
│       - Keep last K raw turns + summary                          │
│                                                                  │
│     Token cost: O(summary_size + K) — bounded                    │
│                                                                  │
│  4. VECTOR-STORE-BACKED MEMORY (RAG for memory)                  │
│     Embed all messages, retrieve relevant ones per turn.         │
│     Pros: Scales to very long conversations                      │
│     Cons: Embedding + retrieval overhead                         │
│                                                                  │
│     Token cost: O(retrieved_k) — controlled                     │
└──────────────────────────────────────────────────────────────────┘
```

### Agents: LLMs That Use Tools

```
┌──────────────────────────────────────────────────────────────────┐
│              HOW AGENTS WORK (ReAct Pattern)                     │
│                                                                  │
│  ReAct = Reasoning + Acting                                      │
│                                                                  │
│  The LLM operates in a loop:                                     │
│                                                                  │
│  Step 1: OBSERVE the input                                       │
│    "User asks: What's the weather in Tokyo?"                    │
│                                                                  │
│  Step 2: THINK about what to do (Reasoning)                      │
│    "I need to check the weather. I'll use the weather tool."     │
│                                                                  │
│  Step 3: ACT — choose a tool and call it (Action)                │
│    Tool: get_weather(city="Tokyo")                              │
│                                                                  │
│  Step 4: OBSERVE the tool's result                               │
│    "Tokyo: 28°C, sunny, humidity 65%"                           │
│                                                                  │
│  Step 5: THINK about whether to respond or use another tool      │
│    "I have the answer. I'll respond to the user."               │
│                                                                  │
│  Step 6: RESPOND with final answer                               │
│    "The weather in Tokyo is 28°C and sunny."                    │
│                                                                  │
│  TOOLS COMMONLY USED:                                            │
│    • Web search (Google, Bing API)                              │
│    • Calculator (for math)                                       │
│    • Database query (SQL, vector search)                         │
│    • API calls (weather, stock prices, maps)                     │
│    • Code execution (Python REPL)                                │
│    • File operations (read, write)                               │
│                                                                  │
│  KEY INSIGHT:                                                    │
│  The LLM DECIDES which tool to use and in what order.            │
│  This is different from a fixed chain where steps are            │
│  pre-determined. The agent is autonomous.                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Chapter 8: Semantic Search and RAG

### Three Categories of Semantic Search

```
┌──────────────────────────────────────────────────────────────────┐
│         THREE TYPES OF SEMANTIC SEARCH SYSTEMS                   │
│                                                                  │
│  1. DENSE RETRIEVAL                                              │
│     Convert query + documents to embeddings.                     │
│     Find nearest documents to query embedding.                   │
│     "Search by meaning, not by keywords."                        │
│                                                                  │
│     Query: "How to bake bread"                                  │
│     Traditional: Finds docs containing "bake" AND "bread"        │
│     Dense: Finds docs about making bread (even if they say       │
│            "cooking dough in oven")                              │
│                                                                  │
│     Tools: Cohere Embed, OpenAI text-embedding-3, sentence-      │
│            transformers (all-MiniLM-L6-v2)                       │
│                                                                  │
│  2. RERANKING                                                    │
│     After initial retrieval, re-score top results with a         │
│     more powerful (but slower) model.                            │
│     "Second pass for precision."                                 │
│                                                                  │
│     Initial retrieval: 1000 results (fast, approximate)          │
│     Reranker: Score top 100 results (slow, precise)              │
│     Final: Return top 10 to user                                 │
│                                                                  │
│     Tools: Cohere Rerank, bge-reranker, cross-encoder models     │
│                                                                  │
│  3. RAG (Retrieval-Augmented Generation)                         │
│     Retrieve relevant documents, feed them to an LLM,            │
│     LLM generates an answer grounded in those documents.         │
│     "Search + Generate."                                         │
│                                                                  │
│     Query → Retrieve docs → Augment prompt → LLM generates       │
│                                                                  │
│     Key benefit: Reduces hallucinations (LLM has ground truth)   │
└──────────────────────────────────────────────────────────────────┘
```

### Dense Retrieval Pipeline

```
FULL DENSE RETRIEVAL PIPELINE:

  ┌─────────────────────────────────────────────────────┐
  │ 1. DOCUMENT INGESTION                               │
  │    Raw documents (PDF, HTML, DOCX, etc.)            │
  │         ↓                                           │
  │    Extract text                                     │
  │         ↓                                           │
  │    Chunk documents (512 tokens, 50-100 overlap)     │
  │         ↓                                           │
  │    Embed each chunk                                 │
  │         ↓                                           │
  │    Store embeddings in vector DB                    │
  └──────────────────────┬──────────────────────────────┘
                         │
  ┌──────────────────────▼──────────────────────────────┐
  │ 2. QUERY TIME                                        │
  │    User query: "How does attention work?"           │
  │         ↓                                           │
  │    Embed query (SAME embedding model)               │
  │         ↓                                           │
  │    Search vector DB for nearest neighbors           │
  │         ↓                                           │
  │    Return top-K results                             │
  └──────────────────────┬──────────────────────────────┘
                         │
  ┌──────────────────────▼──────────────────────────────┐
  │ 3. OPTIONAL RERANKING                                │
  │    Reranker scores (query, document) pairs          │
  │         ↓                                           │
  │    Reorder by relevance score                       │
  │         ↓                                           │
  │    Return refined top-K                             │
  └─────────────────────────────────────────────────────┘

CHUNKING STRATEGIES:
  Fixed-size:  Every 512 tokens (simple, may cut sentences)
  Sentence:    Split on sentence boundaries (preserves meaning)
  Paragraph:   Split on paragraph breaks (good for structured docs)
  Semantic:    Use NLP to find topic boundaries (best quality)
  Recursive:   Try large chunks first, split if too big (LangChain default)

VECTOR DATABASE OPTIONS:
  ┌──────────────┬────────────┬─────────────┬────────────────────┐
  │ Vector DB    │ Type       │ Scalability │ Best For           │
  ├──────────────┼────────────┼─────────────┼────────────────────┤
  │ Chroma       │ Embedded   │ Small-Med   │ Prototyping, local │
  │ FAISS        │ Library    │ Medium      │ Pure speed, local  │
  │ Qdrant       │ Server     │ Large       │ Production, Rust   │
  │ Pinecone     │ Cloud      │ Very Large  │ Managed, no ops   │
  │ Weaviate     │ Server     │ Large       │ Hybrid search     │
  │ pgvector     │ Extension  │ Medium-Large│ PostgreSQL already │
  │ Milvus       │ Server     │ Very Large  │ Billion-scale     │
  └──────────────┴────────────┴─────────────┴────────────────────┘
```

### Retrieval Evaluation Metrics

```
HOW TO EVALUATE RETRIEVAL QUALITY:

  RELEVANCE LABELS:
  For each (query, document) pair, label as relevant (1) or not (0).
  This is your ground truth test set.

  METRICS:

  1. HIT RATE (Recall@K)
     "Did any relevant doc appear in top-K results?"
     Hit@10 = 1 if ANY relevant doc in top 10, else 0
     Average over all queries.

  2. MRR (Mean Reciprocal Rank)
     "How high is the FIRST relevant result?"
     RR = 1/rank of first relevant doc
     If first result is relevant: RR = 1/1 = 1.0
     If third result is relevant: RR = 1/3 = 0.33
     MRR = average RR over all queries

  3. NDCG (Normalized Discounted Cumulative Gain)
     "How well-ordered are ALL relevant results?"
     Rewards relevant results at higher ranks.
     Penalizes relevant results at lower ranks.
     Range: 0 to 1 (1 = perfect ranking)
     Best for: Multiple relevant results with graded relevance

  4. PRECISION@K
     "What fraction of top-K results are relevant?"
     P@10 = (# relevant in top 10) / 10

  IMPORTANCE:
  "The quality of RAG is bounded by the quality of retrieval.
   If retrieval returns wrong documents, the LLM will generate
   wrong answers — no matter how good the LLM is."
```

### Full RAG Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              COMPLETE RAG SYSTEM ARCHITECTURE                     │
│                                                                  │
│  OFFLINE (Indexing):                                             │
│                                                                  │
│    Documents → Extract → Chunk → Embed → Store in Vector DB     │
│    "The Complete Works of Shakespeare"                           │
│         → split into 512-token chunks                            │
│         → embed each chunk                                       │
│         → store {chunk_text, embedding, metadata}                │
│                                                                  │
│  ONLINE (Query):                                                 │
│                                                                  │
│    User: "What does Hamlet say about death?"                    │
│         ↓                                                        │
│    Embed query                                                   │
│         ↓                                                        │
│    Retrieve top-5 chunks from vector DB                         │
│         ↓                                                        │
│    Rerank chunks (optional, for precision)                       │
│         ↓                                                        │
│    Build augmented prompt:                                       │
│    ┌────────────────────────────────────────┐                   │
│    │ System: You are a helpful assistant.   │                   │
│    │ Answer the question based on the       │                   │
│    │ following context. If the context      │                   │
│    │ doesn't contain the answer, say        │                   │
│    │ "I don't know."                        │                   │
│    │                                        │                   │
│    │ Context:                               │                   │
│    │ [Chunk 1: To be or not to be...]       │                   │
│    │ [Chunk 2: O that this too too solid    │                   │
│    │  flesh would melt...]                  │                   │
│    │                                        │                   │
│    │ Question: What does Hamlet say         │                   │
│    │ about death?                           │                   │
│    └────────────────────────────────────────┘                   │
│         ↓                                                        │
│    LLM generates grounded answer                                 │
│    "In his famous 'To be or not to be' soliloquy, Hamlet..."    │
│         ↓                                                        │
│    Return answer (optionally with source citations)              │
│                                                                  │
│  ADVANCED RAG TECHNIQUES:                                        │
│    • Query transformation: Rewrite query for better retrieval   │
│    • HyDE: Generate hypothetical answer, embed THAT for search  │
│    • Multi-query: Generate multiple queries, combine results    │
│    • Parent-document retrieval: Retrieve chunks, return parent  │
│    • Graph RAG: Use knowledge graph for multi-hop reasoning     │
│    • Adaptive RAG: Decide whether to retrieve (not every query  │
│      needs retrieval)                                            │
└──────────────────────────────────────────────────────────────────┘
```

### RAG vs Fine-Tuning Decision Matrix

```
┌────────────────────┬─────────────────────┬──────────────────────┐
│ Use Case           │ RAG                 │ Fine-Tuning          │
├────────────────────┼─────────────────────┼──────────────────────┤
│ New knowledge      │ ✅ Best choice      │ ❌ Expensive, slow  │
│ Frequently updated │ ✅ Update vector DB │ ❌ Retrain each time│
│ Domain vocabulary  │ Can help            │ ✅ Better           │
│ Tone/style         │ Can guide via prompt│ ✅ Better           │
│ Reducing halluc.   │ ✅ Ground in facts  │ ⚠️ Partial          │
│ Fast prototyping   │ ✅ Hours            │ ❌ Days             │
│ Cost (ongoing)     │ Retrieval + LLM     │ Training + serving  │
│ Private docs       │ ✅ Keep in vector DB│ ⚠️ Data in model   │
│ Format adherence   │ ⚠️ Prompt-dependent │ ✅ Reliable        │
│ Reasoning skills   │ ⚠️ Inherent         │ ✅ Can improve     │
└────────────────────┴─────────────────────┴──────────────────────┘

ALAMMAR'S GUIDANCE:
  "Start with RAG. It's faster, cheaper, and more controllable.
   Only fine-tune when RAG doesn't meet your quality bar or when
   you need to change the model's style/tone/format adherence."
```

---

## Chapter 9: Multimodal LLMs

### Vision Transformer (ViT) — How Images Become Tokens

```
┌──────────────────────────────────────────────────────────────────┐
│         HOW A VISION TRANSFORMER PROCESSES IMAGES                │
│                                                                  │
│  ORIGINAL TRANSFORMER (Text):                                    │
│    Text → Tokenizer → Token IDs → Embeddings → Transformer      │
│                                                                  │
│  VISION TRANSFORMER (Images):                                    │
│    Image → Split into patches → Flatten → Embed → Transformer   │
│                                                                  │
│  THE PATCH MECHANISM:                                            │
│                                                                  │
│    ┌─────┬─────┬─────┐                                          │
│    │ P1  │ P2  │ P3  │    Image is divided into patches.       │
│    ├─────┼─────┼─────┤    Paper title: "An Image is Worth     │
│    │ P4  │ P5  │ P6  │    16x16 Words"                        │
│    ├─────┼─────┼─────┤                                          │
│    │ P7  │ P8  │ P9  │    Each 16x16 patch = one "token"      │
│    └─────┴─────┴─────┘                                          │
│                                                                  │
│    Patch → Flatten → Linear Projection → Embedding              │
│    (similar to token ID → embedding lookup for text)            │
│                                                                  │
│  POSITIONAL EMBEDDINGS:                                          │
│    Just like text tokens need position info,                     │
│    image patches need to know WHERE in the image they are.      │
│    P1 = top-left, P9 = bottom-right (in 3x3 grid)              │
│                                                                  │
│  KEY INSIGHT:                                                    │
│    "Once images are converted to patch embeddings,              │
│     the Transformer treats them EXACTLY like text tokens."      │
│    → Same self-attention mechanism works for both!               │
└──────────────────────────────────────────────────────────────────┘
```

### CLIP: Connecting Text and Images

```
┌──────────────────────────────────────────────────────────────────┐
│              CLIP (Contrastive Language-Image Pretraining)       │
│                                                                  │
│  CLIP learns a SHARED embedding space for text and images.       │
│  "A photo of a cat" and an actual cat photo → similar vectors.  │
│                                                                  │
│  TRAINING (Contrastive Learning):                                │
│                                                                  │
│    Text Encoder                Image Encoder                     │
│    ┌──────────┐                ┌──────────┐                     │
│    │ "A cat"  │ → embedding A  │ 🐱 photo │ → embedding X      │
│    │ "A dog"  │ → embedding B  │ 🐶 photo │ → embedding Y      │
│    │ "A bird" │ → embedding C  │ 🐦 photo │ → embedding Z      │
│    └──────────┘                └──────────┘                     │
│                                                                  │
│    TRAINING OBJECTIVE:                                           │
│      MAXIMIZE similarity(A, X)  ← cat text + cat photo           │
│      MINIMIZE similarity(A, Y)  ← cat text + dog photo           │
│      MINIMIZE similarity(A, Z)  ← cat text + bird photo          │
│                                                                  │
│  RESULT: A shared embedding space where:                         │
│    • Text queries can find matching images                       │
│    • Images can be classified using text labels                  │
│    • Zero-shot classification: "Is this a photo of a cat?"      │
│                                                                  │
│  APPLICATIONS:                                                   │
│    • Image search ("find photos of sunsets")                    │
│    • Zero-shot image classification (no training needed)        │
│    • Content moderation (detect unsafe images via text query)   │
│    • Multimodal RAG (retrieve images AND text)                  │
└──────────────────────────────────────────────────────────────────┘
```

### BLIP-2: Bridging Vision and Language Models

```
┌──────────────────────────────────────────────────────────────────┐
│              BLIP-2 ARCHITECTURE                                 │
│                                                                  │
│  PROBLEM: Vision encoders and LLMs are trained separately.      │
│  How do you connect them efficiently?                           │
│                                                                  │
│  SOLUTION: Use a "bridge" called the Q-Former.                  │
│                                                                  │
│  ┌──────────┐     ┌──────────┐     ┌──────────────────┐        │
│  │  Frozen  │     │  Q-Former│     │  Frozen LLM      │        │
│  │  Image   │ ──→ │  (Light  │ ──→ │  (e.g., OPT,     │        │
│  │ Encoder  │     │  Bridge) │     │   Flan-T5)       │        │
│  │  (ViT)   │     │          │     │                  │        │
│  └──────────┘     └──────────┘     └──────────────────┘        │
│                                                                  │
│  THE Q-FORMER:                                                   │
│    A small transformer that "translates" image features         │
│    into the language the LLM can understand.                     │
│                                                                  │
│    Input:  Image features from ViT (frozen, not trained)        │
│    Output: Fixed number of "visual tokens" that the LLM reads   │
│                                                                  │
│  WHY IT MATTERS:                                                 │
│    • Only the Q-Former is trained (cheap!)                      │
│    • Can use ANY pretrained ViT (frozen)                        │
│    • Can use ANY pretrained LLM (frozen)                        │
│    • Enables: image captioning, VQA, image-based chat           │
│                                                                  │
│  USE CASES:                                                      │
│    1. IMAGE CAPTIONING                                           │
│       Input: [IMAGE] + "Describe this image"                    │
│       Output: "A golden retriever playing fetch in a park"      │
│                                                                  │
│    2. VISUAL QUESTION ANSWERING (VQA)                           │
│       Input: [IMAGE] + "What color is the dog?"                 │
│       Output: "Golden"                                          │
│                                                                  │
│    3. MULTIMODAL CHAT                                            │
│       Input: [IMAGE] + conversation history                      │
│       Output: Natural language discussion about the image       │
└──────────────────────────────────────────────────────────────────┘
```

### Multimodal Landscape Comparison

```
┌──────────────────┬──────────────┬───────────────────────────────┐
│ Model            │ Input        │ Key Innovation               │
├──────────────────┼──────────────┼───────────────────────────────┤
│ CLIP (OpenAI)    │ Text + Image │ Shared embedding space       │
│ BLIP-2 (Salesforce)│ Image→Text │ Q-Former bridge (cheap)     │
│ LLaVA            │ Image + Text │ Visual instruction tuning    │
│ GPT-4V (OpenAI)  │ Text + Image │ Native multimodal training   │
│ Gemini (Google)  │ Text+Img+Vid│ Native multimodal from scratch│
│ Qwen-VL (Alibaba)│ Image + Text │ Multi-resolution vision      │
│ Fuyu (Adept)     │ Image + Text │ No separate encoder needed   │
└──────────────────┴──────────────┴───────────────────────────────┘

TWO APPROACHES TO MULTIMODAL:
  1. FUSION (CLIP, BLIP-2):
     Separate encoders → Bridge → Combine
     Pros: Modular, can swap components
     Cons: Bridge training required

  2. NATIVE (GPT-4V, Gemini):
     Train on mixed text+image data from scratch
     Pros: Deepest integration, best quality
     Cons: Extremely expensive to train, proprietary
```

---

## Cross-Book Comparison

```
┌────────────────────┬────────────────────┬──────────────────────┐
│ Topic              │ HoLM (Alammar)     │ AI Eng (Huyen)       │
├────────────────────┼────────────────────┼──────────────────────┤
│ Focus              │ Hands-on code      │ Conceptual breadth   │
│ RAG Coverage       │ Ch 8: Deep dive    │ Ch 7: Overview       │
│                    │ (dense, rerank,    │ (positioning, when   │
│                    │ eval metrics)      │ to use)              │
│ Prompt Eng         │ Ch 6: Detailed     │ Ch 5: Strategic      │
│ Fine-Tuning        │ Ch 10-12: Hands-on │ Ch 7: Overview       │
│                    │ (SBERT, LoRA, DPO) │ (LoRA, QLoRA)        │
│ Agents             │ Ch 7: LangChain    │ Ch 7: Failure modes  │
│ Embeddings         │ Ch 2+10: Create +  │ Ch 2: Overview       │
│                    │ train your own     │                      │
│ Multimodal         │ Ch 9: Deep dive    │ Not covered          │
│                    │ (CLIP, BLIP-2, ViT)│                      │
│ Code Examples      │ Extensive Python   │ Conceptual           │
│ Best For           │ Engineers building │ Leaders deciding     │
│                    │ LLM applications   │ AI strategy          │
└────────────────────┴────────────────────┴──────────────────────┘

COMPLEMENTARY:
  HoLM = HOW to build (code, tools, step-by-step)
  Huyen = WHAT and WHY (concepts, trade-offs, strategy)
  Read Huyen first for understanding, then HoLM for implementation.
```

---

## Interview Q&As

### Q1: "What's the difference between a chain and an agent in LangChain?"

"A chain is a fixed sequence of steps — prompt template → LLM → output parser. The path is pre-determined. An agent uses an LLM to DECIDE which steps to take and in what order. The LLM observes the input, reasons about what tool to use (ReAct pattern: Reason + Act), calls the tool, observes the result, and decides whether to respond or use another tool. Agents are autonomous; chains are deterministic. Use chains for predictable pipelines; use agents when the path depends on the input."

### Q2: "How would you build a RAG system for a company's internal documents?"

"I'd build a four-component pipeline: (1) Ingestion — extract text from PDFs/docs, chunk into 512-token segments with overlap, embed each chunk using a model like text-embedding-3-small or all-MiniLM-L6-v2, store in a vector database like Qdrant or Pinecone. (2) Query — embed the user query with the SAME model, retrieve top-K chunks. (3) Rerank — optionally use a cross-encoder reranker for precision. (4) Generate — build a prompt with the retrieved context and the query, have the LLM generate a grounded answer with citations. I'd evaluate using hit rate and MRR on a test set of queries with known relevant documents."

### Q3: "Explain how CLIP creates a shared embedding space for text and images."

"CLIP uses contrastive learning. It has two encoders: a text encoder and an image encoder. During training, it processes text-image pairs — matching pairs (cat text + cat photo) are positive examples, mismatched pairs are negative examples. The training objective maximizes cosine similarity between positive pairs and minimizes it for negative pairs. After training, text and images live in the same vector space: a text query 'sunset photo' will have high similarity with actual sunset images. This enables zero-shot classification — you don't need to train a classifier for each category; you just compare image embeddings to text label embeddings."

### Q4: "When would you use RAG vs fine-tuning?"

"Use RAG when you need to add new knowledge, when documents update frequently, when you need citations/sources, or for fast prototyping. RAG is faster to build, cheaper to maintain, and more controllable. Use fine-tuning when you need to change the model's tone, style, or output format adherence, when you need domain-specific vocabulary, or when RAG quality isn't sufficient. Start with RAG — it's faster, cheaper, and more controllable. Only fine-tune when RAG doesn't meet your quality bar."

### Q5: "What is the Q-Former in BLIP-2 and why is it important?"

"The Q-Former is a lightweight transformer bridge that connects a frozen vision encoder (ViT) to a frozen LLM. It translates image features into 'visual tokens' that the LLM can understand. The importance is that only the Q-Former is trained — the expensive ViT and LLM remain frozen. This makes multimodal training much cheaper than training from scratch. You can pair any pretrained ViT with any pretrained LLM and just train the Q-Former bridge. It enables image captioning, visual question answering, and multimodal chat without retraining either large model."

### Q6: "What are the different memory types in LangChain and when do you use each?"

"Four types: (1) Conversation Buffer stores the entire conversation — complete context but grows unboundedly. (2) Windowed Buffer keeps only the last K turns — bounded but forgets early context. (3) Conversation Summary periodically summarizes older messages — bounded and retains key info but costs an extra LLM call. (4) Vector-Store-Backed Memory embeds all messages and retrieves relevant ones per turn — scales to very long conversations. For short chats, use buffer. For medium conversations, use windowed. For long conversations where early context matters, use summary or vector-store-backed memory."

### Q7: "How do you evaluate a RAG system's retrieval quality?"

"Three main metrics: (1) Hit Rate (Recall@K) — did any relevant document appear in the top-K results? (2) Mean Reciprocal Rank (MRR) — how high is the first relevant result? RR = 1/rank of first relevant doc. (3) NDCG — how well-ordered are all relevant results, rewarding higher-ranked relevant docs. You need a labeled test set of query-document pairs with relevance judgments. The key insight: RAG quality is bounded by retrieval quality — if retrieval returns wrong documents, no LLM can generate the right answer."

### Q8: "What is quantization and why does it matter for deploying LLMs?"

"Quantization reduces the numerical precision of model weights — from FP32 (4 bytes) to FP16 (2 bytes), INT8 (1 byte), or INT4 (0.5 bytes). This cuts memory requirements by 2-8x with minimal quality loss. For example, Phi-3-mini goes from 7.6GB (FP16) to 2GB (INT4), making it runnable on consumer GPUs. Alammar's rule: use at least 4-bit quantization. Below 4-bit, degradation becomes noticeable — better to use a smaller model at higher precision than a large model at 2-bit."
