# System Design: Real-time AI Search Engine

> **Analogy**: Imagine a **super-smart librarian who understands meaning**, not just keywords. You ask "that movie where the guy forgets everything" and she doesn't just grep for "guy" and "forget" — she *understands* you mean *Memento*, even though neither word appears in the index. She also fixes your typos, autocompletes as you type, knows what's trending *right now*, and reranks results by true relevance (not just keyword match). Behind her: a web crawler gathering every book, an inverted index for lightning-fast lookup, and semantic embeddings for meaning-based retrieval.

---

## 1. Problem Statement

Design an AI-powered search engine (Google/Bing-class, or enterprise search) that:
- Crawls and indexes billions of web pages (or documents).
- Answers queries with sub-second latency combining keyword and semantic matching.
- Understands query intent, autocompletes, and spell-corrects.
- Reranks results with a deep relevance model.
- Indexes breaking news in near-real-time.

**Scale assumptions:**
- Corpus: 50B+ web pages, ~100 PB of content.
- Queries: 10B queries/day, ~150k QPS average, ~500k QPS peak.
- Latency: p99 < 500ms for full results; < 50ms for autocomplete suggestions.

---

## 2. Requirements

### Functional
- Crawl, parse, and index web content continuously.
- Accept user query → return ranked, relevant results with title, URL, snippet.
- Provide autocomplete/suggestions as the user types.
- Spell-correct and understand query intent (transactional, informational, navigational).
- Index breaking news within seconds-to-minutes.
- Support semantic search ("movies like Inception") and direct answers (featured snippets).

### Non-Functional
| Requirement | Target |
|---|---|
| Query latency (p99) | < 500ms |
| Autocomplete latency | < 50ms |
| Index freshness (news) | < 60s |
| Availability | 99.99% |
| Result relevance (NDCG) | continuously improved |
| Recall | must find the relevant page among 50B |

---

## 3. Core Search Concepts

### 3.1 The Inverted Index (Foundation)
```
Forward index:  doc_id → [words in doc]      (slow for search)
Inverted index: word → [doc_ids containing it] (fast for search)

Structure:
  term → postings list
    "transformer" → [doc42:tf=3, doc108:tf=1, doc999:tf=5, ...]
    each posting: doc_id, term frequency, positions, payload

Posting lists are compressed (delta-encoded, varint) and fit on SSD.
Lookup = intersect/union posting lists for query terms.
```

### 3.2 BM25 Scoring (Lexical Relevance)
```
BM25(doc, query) = Σ_t IDF(t) · TF(t,d)·(k₁+1) / (TF(t,d) + k₁·(1 - b + b·|d|/avgdl))

Captures:
 - IDF(t): rare terms are more informative
 - TF saturation: term frequency saturates (diminishing return)
 - Document length normalization (longer docs penalized slightly)
k₁≈1.2, b≈0.75 are standard.
```

### 3.3 Semantic Search (Embeddings)
BM25 matches words; it can't match *meaning* ("film" vs "movie", "forgetful" vs "amnesia"). Semantic search embeds queries and docs into a vector space where meaning determines proximity.

```
Query:  "that movie where the guy forgets everything"
  - BM25:  looks for "movie", "guy", "forgets" → may miss pages about "amnesia films"
  - Semantic: embeds query meaning → matches pages about "memory loss cinema" → finds Memento

Doc embeddings pre-computed at index time, stored in vector index.
Query embedded at query time (~10ms), ANN search over doc vectors.
```

---

## 4. High-Level Architecture

```
┌─────────────────────── CRAWLING & INDEXING (offline) ───────────────────────┐
│                                                                             │
│  URL Frontier ──▶ Crawler Cluster ──▶ Page Fetcher ──▶ Parser/Extractor     │
│  (priority queue,  (thousands of         (HTTP,             (HTML→text,      │
│   politeness,       distributed          render JS)          boilerplate      │
│   freshness)        workers)                                 removal)         │
│                                                              │                │
│                           ┌──────────────────────────────────┘                │
│                           ▼                                                  │
│              ┌────────────────────────┐    ┌───────────────────────┐          │
│              │ Index Builder          │    │ Embedding Pipeline    │          │
│              │ - tokenize, stem, lem  │    │ - passage embed model │          │
│              │ - build inverted index │    │ - 50B docs → vectors  │          │
│              │ - BM25 stats           │    │ - batch GPU           │          │
│              │ - anchor text, links   │    └──────────┬────────────┘          │
│              └───────────┬────────────┘               │                       │
│                          │                            ▼                       │
│                          │               ┌──────────────────────┐             │
│                          │               │ Vector Index         │             │
│                          │               │ (FAISS / ScaNN,      │             │
│                          │               │  sharded, 50B vec)   │             │
│                          │               └──────────────────────┘             │
│                          ▼                                                    │
│              ┌────────────────────┐    ┌───────────────────────┐              │
│              │ Inverted Index     │    │ Link Graph / Rank     │              │
│              │ (sharded by term,  │    │ (PageRank, TrustRank, │              │
│              │  terabytes, SSD)   │    │  quality scores)      │              │
│              └────────────────────┘    └───────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────── QUERY (online) ──────────────────────────────────────┐
│                                                                             │
│  User Query ("best movie about memory loss")                                │
│       │                                                                     │
│       ├──▶ Autocomplete Service (Trie + trending, <50ms) [as they type]     │
│       │                                                                     │
│       ▼                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────────────────┐            │
│  │ Query        │   │ Spell        │   │ Query Understanding    │            │
│  │ Expansion    │   │ Correction   │   │ (intent: info/nav/    │            │
│  │ (synonyms,   │   │ (edit dist,  │   │  transactional;       │            │
│  │  related)    │   │  noisy chan) │   │  entity recognition)  │            │
│  └──────┬───────┘   └──────┬───────┘   └───────────┬───────────┘            │
│         └──────────────────┼───────────────────────┘                         │
│                            ▼                                                 │
│         ┌──────────────────────────────────────┐                             │
│         │ Embed Query (semantic, ~10ms)        │                             │
│         └──────────────────┬───────────────────┘                             │
│                            │                                                 │
│         ┌──────────────────┼──────────────────────────┐                      │
│         ▼                  ▼                          ▼                      │
│   ┌───────────┐     ┌──────────────┐          ┌──────────────┐               │
│   │ Inverted  │     │ Vector Index │          │ Knowledge    │               │
│   │ Index     │     │ (semantic    │          │ Graph /      │               │
│   │ (BM25,    │     │  ANN search) │          │ Entity       │               │
│  │  top-1k)   │     │ (top-1k)     │          │ Panel        │               │
│   └─────┬─────┘     └──────┬───────┘          └──────┬───────┘               │
│         │   fuse (RRF / weighted)                   │                        │
│         └──────────────┬───────────────────────────┘                        │
│                        ▼                                                     │
│              ┌─────────────────────┐                                         │
│              │ Re-ranker           │  (cross-encoder, deep relevance,        │
│              │ (top-1k → top-100)  │   query-doc interaction, ~100ms)        │
│              └──────────┬──────────┘                                         │
│                         ▼                                                     │
│              ┌─────────────────────┐                                         │
│              │ Final Ranking       │  (relevance × authority × freshness ×   │
│              │                     │   personalization × diversity)          │
│              └──────────┬──────────┘                                         │
│                         ▼                                                     │
│              Snippet Generation + Answer Extraction (featured snippet)       │
│                         │                                                     │
│                         ▼                                                     │
│                    Results Page                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Web Crawling

```
URL Frontier (priority queue):
  - Freshness: recrawl important/frequently-updated pages often
  - Politeness: respect robots.txt, rate limits per domain
  - Priority: high-quality/authoritative domains crawled more often
  - Seed + discovered links (from parsed pages' anchor text)

Crawler cluster:
  - Thousands of distributed workers (Scrapy, custom)
  - DNS cache, HTTP/2 connection pooling
  - JS rendering for SPAs (headless browser subset — expensive, selective)

Parsing / extraction:
  - HTML → clean text, title, headings, metadata
  - Boilerplate removal (Readability, trafilatura)
  - Extract structured data (JSON-LD, schema.org, Open Graph)
  - Detect language, duplicate/near-duplicate (SimHash)

Link graph:
  - Build directed graph of page → page links
  - Compute PageRank / authority scores (offline, periodic)
  - Anchor text = "free annotation" for target page (valuable signal)
```

---

## 6. Indexing

### 6.1 Inverted Index Construction
```
1. Tokenize text → terms (lowercase, stemming/lemmatization, stop words)
2. For each term, build postings list: (doc_id, tf, positions)
3. Sort by term → merge into index segments
4. Compress posting lists (delta encoding + varint/PFor)
5. Shard by term hash across hundreds of index nodes

Updates:
 - Build new segments incrementally (LSM-tree style)
 - Merge segments in background (compaction)
 - Delete via tombstones
```

### 6.2 Vector Index (Semantic)
```
- Passage-level embeddings (split docs into passages, embed each)
- 50B docs × ~20 passages = ~1T vectors (even at 100-dim → huge)
- Index: FAISS / ScaNN with IVF + PQ (product quantization) to fit in memory
- Sharded across thousands of nodes
- ANN search: query vector → top-1k passages in ~20ms
- Refresh: re-embed changed/new pages; streaming upsert for news
```

### 6.3 Real-Time Indexing (Breaking News)
```
News/refresh pipeline:
  High-priority crawl feed (RSS, news sitemaps, social signals)
     │
     ▼
  Fast-track parser + embedder (seconds)
     │
     ▼
  In-memory "real-time index" (separate from main index)
     │
     ▼
  Query merges main index + real-time index results

This gives <60s freshness for breaking news while the main index
(batch, TB-scale) rebuilds on a longer cycle.
```

---

## 7. Query Understanding

Before searching, the engine *understands* the query:

```
┌─────────────────────────────────────────────────────────────────┐
│ Query Understanding Pipeline                                    │
│                                                                 │
│ 1. Spell Correction                                             │
│    - Edit distance + noisy channel model + language model       │
│    - "restarant near me" → "restaurant near me"                 │
│    - Only correct if confident (don't "correct" valid queries)  │
│                                                                 │
│ 2. Query Expansion / Rewriting                                  │
│    - Synonyms (film → movie), related terms                     │
│    - LLM-based expansion: "best phone" → + "smartphone review"  │
│    - Query embedding finds semantically similar past queries    │
│                                                                 │
│ 3. Intent Classification                                        │
│    - Informational ("how do transformers work")                 │
│    - Navigational ("twitter login")                             │
│    - Transactional ("buy iphone 15")                            │
│    → routes to specialized verticals (shopping, news, images)   │
│                                                                 │
│ 4. Entity Recognition & Linking                                 │
│    - "Inception director" → Entity:Inception(film) → director   │
│    - Triggers Knowledge Graph panel / direct answer             │
│                                                                 │
│ 5. Personalization signals                                      │
│    - Location, language, search history, device                 │
│    - (With privacy controls / anonymization)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Retrieval: Hybrid Search

Combine lexical (BM25) and semantic (vector) retrieval, same fusion pattern as RAG:

```
Lexical (BM25):     fast, exact-match strong, term-aware
                   "ERR_4292" → exact code pages
                   weakness: synonyms, paraphrases

Semantic (Vector):  meaning-based, synonym/paraphrase strong
                   "forgetful movie" → amnesia/memory-loss films
                   weakness: exact entities, rare terms

Fusion (RRF):       score(d) = Σ 1/(k + rank_i(d)) across retrievers
                   combines ranked lists without score calibration

Result: top-1000 candidate passages from 50B docs in ~40ms.
```

---

## 9. Re-ranking with Cross-Encoder

Retrieval is fast but shallow (bi-encoder). The re-ranker is a **cross-encoder** that concatenates query + passage and produces a deep relevance score:

```
   [CLS] query tokens [SEP] passage tokens [SEP]
              │
              ▼
        Cross-Encoder (BERT/DistilBERT fine-tuned on relevance)
              │
              ▼
        relevance score (0-1)

Re-rank top-1000 → top-100.
~100ms on GPU with batching.
This is where most relevance quality comes from.
```

**Why not cross-encode all 50B docs?** Too slow (cross-encoder is ~100ms per pair). Hence the funnel: cheap retrieval narrows 50B → 1000, expensive cross-encoder refines 1000 → 100.

**Additional ranker features:**
- PageRank / authority score
- Freshness (recency boost for news queries)
- Click-through data (historical CTR for query-doc pairs)
- Location/personalization
- Content quality signals

---

## 10. Answer Extraction & Featured Snippets

```
For informational queries, extract a direct answer:

Query: "capital of France"
  → retrieve top passages
  → extractive QA model: "Paris" (highlight in source passage)
  → display as featured snippet with citation

For entity queries:
  → Knowledge Graph lookup (entity → attributes)
  → Entity panel (structured: capital, population, flag, ...)
```

---

## 11. Autocomplete / Typeahead

```
As user types "rest":
  │
  ▼
Autocomplete Service:
  1. Trie lookup (prefix "rest" → candidate completions) [in-memory, <5ms]
  2. Score candidates: historical query frequency × freshness × personalization
  3. Return top-10 suggestions

"rest" → ["restaurant near me", "restart", "restaurants", "rest api", ...]

Architecture:
 - Distributed Trie / prefix tree in Redis (sharded by prefix)
 - Popularity model updated from query logs (streaming)
 - Trending boost (spike detection on query stream)
 - Personalization (based on user's past queries)
 - p99 < 50ms (typed-ahead must feel instant)
```

---

## 12. Data Flow & Storage

```
Storage breakdown:
  Inverted index:    distributed, sharded by term, on SSD (terabytes)
  Vector index:      distributed, sharded, in-memory (FAISS/IVF-PQ)
  Link graph:        graph DB / specialized store (PageRank)
  Knowledge Graph:   RDF/property graph (entities + relations)
  Crawl cache:       object store (S3) for raw HTML (petabytes)
  Query logs:        columnar warehouse (BigQuery/Spark) for analytics & training
  Autocomplete Trie: Redis (sharded, in-memory)
```

---

## 13. Scaling

| Component | Scaling strategy |
|---|---|
| **Crawler** | Thousands of distributed workers; URL frontier sharded; async I/O |
| **Inverted index** | Shard by term hash; replicas for read throughput; segment compaction |
| **Vector index** | IVF-PQ quantization; shard by vector partition; thousands of nodes; in-memory |
| **Query serving** | Stateless frontend tier; cache common queries (with TTL); geo-distributed |
| **Re-ranker** | GPU pool; batch cross-encoder calls; model distillation for speed |
| **Autocomplete** | Redis cluster; sharded Trie; replicas |
| **Indexing** | MapReduce/Spark for batch builds; streaming for real-time news index |

**Caching** is critical at 500k QPS:
- Result cache: cache full result pages for common queries (minutes TTL).
- Per-user cache: recent results, personalization state.
- Negative cache: cache "no results" to avoid recompute.
- Embedding cache: query embeddings for repeated queries.

---

## 14. Latency Budget (p99 < 500ms)

```
Autocomplete (while typing): <50ms (Redis Trie)
Spell correct:               ~10ms
Query understanding:         ~20ms
Query embedding:             ~10ms
BM25 + Vector search (par):  ~40ms
Fusion:                      ~5ms
Cross-encoder re-rank (1k):  ~100ms
Final ranking + snippets:    ~30ms
Personalization/assembly:    ~10ms
Network:                     ~20ms
────────────────────────────────────
Total:                      ~245ms (margin for p99)
```

---

## 15. Bottlenecks & Mitigations

| Bottleneck | Mitigation |
|---|---|
| **Cross-encoder latency** (1k pairs) | Batch on GPU; distill to smaller model; limit to top-500; cache |
| **Vector index memory** (1T vectors) | IVF-PQ quantization; shard aggressively; tiered (hot in RAM, cold on disk) |
| **Index freshness vs scale** | Two-tier: batch main index + in-memory real-time news index |
| **Crawler politeness vs coverage** | Priority queue; adaptive recrawl frequency; distributed across domains |
| **Query understanding latency** | Cache query embeddings/re writes; small fast models; precompute for trending queries |
| **Personalization at 500k QPS** | Pre-compute user profiles (batch); cache; keep online personalization minimal |
| **Storage cost** (100PB crawl) | Compression; tiered storage; dedup; keep only parsed text + metadata hot |
| **Spam / low-quality results** | Quality classifiers; link-spam detection; human rater data; authority signals |

---

## 16. Interview Q&A

**Q1: How do you search 50B pages in <500ms?**
A: Multi-stage funnel. (1) Retrieval: inverted index (BM25) + vector index (semantic ANN) each return top-1000 candidates from 50B in ~40ms. Fusion combines them. (2) Cross-encoder re-ranks top-1000 → 100 in ~100ms. (3) Final ranking adds authority, freshness, personalization. Heavy sharding, caching, and approximate algorithms (ANN) keep it fast.

**Q2: Why combine BM25 and vector search?**
A: BM25 excels at exact lexical matches (product codes, names, rare terms) but misses synonyms/paraphrases. Vector (semantic) search catches meaning but can miss exact entities. Hybrid + RRF fusion gets both. Pure semantic also struggles with rare/out-of-vocabulary terms where BM25 shines.

**Q3: How does the cross-encoder re-ranker differ from the retrieval model?**
A: Retrieval is a bi-encoder (query and doc encoded separately, dot product) — fast but shallow. The cross-encoder concatenates query+doc and applies joint attention — far more accurate but ~100ms per pair. So we use bi-encoder to narrow 50B → 1000 cheaply, then cross-encoder to refine 1000 → 100 precisely.

**Q4: How do you index breaking news in under a minute?**
A: A separate high-priority pipeline: RSS/news sitemaps/social signals trigger fast-track crawling → parsing → embedding → into an in-memory real-time index (separate from the massive batch main index). Queries merge results from both. The main index rebuilds on a longer cycle; the real-time index provides freshness for news.

**Q5: How does autocomplete work at 500k QPS?**
A: Distributed Trie/prefix tree in sharded Redis. Prefix lookup in <5ms. Candidates scored by historical query frequency (from streaming query logs) × trending boost (spike detection) × personalization. p99 < 50ms. Replicated for read throughput.

**Q6: How do you handle spell correction without over-correcting?**
A: Noisy-channel model: P(correction|query) considering edit distance and language model probability. Only correct if confidence is high (don't "fix" valid rare words or entity names). Use search logs — if a "misspelling" consistently gets good results/clicks, don't correct it.

**Q7: How do you handle semantic search at 50B-doc scale?**
A: Passage-level embeddings (split docs into passages, embed each). Index in FAISS/ScaNN with IVF (clustering) + PQ (product quantization) to compress vectors and fit in memory. Shard across thousands of nodes. ANN search trades exactness for speed — recall@1000 ~98% at ~20ms.

**Q8: What role does the link graph play?**
A: PageRank and authority scores computed from the link graph are crucial ranking features — they capture page importance/authority independent of content. Anchor text from inbound links is "free annotation" describing the target page. Combined with content relevance, authority signals separate quality results from spam.

**Q9: How do you personalize at scale without violating privacy?**
A: Lightweight personalization signals (location, language, device) applied at final ranking. More aggressive personalization based on search history requires user consent and privacy controls. Use anonymized/aggregated signals where possible. Allow opt-out. Keep personalization computation cheap (pre-computed profiles, cached).

**Q10: How do you deal with spam and low-quality content?**
A: Multi-layer: (1) crawl-time filtering (known spam domains), (2) content quality classifiers (ML), (3) link-spam detection (link farms, unnatural patterns), (4) authority signals (PageRank, TrustRank), (5) user signals (dwell time, bounce), (6) human raters for training data and edge cases.

**Q11: How do you cache search results at scale?**
A: Multi-level: (1) full result-page cache for common queries (minutes TTL, invalidated by freshness signals), (2) query embedding cache (avoid re-embedding repeated queries), (3) per-user personalization cache, (4) negative cache for "no results." Caching handles a huge fraction of 500k QPS; only uncached queries hit the full pipeline.

**Q12: How do you evaluate relevance?**
A: (1) Offline: NDCG/MRR on human-labeled query-doc rating sets. (2) Online: click models, dwell time, satisfaction (result abandonment). (3) Human raters (Google's approach) following published guidelines. (4) A/B tests on subsets. Relevance is continuously improved via training data from these signals.

---

## 17. Summary Cheatsheet

```
Crawl & Index:  URL frontier → distributed crawl → parse → inverted index + vector index + link graph
Query pipeline: autocomplete → spell correct → query understand → embed → hybrid search (BM25+vec, RRF)
Re-rank:        cross-encoder (top-1k → top-100) → final rank (relevance × authority × freshness × personal)
Freshness:      separate real-time in-memory index for news, merged with batch main index at query time
Scale:          shard everything, IVF-PQ vector quantization, aggressive caching (result + embedding + user)
Autocomplete:   sharded Redis Trie, popularity × trending × personalization, p99 < 50ms
Eval:           NDCG (offline) + click/dwell (online) + human raters + A/B tests
```

> **One-liner**: An AI search engine is a multi-stage funnel — web crawling → inverted index + vector index → hybrid retrieval (BM25 + semantic ANN) → cross-encoder re-ranking → authority/freshness/personalization final rank — with real-time news indexing, sub-50ms autocomplete, and query understanding, all backed by massive sharding and caching to serve 50B-doc search at 500k QPS under 500ms.
