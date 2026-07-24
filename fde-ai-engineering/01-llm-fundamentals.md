# Chapter 1: LLM Fundamentals

> **Interview question:** "Tell me about LLMs. How do they work?"

---

## 1. What Is an LLM?

**Analogy:** An LLM is like someone who has read the entire internet and is incredibly good at predicting the next word in any conversation. But they've also internalized reasoning patterns, facts, code, and logic from all that reading.

**LLM = Large Language Model.** It's a neural network trained on massive text data to predict the next token (word piece).

A **token** is a chunk of text — roughly 3/4 of a word in English.
- "Hello world" = 2 tokens
- "unbelievable" might be 3 tokens: "un" + "believ" + "able"
- 100 tokens ≈ 75 words

---

## 2. How LLMs Actually Work (Simplified)

### The Transformer Architecture

```
         Input: "The cat sat on the"
                    │
                    ▼
         ┌─────────────────────┐
         │  TOKENIZATION        │  Split text into tokens
         │  ["The","cat","sat"] │  Each token → a number (ID)
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  EMBEDDING LAYER     │  Each token ID → vector (list of numbers)
         │                      │  Similar words have similar vectors
         │  "cat"  → [0.2, -1.3, ...]
         │  "dog"  → [0.3, -1.1, ...]  ← similar to "cat"
         │  "pizza"→ [-0.8, 2.1, ...]  ← very different
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  TRANSFORMER LAYERS  │  The "brain". Multiple layers of
         │  (self-attention)    │  attention mechanism that looks at
         │                      │  ALL previous tokens to understand
         │  "What should come   │  context before predicting next token
         │   after 'on the'?"   │
         └──────────┬──────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │  OUTPUT LAYER        │  Probability distribution over
         │                      │  the entire vocabulary
         │                      │
         │  "mat"  → 72%        │
         │  "floor"→ 15%        │
         │  "chair"→ 8%         │
         │  ...                  │
         └─────────────────────┘
                    │
                    ▼
         Output: "mat" (most likely next token)
```

### Self-Attention (The Key Innovation)

**Analogy:** Reading a detective novel. When you see "the killer picked up the knife," you immediately connect "the killer" to a character mentioned 50 pages ago. Self-attention does this — every token "looks at" every other token to understand relationships.

```
Sentence: "The dog crossed the street because it was tired."

Self-attention figures out:
  "it" → refers to "dog" (not "street")
  Because "it was tired" — tiredness applies to dogs, not streets.
```

Each attention layer learns different relationships:
- Layer 1: grammar ("the" goes with nouns)
- Layer 5: semantics ("dog" is an animal)
- Layer 20+: reasoning and logic patterns

---

## 3. The Three Training Stages

### Stage 1: Pre-Training (Learning the World)

```
Goal: Learn language, facts, reasoning, code from the entire internet.

Data: Trillions of tokens (Wikipedia, books, code, web pages)
      ~4-5 trillion tokens for models like Llama 3
Cost: $60M-$200M+ (for frontier models)
Duration: Months on thousands of GPUs

What happens:
  The model sees: "The capital of France is ___"
  It guesses randomly at first.
  It compares its guess to the real next word: "Paris"
  It adjusts its weights (via backpropagation) to be more right next time.
  Repeat 4 TRILLION times.

Result: A "base model" that can complete text but doesn't follow instructions.
```

### Stage 2: Supervised Fine-Tuning (SFT) — Learning to Chat

```
Goal: Turn the text-completer into a helpful assistant.

Data: High-quality human-written Q&A pairs
      Human: "What is 2+2?"
      Assistant: "2+2 equals 4."
      (~100K-1M examples)

Cost: $1K-$50K (much cheaper than pre-training)
Duration: Hours to days on a few GPUs

What happens:
  The model learns the FORMAT of being helpful.
  Instead of completing "What is 2+2?" with "What is 3+3?" (text completion),
  it learns to ANSWER: "2+2 equals 4."

Result: An "instruct model" or "chat model" — follows instructions.
```

### Stage 3: RLHF (Reinforcement Learning from Human Feedback)

```
Goal: Make the model's answers PREFERRED by humans over the base model.

Data: Human preferences
      - Show humans 2 model outputs for the same prompt
      - Human picks the better one
      - Train a "reward model" on these preferences
      - Use the reward model to further fine-tune the LLM via reinforcement learning

Cost: $10K-$100K
Duration: Days

Result: A model that gives helpful, harmless, honest answers (aligned).
```

**THE FULL PIPELINE:**
```
Raw Text (4T tokens)
    │
    ▼  [Pre-training — $100M+, months]
Base Model (Llama-3-8B-Base)
    │
    ▼  [SFT — $1K-$50K, hours-days]
Instruct Model (Llama-3-8B-Instruct)
    │
    │   ┌──────────────────────────────┐
    │   │ Many models STOP here.        │
    │   │ This is what you download     │
    │   │ from HuggingFace.             │
    │   └──────────────────────────────┘
    │
    ▼  [RLHF — $10K-$100K, days]
Aligned Model (Llama-3-8B-Instruct + RLHF)
    │
    ▼
ChatGPT-grade assistant
```

---

## 4. Key LLM Concepts for Interviews

### Context Window (The "Memory")

```
The context window is how much text the model can "see" at once.

Model                  Context Window
─────────────────────────────────────
GPT-3 (2020)           2K tokens     (~1.5 pages)
GPT-4 (2023)           128K tokens   (~300 pages)
Claude 3 (2024)        200K tokens   (~500 pages)
Gemini 1.5 (2024)      1M tokens     (~2,500 pages)
Llama 3.1 (2024)       128K tokens   (~300 pages)

Key insight: Just because a model CAN handle 1M tokens doesn't mean
it processes them all perfectly. "Lost in the middle" problem —
models sometimes miss information in the middle of long contexts.
```

### Temperature and Sampling

```
Temperature controls randomness/creativity:

Temperature = 0.0: Always pick the most likely token. Deterministic.
                    Good for: code, math, factual answers.

Temperature = 0.7: Some randomness. Most common for chat.
                    Good for: conversation, brainstorming.

Temperature = 1.0+: High randomness. Wild creative outputs.
                     Good for: poetry, creative writing.

Analogy:
  temp=0 → The model is a strict librarian. Always gives the most accurate answer.
  temp=1 → The model is a creative writer. Takes risks, sometimes wrong but interesting.
```

### Tokenization

```
Text → Tokens → Token IDs → Embeddings

"Hello, world!" → ["Hello", ",", " world", "!"] → [9906, 11, 1917, 0] → vectors

Important implications:
- LLMs don't "see" letters or characters. They see tokens.
- " strawberry" and "strawberry" are different tokens (space matters!)
- Tokenization affects spelling tasks (models are bad at counting letters)
- Pricing is per-token: 1M input tokens for $0.15-$60 depending on model
```

### Hallucinations

```
WHY do LLMs hallucinate?
  Because they are PROBABILITY MACHINES, not fact databases.
  They generate the most LIKELY next token, not the most TRUTHFUL one.

  "Who won the 2026 World Series?"
  → Model has no data about 2026, but generates a plausible-sounding answer.

HOW to reduce hallucinations:
  1. RAG (give the model source documents to ground its answers)
  2. Lower temperature for factual questions
  3. Ask the model to cite sources
  4. System prompt: "If you don't know, say 'I don't know'"
```

---

## 5. The Model Landscape (2024-2025)

### Proprietary (API-based)

| Model | Context | Strengths | Cost (per 1M tokens) |
|-------|---------|-----------|----------------------|
| GPT-4o | 128K | Best general-purpose, multimodal | $2.50 in / $10 out |
| Claude 3.5 Sonnet | 200K | Best coding, long context | $3 in / $15 out |
| Gemini 1.5 Pro | 1M+ | Massive context, multimodal | $1.25 in / $5 out |
| GPT-4o-mini | 128K | Cheapest good model | $0.15 in / $0.60 out |

### Open-Source (Self-hosted)

| Model | Size | Strengths | Hardware Needed |
|-------|------|-----------|-----------------|
| Llama 3.1 8B | 8B params | Small, fast, good | 1 GPU (16GB VRAM) |
| Llama 3.1 70B | 70B params | Near-GPT-4 quality | 2-4 GPUs |
| Llama 3.1 405B | 405B params | Frontier-class open model | 8 GPUs (H100s) |
| Mistral 7B | 7B params | Efficient, punch-above-weight | 1 GPU (16GB VRAM) |
| Qwen 2.5 72B | 72B params | Excellent multilingual | 2-4 GPUs |
| GLM-4 9B | 9B params | Strong reasoning, tool use | 1 GPU |

### When to Use Which (FDE Decision Framework)

```
Is the data extremely sensitive? → Open-source, self-hosted (Llama 3.1)
Cost-sensitive at high volume? → Open-source OR GPT-4o-mini
Need absolute best quality? → Claude 3.5 Sonnet or GPT-4o
Need 1M+ context? → Gemini 1.5 Pro
Need vision/image understanding? → GPT-4o, Claude 3.5, Gemini 1.5
Need on-device (phone)? → Phi-3 mini, Qwen2-1.5B
```

---

## 6. Inference — How LLMs Are Served

```
[Client Request]
  POST /v1/chat/completions
  {"messages": [{"role":"user","content":"Hello"}]}
       │
       ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  API Gateway /   │ ──> │  Inference Server│ ──> │  GPU             │
│  Load Balancer   │     │  (vLLM/TGI)      │     │  (NVIDIA A100/H100)│
│                  │     │                  │     │                  │
│  - Rate limiting │     │  - Batches       │     │  - Model weights │
│  - Auth          │     │    requests      │     │    loaded in VRAM │
│  - Routing       │     │  - KV cache mgmt │     │  - Matrix math    │
└──────────────────┘     └──────────────────┘     └──────────────────┘
       │
       ▼
[Response streamed back token-by-token via SSE]
```

### Serving Technologies

| Tool | What It Does | Why It's Important |
|------|-------------|-------------------|
| **vLLM** | High-throughput inference engine | PagedAttention → 10-20× more throughput than naive inference |
| **TGI** (Text Generation Inference) | HuggingFace's serving solution | Production-ready, used by many LLM hosting platforms |
| **llama.cpp** | CPU/edge inference | Run LLMs on MacBooks, Raspberry Pi, low-resource environments |
| **Ollama** | Easy local LLM runner | `ollama run llama3` — one command to run locally |
| **TensorRT-LLM** | NVIDIA's optimized inference | Fastest possible inference on NVIDIA GPUs |

---

## 7. Inference Optimization Techniques

### Quantization (Making Models Smaller)

```
Original model:  FP16 (16 bits per weight)  → 70B model = 140 GB VRAM
Quantized:       INT4 (4 bits per weight)   → 70B model = 35 GB VRAM

4× less memory → runs on fewer GPUs → much cheaper
Slight quality degradation (~1-3% on benchmarks)

Formats: GGUF (llama.cpp), AWQ, GPTQ, BNB (bitsandbytes)
```

### KV Cache

```
When generating token N, the model doesn't recompute tokens 1 to N-1.
Instead, it stores ("caches") the computed representations of previous tokens.

Without KV cache: Generating 1000 tokens = O(n²) computation
With KV cache:    Generating 1000 tokens = O(n) computation

This is why the first token is slow (prefill) but subsequent tokens are fast (decode).
```

### Continuous Batching

```
Without batching:
  Request A ──────────────────> (50 tokens)     GPU: 5% utilized
  Request B            ────────> (30 tokens)    GPU: 5% utilized
  (each request processed sequentially → GPU wasted)

With continuous batching:
  Request A ──────────────────>                 ┐
  Request B            ────────>                │  GPU: 80% utilized
  Request C     ───────────────>                │  (all processed together)
  Request D  ──────────────────>                ┘
  (many requests share the GPU simultaneously → massive throughput)
```

---

## 8. Pricing Models (For FDE Cost Analysis)

```
API Pricing (per 1 million tokens):
  GPT-4o:           $2.50 in / $10.00 out
  GPT-4o-mini:      $0.15 in / $0.60 out
  Claude 3.5:       $3.00 in / $15.00 out
  Llama 3.1 70B (self-hosted): ~$0.50-1.00 (GPU cost)

Cost estimation example:
  App: Customer support bot
  1M conversations/month, avg 2000 tokens each = 2B tokens/month
  
  GPT-4o:    2B × ($2.50+$10)/2 / 1M = $12,500/month
  GPT-4o-mini: 2B × ($0.15+$0.60)/2 / 1M = $750/month
  Self-hosted Llama 3.1 8B: ~$200-500/month (2 GPU instances)

FDE insight: The model choice DRAMATICALLY affects unit economics.
A good FDE helps the customer choose the right model for their budget.
```

---

## Interview Q&A

**Q: "Can you explain how an LLM works at a high level?"**
A: An LLM is a transformer neural network trained to predict the next token. It's trained in three stages: pre-training (learn language and facts from internet-scale data), supervised fine-tuning (learn to follow instructions and chat), and RLHF (align with human preferences). At inference time, it takes input tokens, processes them through attention layers that understand context, and outputs a probability distribution over the vocabulary for the next token.

**Q: "What is self-attention?"**
A: Self-attention is the core mechanism of transformers. For each token, the model computes how much it should "attend to" (focus on) every other token in the sequence. This lets the model understand long-range dependencies — like connecting "it" to the noun it refers to 50 words ago. Multi-head attention runs this process in parallel with different "perspectives" — some heads focus on grammar, others on meaning, others on reasoning.

**Q: "What causes hallucinations and how do you reduce them?"**
A: LLMs are probabilistic token predictors, not fact databases. They hallucinate when they generate plausible-sounding but incorrect tokens. I reduce hallucinations through: (1) RAG — grounding responses in retrieved source documents, (2) lower temperature for factual queries, (3) system prompts that enforce "say I don't know if unsure", and (4) structured output constraints that prevent the model from generating invalid fields.

**Q: "How would you choose between GPT-4o and an open-source model?"**
A: I evaluate five factors: (1) Data sensitivity — if data can't leave the network, open-source is mandatory. (2) Volume/cost — at 2B tokens/month, GPT-4o costs $12K/month while self-hosted Llama is ~$500/month. (3) Latency requirements — self-hosted can be faster for single requests (no network round-trip to API). (4) Quality bar — if the task needs frontier-level reasoning, GPT-4o/Claude 3.5. (5) Compliance — regulated industries (healthcare, finance) often require self-hosted.

**Q: "What is quantization and why does it matter?"**
A: Quantization reduces the precision of model weights — from FP16 (16 bits) to INT4 (4 bits). This shrinks the model 4× in memory, letting a 70B model run on a single GPU instead of 4. The tradeoff is a small quality drop (1-3% on benchmarks). For FDE work, this is huge — it changes a $25K/month GPU bill into a $6K/month bill while serving nearly the same quality.
