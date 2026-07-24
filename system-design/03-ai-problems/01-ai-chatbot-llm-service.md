# System Design: AI Chatbot / LLM Service (ChatGPT-style)

> **Analogy**: Picture a high-end restaurant kitchen. The **maître d'** (API gateway) takes orders and routes them. **Servers** (load balancers) hand tickets to specialized **chefs** (GPUs) who each have a station (model). Some orders are quick appetizers (short prompts → small model), others are multi-course meals (long context → large model). A **sous-chef** (KV cache manager) keeps prep work hot so chefs don't redo work. Orders stream out dish-by-dish (token streaming) rather than arriving all at once.

---

## 1. Problem Statement

Design a ChatGPT-style conversational AI service that can:
- Accept natural language prompts and stream human-quality responses.
- Maintain multi-turn conversation history and context.
- Scale to millions of concurrent users with sub-second first-token latency.
- Support token-based usage metering, rate limits, and model selection.

**Scale assumptions:**
- 10M daily active users, ~50 requests/user/day → **500M requests/day**, ~6k RPS average, ~25k peak RPS.
- Avg prompt 500 tokens, avg completion 400 tokens → ~450M tokens/hr at peak.
- Availability target 99.9%, p99 time-to-first-token (TTFT) < 1.5s.

---

## 2. Requirements

### Functional
- Accept chat completion requests (prompt + params: model, temperature, max_tokens, stop).
- Stream tokens back via Server-Sent Events (SSE) as they're generated.
- Persist conversation sessions; allow resume, fork, delete.
- Support multiple model tiers (small/fast, large/smart) and tool/function calling.
- Enforce per-user rate limits and usage quotas.

### Non-Functional
| Requirement | Target |
|---|---|
| Latency (TTFT) | p99 < 1.5s |
| Latency (per-token) | p99 < 50ms inter-token |
| Throughput | 25k concurrent streaming sessions |
| Availability | 99.9% monthly |
| Cost | < $X per 1M output tokens delivered |
| Durability | Conversations replicated, point-in-time recovery |

---

## 3. Capacity Estimation (Back-of-Envelope)

```
Requests:        6,000 RPS avg, 25,000 peak
Tokens/sec out:  25,000 × 400 tokens ÷ ~5s avg stream ≈ 2M tokens/sec
GPU memory:      70B model in FP8 ≈ 70 GB weights + KV cache
Per A100 (80GB): batch ~32-64 concurrent (continuous batching)
GPUs needed:     ~2M tok/s ÷ (A100 ~3k tok/s throughput) ≈ 700 GPUs (rough)
Storage:         500M req × 1KB conv metadata ≈ 500GB/day conv log
                 + embeddings cache, prompt cache
```

> **Key insight**: LLM serving is **GPU-bound and memory-bandwidth-bound**, not compute-bound in the FLOPS sense. The dominant cost is moving weights from HBM to SMs on every forward pass. This drives *every* optimization below.

---

## 4. High-Level Architecture

```
                    ┌──────────────────────────────────────────────┐
   User / SDK ─────▶│  API Gateway (auth, rate limit, billing)     │
                    │  TLS, WAF, request routing                   │
                    └───────────────┬──────────────────────────────┘
                                    │
                    ┌───────────────▼──────────────────────────────┐
                    │  LLM Router / Scheduler                      │
                    │  - model selection (small vs large tier)     │
                    │  - prompt-cache key lookup                   │
                    │  - routing to inference cluster by load      │
                    └───────┬───────────────┬──────────────────────┘
                            │               │
              ┌─────────────▼──┐   ┌────────▼────────────┐
              │ Small Model    │   │ Large Model Cluster │
              │ Cluster (8B)   │   │ (70B / MoE)         │
              │ vLLM / TGI     │   │ vLLM w/ tensor      │
              │ continuous     │   │ parallelism         │
              │ batching       │   │ across 2-8 GPUs     │
              └────────────────┘   └─────────────────────┘
                            │
              ┌─────────────▼──────────────────────────────────┐
              │ KV Cache / Prefix Cache (Redis)                │
              │ - shared prompt prefix reuse                   │
              │ - session embedding cache                      │
              └─────────────┬──────────────────────────────────┘
                            │
   ┌────────────────────────▼────────────────────────────────────┐
   │ Streaming Layer (SSE gateway, per-connection token buffer)  │
   │ → pushes tokens to client as generated                      │
   └─────────────────────────────────────────────────────────────┘
                            │
   ┌────────────────────────▼────────────────────────────────────┐
   │ Conversation Store (Postgres/Cassandra) + Usage Metering    │
   │ → async writes, usage counters → billing pipeline           │
   └─────────────────────────────────────────────────────────────┘
```

---

## 5. ML Architecture

### 5.1 Model Selection & Tiering

| Tier | Use Case | Example Models | Hardware |
|---|---|---|---|
| **Fast (small)** | Drafting, simple Q&A, autocomplete, routing | 8B-class (Llama 3 8B, Qwen2.5-7B) | 1 GPU / instance |
| **Smart (large)** | Reasoning, coding, long-context tasks | 70B / MoE (Mixtral 8x22B) | 2-8 GPUs (tensor parallel) |
| **Draft + Verify** | Speculative decoding for large models | small draft model + large target | 1+8 GPUs |

**Speculative decoding** is critical for large models: a small *draft* model proposes K tokens cheaply; the large *target* model verifies them in a single forward pass. Accepted tokens come at the cost of the small model; rejected ones fall back to one big-model step. Net effect: 2-3× throughput on the expensive GPU at near-zero quality loss.

### 5.2 Inference Serving Stack

```
┌─────────────────────────────────────────────────────────────┐
│ Serving Layer (vLLM / TGI / Triton)                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Continuous Batching Engine                              │ │
│ │  - requests join/leave the active batch dynamically     │ │
│ │  - no static batch size; maximizes GPU utilization      │ │
│ │  - iteration-level scheduling                           │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌──────────────────┐  ┌────────────────────────────────┐   │
│ │ PagedAttention   │  │ Prefix Caching                 │   │
│ │ - KV cache in    │  │ - cache system prompt + few-   │   │
│ │   virtual blocks │  │   shot examples shared across  │   │
│ │ - eliminates     │  │   requests → avoids recompute  │   │
│ │   fragmentation  │  │                                │   │
│ └──────────────────┘  └────────────────────────────────┘   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Quantization: FP8 / INT8 weights (AWQ/GPTQ)             │ │
│ │ → halves memory, ~1.5-2× throughput, minimal quality hit│ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 KV Cache Management

The **attention KV cache** is the largest single memory consumer at inference time. For a 70B model with 64k context:
- KV cache ≈ `2 × layers × seq_len × hidden_dim × dtype_bytes`.
- 64k context, FP8 → ~**32-40 GB per request** of KV state alone.

**PagedAttention (vLLM)** manages KV cache in fixed-size virtual blocks (like OS virtual memory pages), eliminating fragmentation and enabling memory sharing across requests with identical prefixes (e.g., shared system prompt).

### 5.4 Training Pipeline (offline, not on request path)

```
Data Collection ──▶ Pretrain / Continue-Pretrain ──▶ SFT ──▶ RLHF/DPO ──▶ Eval ──▶ Deploy
(human + synth)     (weeks, 1000s GPUs)              (days)  (days)       (gates)   (canary)
```
- We *serve* pretrained+aligned models; training is an offline concern in this design. Focus on inference.

---

## 6. Streaming & Token Delivery

```
Client ──POST /v1/chat/completions (stream:true)──▶ API Gateway
                                                        │
                                     ┌──────────────────▼────────────────┐
                                     │ Router assigns request to a GPU   │
                                     │ worker; opens SSE channel         │
                                     └──────────────────┬────────────────┘
                                                        │
   ┌────────────────────────────────────────────────────▼───────────────────────┐
   │  Per-token loop (autoregressive decode):                                    │
   │   for each step:                                                            │
   │     1. forward pass produces next-token logits                              │
   │     2. sample (temperature/top-p) → token id                                │
   │     3. decode token → text fragment                                         │
   │     4. SSE: data: {"choices":[{"delta":{"content":"Hel"}}]}\n\n           │
   │     5. flush to client socket                                               │
   │   until EOS or max_tokens                                                   │
   └─────────────────────────────────────────────────────────────────────────────┘
                                                        │
   Client ◀── SSE chunks (incremental deltas) ────── SSE gateway
```

**Why streaming matters:** A 400-token answer at non-streamed p50 3s feels broken. Streaming first token at p99 < 1.5s + 30ms/token **feels** instant even though total time is identical. Perceived latency ≈ TTFT; total latency is hidden by progressive display.

---

## 7. Prompt & Conversation Management

```
┌──────────────────────────────────────────────────────────────┐
│ Conversation Store (Cassandra / Postgres)                    │
│  session_id, turn_idx, role, content, tokens, model, ts      │
│  - append-only turn log, TTL 90 days                         │
│  - secondary index by user_id for listing sessions           │
└──────────────────┬───────────────────────────────────────────┘
                   │ on each new request:
                   ▼
   Reconstruct context window = system_prompt + last N turns + new_user_msg
   (truncate oldest turns if exceeds model context limit)
                   │
                   ▼
   Compute prefix-cache key = hash(system_prompt + canonical history prefix)
   → Redis lookup: if hit, skip prefill on that prefix
```

**Conversation memory strategies:**
- **Full window**: pass all turns up to context limit (simple, expensive).
- **Summarization**: compress old turns into a summary every K turns (cheap, lossy).
- **Retrieval over history**: embed each turn, retrieve top-k relevant at query time (hybrid, best for very long sessions).
- **Sliding window + summary**: keep last N turns raw + rolling summary of older (most common production default).

---

## 8. API Design

### REST (OpenAI-compatible)

```http
POST /v1/chat/completions
Authorization: Bearer <key>
Content-Type: application/json

{
  "model": "large-v2",
  "messages": [
    {"role":"system","content":"You are a helpful assistant."},
    {"role":"user","content":"Explain transformers."}
  ],
  "temperature": 0.7,
  "max_tokens": 500,
  "stream": true,
  "tools": [ ... ]           // optional function calling
}
```

**Streaming response** (SSE):
```
data: {"id":"...","choices":[{"delta":{"role":"assistant"}}]}

data: {"choices":[{"delta":{"content":"Transformers"}}]}

data: {"choices":[{"delta":{"content":" are"}}]}

data: [DONE]
```

### Key endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/chat/completions` | Streaming/non-streaming completion |
| POST | `/v1/completions` | Legacy text completion |
| GET | `/v1/models` | List available models + pricing |
| GET | `/v1/conversations` | List user sessions |
| GET | `/v1/conversations/{id}` | Fetch full history |
| DELETE | `/v1/conversations/{id}` | Delete session |
| GET | `/v1/usage` | Token usage / billing |

---

## 9. Load Balancing GPU Workloads

```
                    ┌─────────────────────────────┐
   Incoming req ───▶│  LLM-Aware Load Balancer    │
                    │  routing signals:           │
                    │   - GPU mem headroom        │
                    │   - queue depth (KV slots)  │
                    │   - prefix-cache affinity   │
                    │   - model tier match        │
                    └──┬───────┬───────┬──────────┘
                       │       │       │
                 ┌─────▼─┐  ┌──▼──┐  ┌─▼────┐
                 │ GPU   │  │ GPU │  │ GPU  │
                 │ pod A │  │pod B│  │pod C │
                 │(70B)  │  │(70B)│  │(8B)  │
                 └───────┘  └─────┘  └──────┘
```

**Routing strategies:**
1. **Least-loaded by KV-cache occupancy** — not just connection count. A GPU with free HBM for more KV slots can absorb more.
2. **Prefix-cache affinity** — route requests sharing the same system prompt / conversation to the same replica to reuse cached prefill.
3. **Model-tier routing** — classifier or heuristic decides small vs large model; route accordingly.
4. **Queue-aware backpressure** — if all workers saturated, return HTTP 429 with `Retry-After`; never queue unboundedly (OOM risk).

---

## 10. Scaling ML Inference (Deep Dive)

### 10.1 Continuous Batching vs Static Batching
- **Static**: wait for N requests, run together → wastes GPU when requests finish at different times.
- **Continuous (iteration-level)**: each decode step, the engine re-batches whatever requests are active. New requests join mid-stream; finished ones leave. **vLLM, TGI, and Triton all support this.**

### 10.2 Parallelism Strategies
```
For models too large for one GPU (70B / MoE):

Tensor Parallelism (TP):     Pipeline Parallelism (PP):
 split each layer across GPUs split layers across GPUs
 ┌─────┬─────┐                ┌─────┐  ┌─────┐
 │GPU0 │GPU1 │  all-to-all     │L0-15│→ │L16-31│→ ...
 │     │     │  comm per layer │GPU0 │  │GPU1 │
 └─────┴─────┘                └─────┘  └─────┘
 low latency, high comm       higher latency (bubbles),
                              less comm
```
- **TP** preferred for low-latency within a node (NVLink).
- **PP** used to scale across nodes (slower interconnect) — 2-3 stage pipelines common.
- **Expert parallelism** for MoE: route tokens to the GPU holding the relevant expert.

### 10.3 Quantization
| Format | Memory | Throughput | Quality | Use when |
|---|---|---|---|---|
| FP16/BF16 | 1× (baseline) | 1× | best | Quality-critical, ample GPUs |
| FP8 (W8A8) | 0.5× | ~1.7× | ~99% | Default production choice |
| INT4 (AWQ/GPTQ) | 0.25× | ~2-3× | ~95-98% | Throughput tier / edge |

### 10.4 Prefix Caching & Prompt Caching
- System prompt + few-shot examples are often identical across millions of requests.
- Cache the **prefill KV** for these prefixes in a shared Redis; a request reusing a cached prefix skips the expensive prefill (the dominant cost for long prompts).
- Commercial implementations: Anthropic prompt caching, OpenAI cached system messages.

### 10.5 Speculative Decoding (recap)
- Draft model generates K candidate tokens (cheap, on small GPU).
- Target model verifies all K in one forward pass (tree attention).
- Accept all matching tokens; resample at first mismatch.
- **2-3× latency reduction** on the expensive target GPU, quality-neutral.

### 10.6 Autoscaling Signal
Don't scale on CPU/RAM. Scale on:
- **KV-cache utilization** (% of KV blocks allocated).
- **Request queue depth** above threshold for > 30s.
- **TTFT SLO burn rate** (if p99 TTFT > target, add replicas).

---

## 11. Data & Observability Pipeline

```
Request ──▶ Token log (async) ──▶ Kafka ──▶ Usage Aggregator ──▶ Billing
                │                              │
                ├──▶ Prompt/Response Audit ──▶ Safety classifier (offline)
                │                              │
                └──▶ Metrics: TTFT, tok/s, GPU util, cache hit rate
                          → Prometheus → Grafana / dashboards
```

**Key SLOs / metrics to track:**
- TTFT p50/p99, inter-token latency p99, end-to-end latency.
- GPU utilization %, KV-cache occupancy, batch size distribution.
- Prefix-cache hit rate, speculative-decoding acceptance rate.
- 429 rate, OOM kills, queue wait time.

---

## 12. Bottlenecks & Mitigations

| Bottleneck | Symptom | Fix |
|---|---|---|
| **Prefill latency** (long prompts) | High TTFT on 8k+ token prompts | Prefix caching, prompt compression, chunked prefill |
| **GPU memory (KV cache)** | OOM, low batch concurrency | PagedAttention, quantization, limit max context |
| **GPU cost** | $/token too high | Speculative decoding, INT4 tier, request routing to smallest sufficient model |
| **Network egress** (streaming) | High bandwidth for 25k SSE streams | Compression (gzip/brotli on SSE), co-locate gateway |
| **Cold start** (new replica loads weights) | 30-60s startup, slow autoscale | Pre-warm pools, keep weights in RAM disk, image with embedded weights |
| **Tail latency** | p99 >> p50 (noisy neighbor) | Dedicated tenant isolation, request priorities, admission control |
| **Weight loading** across nodes | TP/PP startup delay | RDMA / GPUDirect, shared model store on fast NVMe |

---

## 13. Failure & Resilience

- **GPU pod crash**: router detects via health check, fails over to healthy pod; client reconnects SSE with `last-event-id` to resume.
- **Redis (KV cache) loss**: graceful degradation — requests recompute prefill, latency spike but no outage.
- **Cassandra unavailability**: conversation writes buffered in Kafka, drained on recovery; reads fail soft.
- **Region failover**: multi-region active-active for API + read replicas; inference clusters in 2-3 regions.

---

## 14. Security & Compliance
- **Prompt injection**: input/output safety classifiers in pipeline; system prompt isolation.
- **PII / data residency**: per-tenant region pinning; no cross-tenant training on conversation data.
- **Rate limiting & abuse**: per-key token-budget rate limiter; anomalous usage detection.
- **Model output filtering**: secondary classifier on completions before delivery.

---

## 15. Cost Optimization Summary
1. Route to the smallest model that meets quality bar (classifier-gated tiering).
2. Quantize everywhere FP16 isn't strictly needed.
3. Prefix-cache aggressively (shared system prompts → huge prefill savings).
4. Speculative decoding on large-model tier.
5. Continuous batching to keep GPU occupancy > 70%.
6. Spot/preemptible GPU pools for batch (non-real-time) workloads.

---

## 16. Interview Q&A

**Q1: How do you handle a request that needs a 128k-token context?**
A: First, ensure the serving engine supports it (vLLM PagedAttention handles long contexts). Prefill is the cost — use **chunked prefill** (process prompt in chunks interleaved with decode steps to avoid starving active sessions) and **prefix caching** if the long prefix is reusable. Cap concurrent long-context sessions per GPU since each holds a large KV cache. Consider prompt compression / retrieval to shorten effective context.

**Q2: Why not just horizontally scale more GPUs?**
A: You can, but GPUs are the dominant cost — naive scaling destroys unit economics. Each optimization (continuous batching, prefix caching, quantization, speculative decoding, tier routing) multiplies the others. A well-tuned stack serves 5-10× more tokens/GPU than a naive one.

**Q3: How do you stream tokens efficiently to 25k concurrent clients?**
A: SSE over HTTP/2 (multiplexing). Each inference worker writes tokens to a per-connection buffer; a dedicated streaming gateway flushes to clients. The gateway handles backpressure (slow client → buffer → drop or pause generation). Keep the gateway co-located with workers to minimize internal hops.

**Q4: What's the difference between TTFT and per-token latency, and which matters more?**
A: TTFT = time to first token (dominated by prefill of the prompt). Per-token = inter-arrival during decode. For UX, **TTFT dominates perceived responsiveness**; users tolerate slow trickle if it starts fast. Optimize prefill (caching, chunking) for TTFT and decode batching for throughput.

**Q5: How do you do model upgrades with zero downtime?**
A: Blue-green / canary deployment. New model version loaded into a fresh replica pool; router shifts traffic canary (1% → 10% → 100%). KV cache is not portable across model versions, so cold prefill on cutover — accept temporary TTFT spike or run shadow traffic to prewarm. Conversation format must be backward-compatible.

**Q6: How would you reduce the cost of serving a 70B model?**
A: (1) FP8/INT4 quantization, (2) speculative decoding with an 8B draft, (3) route easy queries to an 8B model entirely, (4) aggressive prefix caching for shared system prompts, (5) continuous batching for high occupancy, (6) spot GPUs for async/batch workloads.

**Q7: How do you handle a traffic spike 5× over baseline?**
A: Autoscaling on queue depth + KV utilization adds replicas (pre-warmed pool reduces cold start). Admission control returns 429 with Retry-After for excess load to protect SLOs. Burst traffic routed to fast (small-model) tier. Multi-region overflow if a region saturates.

**Q8: How do you prevent one tenant's long-running request from starving others?**
A: Continuous batching already interleaves, but set per-request token budgets and priorities. Use fair-share scheduling at the batch level (don't let one request monopolize KV slots). Tenant isolation via dedicated pools for large enterprise customers.

**Q9: Where does speculative decoding break down?**
A: When the draft model and target model diverge (e.g., target is much stronger at reasoning/code), acceptance rate drops and you pay draft cost + full target cost. Also adds implementation complexity (tree attention). Best when draft and target are from the same model family.

**Q10: How do you store conversation history efficiently at scale?**
A: Append-only store (Cassandra) keyed by session_id, TTL 90 days. For context reconstruction, fetch last N turns. For very long sessions, summarize older turns and store summary + recent raw turns. Don't re-store the full context each turn — store deltas.

---

## 17. Summary Cheatsheet

```
TTFT optimization:     prefix cache → chunked prefill → small model for easy Qs
Throughput:            continuous batching + PagedAttention + quantization
Large model serving:   tensor parallelism (intra-node) + pipeline (inter-node)
Cost:                  tier routing + speculative decoding + spot for batch
Streaming:             SSE, gateway handles backpressure, co-locate w/ workers
State:                 append-only conversation store + TTL + summary for long sessions
Scaling signal:        KV-cache occupancy + queue depth + TTFT SLO burn rate
```

> **One-liner**: Design a GPU-efficient, continuously-batched, prefix-cached, tier-routed LLM serving system that streams tokens via SSE, scales on KV-cache utilization, and treats model inference as a memory-bandwidth-bound scheduling problem.
