# System Design: RAG System (Retrieval Augmented Generation)

> **Analogy**: Imagine a **research library with a smart librarian**. When you ask a question, the librarian doesn't answer from memory alone (that's the LLM, which can hallucinate). Instead she (1) understands your question, (2) searches the stacks using multiple methods — by topic, by exact phrase, by *meaning*, (3) gathers the most relevant pages, (4) re-reads them to pick the truly useful ones, then (5) composes an answer *citing those pages*. That's RAG: ground every answer in retrieved evidence.

---

## 1. Problem Statement

Design a RAG system that lets users ask natural-language questions over a **large, constantly-updating corpus** (company docs, PDFs, wikis, code, support tickets) and get accurate, cited answers powered by an LLM — without retraining the model for every new document.

**Scale assumptions:**
- Corpus: 10M documents, avg 10 pages each → ~100M pages, ~5B tokens.
- 100k documents added/updated daily.
- Query volume: 200 QPS average, 1k QPS peak.
- Latency: p95 end-to-end < 3s; retrieval p95 < 300ms.

---

## 2. Requirements

### Functional
- Ingest heterogeneous sources (PDF, HTML, Markdown, DOCX, Confluence, code).
- Answer natural-language questions grounded in the corpus, with citations.
- Support incremental updates (new/edited docs available to queries within minutes).
- Handle multi-turn follow-up questions using conversation context.
- Provide filters (date, source, department, ACL/security scope).

### Non-Functional
| Requirement | Target |
|---|---|
| Answer latency (p95) | < 3s |
| Retrieval recall@10 | > 90% (answer-bearing chunk in top 10) |
| Index freshness | New doc searchable < 5 min |
| Availability | 99.9% |
| Citation accuracy | > 95% claims traceable to cited chunk |

---

## 3. Why RAG? (vs Fine-tuning / Long-context)

| Approach | Pros | Cons |
|---|---|---|
| **Fine-tune on corpus** | Fast inference; knowledge "baked in" | Retrain on every update; no citations; hallucination risk; expensive |
| **Long-context (stuff all docs in prompt)** | Simple | 100M docs can't fit; cost ∝ context; no selectivity |
| **RAG** | Fresh, cited, selective, cheap per query | Retrieval quality is the bottleneck; pipeline complexity |

RAG wins for **large, changing, citation-required** knowledge bases. Fine-tuning is better for *style/format* adaptation, not *knowledge* injection.

---

## 4. High-Level Architecture

```
   ┌─────────────────────────── INGESTION (offline/async) ──────────────────────┐
   │                                                                            │
   │  Source Connectors ──▶ Doc Loader ──▶ Cleaner/Normalizer                   │
   │  (S3, DB, API, crawl)    (PDF/HTML     (strip boilerplate,                 │
   │                            parsers)        dedupe, lang detect)             │
   │                                          │                                 │
   │                                          ▼                                 │
   │                              ┌───────────────────────┐                      │
   │                              │ Chunker               │                      │
   │                              │ - semantic / sentence │                      │
   │                              │ - overlap windows     │                      │
   │                              │ - metadata attach     │                      │
   │                              └───────────┬───────────┘                      │
   │                                          ▼                                  │
   │                     ┌────────────────────────────────────┐                  │
   │                     │ Embedding Model (batch, GPU)       │                  │
   │                     │ text → 768/1536-dim vector         │                  |
   │                     └─────────────────┬──────────────────┘                  │
   │                                       ▼                                     │
   │            ┌────────────────┐   ┌───────────────┐   ┌──────────────┐        │
   │            │ Vector DB      │   │ Keyword Index │   │ Metadata DB  │        │
   │            │ (semantic)     │   │ (BM25/Elastic)│   │ (Postgres)   │        │
   │            └────────────────┘   └───────────────┘   └──────────────┘        │
   └────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────────── QUERY (online) ──────────────────────────────────┐
   │                                                                            │
   │  User Question                                                             │
   │       │                                                                    │
   │       ▼                                                                    │
   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐               │
   │  │ Query Rewrite│▶ │ HyDE /       │▶ │ Embed Query          │               │
   │  │ (LLM, expand)│  │ Multi-Query  │  │ (same embed model)   │               │
   │  └──────────────┘  └──────────────┘  └──────────┬───────────┘               │
   │                                                   │                         │
   │                    ┌──────────────────────────────┼───────────────┐         │
   │                    ▼                              ▼               ▼         │
   │              ┌──────────┐                 ┌──────────────┐  ┌─────────┐    │
   │              │ Vector   │                 │ BM25 /       │  │Metadata │    │
   │              │ Search   │                 │ Keyword      │  │Filter   │    │
   │              │ (top-50) │                 │ Search(top50)│  │(ACL,date)│   │
   │              └────┬─────┘                 └──────┬───────┘  └────┬────┘    │
   │                   │  fuse (RRF)                  │               │         │
   │                   └──────────────┬───────────────┘               │         │
   │                                  ▼                               │         │
   │                         ┌────────────────┐  ← apply filters ─────┘         │
   │                         │ Re-ranker       │  (cross-encoder, top-50→top-5) │
   │                         │ (GPU, ~50ms)    │                                │
   │                         └───────┬─────────┘                                │
   │                                 ▼                                          │
   │            ┌──────────────────────────────────────┐                        │
   │            │ Prompt Assembly                      │                        │
   │            │  system + retrieved chunks + query   │                        │
   │            │  + citation instructions             │                        │
   │            └─────────────────┬────────────────────┘                        │
   │                              ▼                                              │
   │                     ┌────────────────┐                                     │
   │                     │ LLM (streamed) │ → Answer + [citations]              │
   │                     └────────────────┘                                     │
   └────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Document Ingestion Pipeline

### 5.1 Loading & Normalization
- **Connectors**: S3, Google Drive, Confluence, Jira, web crawl, DB CDC.
- **Parsing**: unstructured.io / Apache Tika for PDF/DOCX; html2text for web; tree-sitter for code.
- **Cleaning**: remove nav/boilerplate (trafilatura), dedupe near-duplicates (MinHash), language detection, normalize whitespace/Unicode.

### 5.2 Chunking Strategy (critical for retrieval quality)
```
Bad chunking → retrieval fails even with great embed model.

Strategies:
 ┌─────────────────────────────────────────────────────────────────┐
 │ Fixed-size token window (e.g., 512 tokens, 50-token overlap)    │
 │  + simple, predictable                                          │
 │  - can split sentences/ideas mid-way                            │
 ├─────────────────────────────────────────────────────────────────┤
 │ Sentence/paragraph-aware (split on boundaries, merge to budget) │
 │  + preserves semantic units                                     │
 │  - variable chunk sizes                                         │
 ├─────────────────────────────────────────────────────────────────┤
 │ Document-structure-aware (split by headings/sections)           │
 │  + best for structured docs (wikis, manuals)                    │
 │  + preserves hierarchy in metadata                              │
 ├─────────────────────────────────────────────────────────────────┤
 │ Semantic chunking (embed sentences, split where similarity      │
 │  drops sharply)                                                 │
 │  + adapts to content shifts                                     │
 │  - compute-heavy at ingest                                      │
 └─────────────────────────────────────────────────────────────────┘
```
**Each chunk stores**: `chunk_id, doc_id, text, embedding, position, heading_path, source, acl, ts`.

### 5.3 Embedding Generation
- Model: text-embedding-3-large (OpenAI), BGE-large, E5-mistral, GTE (open) — 768–1536 dims.
- Batch embedding on GPU cluster; ~10k chunks/sec on a single A100 with batching.
- **Asymmetric**: many embed models have separate query/passage encoders (prefix "query:" / "passage:").

---

## 6. Vector Database Selection

| DB | Strength | When to pick |
|---|---|---|
| **Pinecone** | Managed, serverless, easy scale | Team wants zero ops |
| **Weaviate** | Hybrid built-in, modules (multi-modal) | Want hybrid + plugin ecosystem |
| **Qdrant** | Rust, fast, payload filtering, open-source | Self-hosted, filtering-heavy |
| **Milvus** | Massive scale (10B+ vectors), distributed | Very large corpus |
| **pgvector** (Postgres) | SQL, transactions, ACID + vectors | Smaller scale, want one DB |
| **Elasticsearch (dense_vector)** | Already running ES | Consolidate infra |

**Core operations:**
- `upsert(id, vector, payload)` — insert/update chunk.
- `search(query_vec, top_k, filter)` — ANN search with metadata filter.
- Index: **HNSW** (graph-based, fast query, higher memory) or **IVF-PQ/SQ** (quantized, lower memory, slightly lower recall).

**ANN tradeoff (HNSW params):**
- `M` (graph connectivity) ↑ → recall ↑, memory ↑.
- `ef_construction` ↑ → build quality ↑, build time ↑.
- `ef_search` ↑ → recall ↑, latency ↑.
- Typical: M=16, ef_construction=200, ef_search=100 → recall@10 ~98%, latency ~5-15ms.

---

##  + Keyword (BM25) Search

Pure vector search misses **exact-match** signals: product IDs, error codes, names, acronyms. Pure BM25 misses **semantic** matches (synonyms, paraphrases). **Hybrid** fuses both.

```
Vector search (semantic):    "how to reset password"
  → retrieves chunks about "credential recovery" (good semantic match)

BM25 search (lexical):       "error code ERR_4292"
  → retrieves chunks containing the literal code (exact match)

Fusion (Reciprocal Rank Fusion - RRF):
  score(d) = Σ 1 / (k + rank_i(d))   across all retrievers
  k ≈ 60 (dampens top ranks less aggressively)
  → combines ranked lists without needing score calibration
```

**Weighted fusion** (alpha blend) is an alternative when scores are comparable, but RRF is more robust across systems. Many production systems retrieve top-50 from each, fuse to top-50, then re-rank.

---

## 8. Re-ranking (The Quality Multiplier)

Retrieval (vector + BM25) is **bi-encoder**: query and passage encoded separately, similarity = dot product. Fast but shallow. **Re-ranking uses a cross-encoder**: query and passage concatenated, fed through a transformer that attends across both — far more accurate but ~100× slower.

```
Retrieval (bi-encoder):      cheap, top-50 in ~20ms
   query → [embed] ←·→ [embed] ← passage

Re-rank (cross-encoder):     expensive, top-50→top-5 in ~50ms
   [query + passage] → [cross-encoder] → relevance score
   (attend across both → deep interaction)
```

**Models**: Cohere Rerank, BGE-reranker, ms-marco-MiniLM. Re-ranking top-50→5 typically lifts answer accuracy by 10-20% over raw retrieval. This is often the single highest-ROI step in a RAG pipeline.

---

## 9. Query Understanding & Expansion

Users ask vague, poorly-phrased questions. Pre-process the query:

```
User: "does it support sso"

Step 1 — Query Rewrite (LLM, cheap/small model):
  → "Does [Product] support single sign-on (SSO) integration?"

Step 2 — Multi-query / Sub-questions (LLM):
  → "How to configure SSO in [Product]"
  → "Supported authentication methods in [Product]"
  → "SAML/OIDC setup for [Product]"

Step 3 — HyDE (Hypothetical Document Embedding):
  Generate a hypothetical ideal answer, embed THAT instead of the query:
  → hypo answer: "Yes, [Product] supports SSO via SAML 2.0 and OIDC..."
  → embed hypo answer → semantic search (matches real passages better)

Run retrieval for each expanded query; union/dedupe results before re-ranking.
```

These steps dramatically improve recall for ambiguous queries. Trade-off: +1 LLM call latency (~200-400ms). Use a small/fast model (8B) and cache common rewrites.

---

## 10. Generation & Citation

### Prompt Assembly
```
SYSTEM: You are a precise assistant. Answer ONLY using the provided context.
        If the context doesn't contain the answer, say "I don't have enough
        information." Cite sources as [1], [2] referencing the chunk IDs.

CONTEXT:
[1] (source: wiki/auth.md) [Product] supports SSO via SAML 2.0 and OIDC...
[2] (source: docs/config.md) To configure SSO, navigate to Settings > ...
[3] (source: docs/faq.md) ...

USER: does it support sso
```

### Citation enforcement
- Instruct the model to cite; verify post-hoc that cited chunk IDs exist and support the claim.
- **Attribution check**: re-encode the answer and check similarity to cited chunks; flag low-overlap answers.
- **Faithfulness classifier**: detect when the answer strays from context (hallucination guard).

---

## 11. Conversation / Multi-turn RAG

Problem: "it" in a follow-up ("how much *does it* cost?") has no standalone meaning.

```
Conversation history + new query
         │
         ▼
   Standalone Question Rewriter (LLM):
     history = ["does it support sso", "yes via saml"]
     new     = "how much does it cost"
     → "How much does SSO/SAML integration cost for [Product]?"
         │
         ▼
   Use rewritten query for retrieval + generation
   (pass full history to generator for natural flow)
```

---

## 12. Data Freshness & Incremental Updates

```
Document change event (CMS webhook / CDC / cron diff)
   │
   ▼
Re-chunk changed doc → re-embed changed chunks → upsert to vector DB
   │                                          → update BM25 index
   │
   ▼
New doc searchable within minutes.
For deletes: tombstone chunks; periodic compaction.
Version chunks to support time-travel queries ("as of Q3 policy").
```

**Soft delete + tombstone** avoids immediate vector index rebuild (expensive). Background compaction merges tombstones out during low-traffic windows.

---

## 13. Security & Access Control (ACL)

Documents have access scopes (department, clearance, user-specific). Retrieval must **never** surface a chunk the user can't see.

```
Approaches:
1. Pre-filtering: vector search with metadata filter (acl ∈ user_groups)
   - Qdrant/Elasticsearch support this natively
   - can hurt ANN recall if filter is very selective

2. Post-filtering: retrieve top-K, then filter by ACL, re-fetch if too few remain
   - simpler, but may miss relevant chunks if filtered set is small

3. Tenant isolation: separate collection/index per tenant
   - strongest isolation, more operational overhead
```

Production default: **pre-filtering with over-fetch** (retrieve top-100, filter to allowed set, re-rank top-50→5).

---

## 14. Scaling & Performance

| Component | Bottleneck | Scale strategy |
|---|---|---|
| Embedding (ingest) | GPU throughput | Batch; async queue; scale GPU workers |
| Vector DB query | Memory + CPU | Sharding by doc partition; read replicas; HNSW in RAM |
| BM25 (Elasticsearch) | CPU + disk I/O | Shards + replicas; warm caches |
| Re-ranker | GPU | Batch top-50 cross-encoder calls; dedicated GPU pool |
| LLM generation | GPU (prefill of context) | Same as LLM service design (prefix cache system+context) |

**Latency budget (p95):**
```
Query rewrite:        150ms  (small LLM)
Embed query:           20ms
Vector + BM25 search:  40ms  (parallel)
Fusion + filter:       10ms
Re-rank top-50:        60ms  (GPU cross-encoder)
Prompt assembly:        5ms
LLM first token:      600ms  (prefill ~3k context)
LLM streaming:       ~1.5s   (300 tokens @ ~50ms inter-token)
────────────────────────────────
Total p95:          ~2.4s
```

---

## 15. Evaluation & Quality

RAG quality = retrieval quality × generation quality. Measure both.

```
Retrieval metrics:
  - Recall@k: is the gold chunk in top-k? (need labeled test set)
  - MRR / NDCG
  - Context relevance (LLM-as-judge: "does retrieved context address the query?")

Generation metrics:
  - Faithfulness: answer supported by context? (hallucination rate)
  - Answer relevance: does it address the question?
  - Citation accuracy: cited chunks actually support claims?

Eval harness:
  - Curated Q&A set (~500-1000) with gold answers + gold passages
  - Run nightly on pipeline changes
  - RAGAS / TruLens / LangSmith frameworks
  - A/B test changes against baseline before full rollout
```

---

## 16. Bottlenecks & Mitigations

| Bottleneck | Mitigation |
|---|---|
| **Bad chunking** kills retrieval | Semantic/structure-aware chunking; tune chunk size per doc type; eval harness |
| **Embedding model choice** underperforms | Benchmark (MTEB); consider domain-adapted/fine-tuned embed model |
| **Re-ranker latency** on GPU-poor setups | Distill cross-encoder; limit to top-30; cache common query reranks |
| **Vector DB memory** at 100M+ chunks | IVF-PQ quantization; sharding; tiered storage (hot in RAM, cold on disk) |
| **LLM context length** with many chunks | Re-rank to fewer, better chunks; summarize chunks before insertion |
| **Freshness** of fast-changing corpus | Streaming ingestion (Kafka → embed → upsert); soft-delete + compaction |
| **Hallucination** despite grounding | Faithfulness classifier; low-temperature generation; "I don't know" fallback |
| **Multi-tenant ACL** complexity | Pre-filter with over-fetch; tenant isolation for large enterprise tenants |

---

## 17. Advanced Patterns

- **Parent-child / small-to-big retrieval**: embed small chunks (precision), but return the parent section (context) to the LLM.
- **Graph RAG**: build a knowledge graph from the corpus; retrieve subgraphs for multi-hop reasoning.
- **Multi-modal RAG**: embed images/tables (CLIP, ColPali) alongside text.
- **Self-RAG / Corrective RAG**: LLM decides whether retrieval is needed, and whether retrieved context is sufficient; retrieves again if not.
- **Agentic RAG**: LLM iteratively searches, reads, and reasons across multiple retrieval rounds.

---

## 18. Interview Q&A

**Q1: Why not just fine-tune the LLM on all our documents?**
A: Fine-tuning teaches style/format, not reliable factual recall — it's prone to hallucination, can't cite sources, and requires retraining on every doc update (daily). RAG keeps knowledge external (fresh, citeable, filterable) and uses the LLM for reasoning/synthesis. Fine-tuning and RAG are complementary, not substitutes.

**Q2: How do you choose chunk size?**
A: Balance precision vs context. Too small → loses context, answer spread across chunks. Too large → dilutes relevance signal, fewer chunks fit in LLM context. Start at 256-512 tokens with overlap, measure recall@k on an eval set, tune per doc type (code vs prose vs tables). Use semantic/structure-aware splitting, not blind character counts.

**Q3: Vector search alone isn't finding exact error codes. Why?**
A: Embedding models compress semantics and lose exact lexical signal. Fix with **hybrid search**: combine vector (semantic) + BM25 (lexical) via Reciprocal Rank Fusion. BM25 catches exact matches; vectors catch synonyms/paraphrases.

**Q4: How do you handle a 500-page PDF?**
A: Parse → structure-aware chunk by section/heading → embed each chunk with position metadata. For retrieval, fetch relevant chunks; if answer needs broader context, use small-to-big (retrieve chunk, return parent section). Optionally generate a per-section summary at ingest for coarse retrieval first.

**Q5: What's the role of the re-ranker, and is it worth the latency?**
A: Retrieval (bi-encoder) is fast but shallow; re-ranker (cross-encoder) deeply compares query-passage pairs and is far more accurate. Re-ranking top-50→5 typically improves answer accuracy 10-20%. At ~50ms it's the highest-ROI quality step. Skip it only if latency budget is extremely tight.

**Q6: How do you keep the index fresh as docs change?**
A: Event-driven ingestion: CMS webhooks / DB CDC trigger re-chunking and re-embedding of changed docs, upserted to vector + BM25 indexes. Soft-delete stale chunks (tombstone), compact in background. Target < 5 min from edit to searchable.

**Q7: How do you prevent users from seeing documents they lack access to?**
A: Attach ACL metadata to every chunk. At query time, pre-filter vector search with `acl ∩ user_groups`. Over-fetch (top-100) then filter to compensate for selectivity. For strict isolation, separate collections per tenant.

**Q8: How do you evaluate if your RAG system is good?**
A: Curated eval set with gold passages + gold answers. Measure retrieval recall@k and generation faithfulness/relevance (RAGAS, LLM-as-judge). Run nightly regression on pipeline changes. A/B test in production with implicit feedback (thumbs up/down, follow-up rate).

**Q9: Query is ambiguous ("how to use it"). How do you improve retrieval?**
A: Query rewriting: use a small LLM to resolve pronouns against conversation history into a standalone query. Multi-query expansion: generate sub-questions, retrieve for each, union results. HyDE: generate a hypothetical answer and embed that. All improve recall for vague queries.

**Q10: How do you scale to 100M chunks?**
A: Shard vector DB by doc partition or tenant; use IVF-PQ quantization to fit in memory; read replicas for query load; separate hot (recent) and cold (archive) tiers. Batch embedding at ingest on GPU workers behind a queue. Re-rank only top-50 to bound GPU cost.

**Q11: What if the retrieved context doesn't contain the answer?**
A: The LLM should say "I don't have enough information" rather than hallucinate. Enforce via prompt + low temperature + faithfulness classifier. Optionally, a self-RAG loop: if confidence is low, retrieve again with a reformulated query, or escalate to a broader corpus/search.

---

## 19. Summary Cheatsheet

```
Ingest:    connectors → parse → clean → semantic chunk → embed (batch GPU) → vector+BM25+meta
Query:     rewrite/expand → embed → hybrid search (vec+BM25, RRF) → filter(ACL) → rerank → prompt → LLM
Quality:   chunking + hybrid search + reranking + query expansion + faithfulness checks
Scale:     shard vector DB, batch embed, GPU rerank pool, prefix-cache LLM context
Eval:      recall@k (retrieval) + faithfulness/relevance (generation), nightly regression
Freshness: event-driven ingest, soft-delete + compaction, <5 min to searchable
```

> **One-liner**: RAG grounds LLM answers in retrieved evidence — the system is a hybrid (vector + lexical) retrieval pipeline with query understanding, cross-encoder re-ranking, ACL-aware filtering, and a citation-enforcing generation step, where retrieval quality (chunking, embeddings, reranking) is the dominant success factor.
