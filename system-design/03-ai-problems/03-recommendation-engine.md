# System Design: Recommendation Engine (Netflix / Spotify style)

> **Analogy**: Think of a **personal shopper who knows your taste**. When you walk in, she quickly scans the entire store (candidate generation) to find ~1000 things you *might* like, then carefully evaluates each (ranking) against your detailed taste profile, budget, and current mood, presenting only the top 20. She remembers what you bought, what you skipped, what you lingered on, and adjusts instantly. She also has strategies for brand-new customers (cold start) and new arrivals she's never sold before.

---

## 1. Problem Statement

Design a recommendation system for a streaming/media platform that:
- Personalizes the home feed, "for you" rails, and similar-item suggestions.
- Serves recommendations in real-time as user behavior updates.
- Handles new users and new items with no interaction history (cold start).
- Scales to hundreds of millions of users and tens of millions of items.

**Scale assumptions (Netflix/Spotify class):**
- 250M users, 50k movies/shows (Netflix) or 100M tracks (Spotify).
- 200M daily active users, avg 10 feed renders/day → 2B recommendation requests/day.
- ~25k RPS average, ~100k RPS peak.
- Latency: recommendation response p99 < 200ms (it's on the critical render path).

---

## 2. Requirements

### Functional
- Generate personalized rankings for feeds, rails, and detail-page "more like this."
- Update recommendations in near-real-time as the user interacts (watch, skip, like).
- Support contextual signals: time of day, device, location, session intent.
- Explain recommendations ("Because you watched X").
- Handle cold-start for new users and new items.

### Non-Functional
| Requirement | Target |
|---|---|
| Latency (p99) | < 200ms end-to-end |
| Throughput | 100k RPS |
| Coverage | > 95% of items get recommended (no rich-get-richer) |
| Diversity | Avoid feedback loops / filter bubbles |
| Availability | 99.95% (directly affects engagement) |

---

## 3. Recommendation Paradigms

| Paradigm | Idea | Strength | Weakness |
|---|---|---|---|
| **Collaborative Filtering (CF)** | "Users who liked X also liked Y" | Discovers taste patterns; no item content needed | Cold start; needs dense interaction matrix |
| **Content-Based (CB)** | "Recommend items similar to ones you liked (by features)" | Handles new items; explainable | Limited serendipity; over-specialization |
| **Hybrid** | Combine CF + CB + contextual | Best of all; production default | Complexity; many models to maintain |
| **Knowledge/Graph** | Item relationships via knowledge graph | Great for "similar" / multi-hop | Needs curated graph |

**Production reality**: almost all large-scale systems use a **hybrid, multi-stage funnel**: candidate generation (recall) → ranking (precision) → re-ranking (policy/diversity).

---

## 4. High-Level Architecture: Multi-Stage Funnel

```
                         User Request (feed / rail / detail page)
                                      │
                                      ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  Candidate Generation (RECALL — "get 1000 might-likes fast")    │
   │                                                                 │
   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
   │  │ Collaborative│  │ Content-Based│  │ Contextual / Trending│  │
   │  │ Filtering    │  │ (ANN over    │  │ (geo, time, popular, │  │
   │  │ (matrix fac /│  │  item emb)   │  │  new releases)       │  │
   │  │  two-tower)  │  │              │  │                      │  │
   │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
   │         │                 │                     │              │
   │         └─────────────────┼─────────────────────┘              │
   │                           ▼                                    │
   │              Union + Dedupe → ~500-1000 candidates             │
   └───────────────────────────┬─────────────────────────────────────┘
                               ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  Ranking (PRECISION — "score each candidate precisely")         │
   │                                                                 │
   │  Feature assembly (user feats + item feats + cross feats +      │
   │    context) from Feature Store                                  │
   │                           ▼                                     │
   │  ┌────────────────────────────────────┐                         │
   │  │ Ranking Model (DNN / GBDT / DLRM)  │ → per-candidate score   │
   │  │ trained on engagement objectives   │                         │
   │  └────────────────────────────────────┘                         │
   └───────────────────────────┬─────────────────────────────────────┘
                               ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  Re-ranking / Policy (POLISH — "apply business rules")          │
   │  - Diversity (don't show 10 action movies in a row)             │
   │  - Freshness (boost new releases)                               │
   │  - Fairness / exploration (explore-exploit, bandits)            │
   │  - Dedupe against recent history                                │
   │  - Filter already-watched, unavailable, age-restricted          │
   └───────────────────────────┬─────────────────────────────────────┘
                               ▼
                        Top-N Recommendations
                        (+ explanation metadata)
```

---

## 5. Candidate Generation (Deep Dive)

Goal: **maximize recall** (don't miss the item the user will love) at **low latency** (can't score 50M items per request).

### 5.1 Collaborative Filtering

**Matrix Factorization (classic, still used):**
```
Interactions matrix R (users × items), sparse.
Factorize: R ≈ U · V^T
  U: user latent factors (m × k)
  V: item latent factors (n × k)
  k ≈ 50-200 latent dimensions

User u's preference for item i ≈ dot(U[u], V[i])
```
Train via ALS (Alternating Least Squares) or SGD on observed interactions (implicit feedback: clicks, watches, skips weighted).

**Two-Tower / Dual Encoder (modern, neural CF):**
```
   User features ──▶ [User Tower (DNN)] ──▶ user_emb (256-d)
                                              │
                                              · (dot product)
                                              │
   Item features ──▶ [Item Tower (DNN)] ──▶ item_emb (256-d)

Train with sampled softmax / in-batch negative sampling.
Item embeddings pre-computed & indexed (ANN).
At serving: compute user_emb (fast), ANN search over item index.
```
Two-tower is the **industry standard** for candidate generation at scale (YouTube, Google, Pinterest) because item embeddings are precomputed and served via ANN.

### 5.2 Content-Based (Item Similarity)
- Embed items from metadata (genre, cast, tags, description via text encoder; poster via image encoder).
- User's profile = weighted combination of embeddings of items they liked.
- Retrieve via ANN items closest to user profile vector.

### 5.3 ANN Index for Retrieval
```
Index: FAISS / ScaNN / HNSW (same family as vector DB in RAG)
  - Item embeddings: 50M × 256-dim, stored in memory
  - Query: user_emb → top-1000 nearest items in ~5-15ms
  - Approximate but fast; recall@1000 ~99%

Multiple candidate generators run in parallel; results unioned.
```

### 5.4 Co-occurrence / Association Rules
- "Users who watched X also watched Y" — precomputed item-to-item maps (Jaccard / lift on co-watch graph).
- Cheap, explainable ("because you watched X"), great for "more like this" rails.

---

## 6. Ranking Model (Deep Dive)

Candidate generation is fast but coarse (dot-product score). Ranking is **expensive but precise** — it scores ~1000 candidates with rich features and a powerful model.

### 6.1 Feature Engineering

```
User features:          Item features:           Cross/Context features:
 - demographics         - genre, tags            - user×genre affinity
 - historical stats     - recency, popularity    - time of day × genre
 - avg watch time       - quality score          - device, location
 - signup age           - source                 - session position
 - taste vector         - price/tier             - impression count
                                                 - days since last rec

Real-time features (from Feature Store, <1s fresh):
 - items clicked in last hour
 - session intent (what they've browsed this session)
 - dwell time on current page
```

### 6.2 Model Choices
| Model | Strength | Use case |
|---|---|---|
| **GBDT** (XGBoost, LightGBM) | Strong on tabular, fast inference, interpretable | Workhorse ranker, great baseline |
| **DNN / DLRM** (Deep & Cross, DCN) | Learns complex interactions, embedding-heavy | Large-scale ranker (YouTube, Meta) |
| **Wide & Deep** | Memorization (wide) + generalization (deep) | Google Play recommendations |
| **Transformer sequential** (SASRec, BERT4Rec) | Models user behavior sequence | Session-based / next-item rec |

**Objective**: predict P(engagement) — watch, click, complete, like. Often **multi-task**: predict multiple objectives (click, watch, share) and combine scores.

### 6.3 Training Pipeline
```
Impression logs (what was shown) + outcome labels (click/watch/skip)
   │
   ▼
Feature Store joins (add user/item/context features at impression time)
   │
   ▼
Training data (billions of rows)
   │
   ▼
Train ranker (daily / multiple times per day)
   │
   ▼
Validate on holdout (AUC, NDCG, offline metrics)
   │
   ▼
Deploy (canary → ramp → full)
   │
   ▼
Online A/B test (north star: watch time, retention, CTR)
```

---

## 7. Feature Store (Real-time Personalization)

The feature store is the **bridge** between batch/streaming feature pipelines and online serving. It provides low-latency (<10ms) feature reads at request time.

```
   ┌──────────────────────────────────────────────────────────────┐
   │ OFFLINE (batch)                    │ ONLINE (serving)        │
   │                                   │                          │
   │ Spark / Flink jobs ──write────▶ Feature Store ◀──read── API   │
   │  compute:                        │  - Redis / DynamoDB       │
   │   - user_taste_vector            │    (low-latency online)   │
   │   - item_popularity_7d           │  - + historical store     │
   │   - genre_affinity               │    (Spark/BigQuery for    │
   │  cadence: hourly/daily           │     training joins)       │
   │                                   │                          │
   │ Streaming (Flink) ──write────▶    │  Point-in-time correctness│
   │   - clicks in last 5 min          │  (training uses features  │
   │   - session intent                │   as-of impression time,  │
   │   cadence: seconds                │   avoiding leakage)       │
   └──────────────────────────────────────────────────────────────┘
```

**Critical concept — point-in-time correctness**: when building training data, you must join features **as they were at impression time**, not current values, to avoid training-serving skew and data leakage.

---

## 8. Cold Start Problem

### New User (no history)
```
1. Onboarding survey (pick genres/artists) → seed taste vector
2. Demographic / geo priors (users like you)
3. Popular / trending globally and in region
4. Contextual bandit: explore diverse content, learn fast from first interactions
5. Within a few interactions, switch to personalized CF
```

### New Item (no interactions)
```
1. Content-based: embed from metadata, recommend to users whose taste matches
2. "Exploration" allocation: force-show new items to a sample of users to gather signal
3. Boost in re-ranking (freshness policy) for first 48h
4. Use item metadata priors (similar items' performance)
5. Once interactions accrue → CF models pick it up naturally
```

### Exploration-Exploitation
- Pure exploitation → feedback loops, "rich get richer," filter bubbles.
- Add exploration: multi-armed bandits (Thompson sampling, UCB) allocate a fraction of slots to uncertain items to gather feedback.
- **Determinantal Point Processes (DPP)** for diversity: mathematically select a set of items that are both relevant and diverse.

---

## 9. Real-Time Updates

Recommendations must reflect the user's *current session*, not just yesterday's batch model.

```
User action (click, watch, skip)
   │
   ▼
Event stream (Kafka)
   │
   ├──▶ Streaming feature updates (Flink) → Feature Store (Redis)
   │      updates: session_clicks, recent_genre, dwell_time, intent
   │
   ├──▶ Online model update (optional): update user embedding incrementally
   │      (e.g., two-tower: update user tower with recent items)
   │
   └──▶ Impression log (for next training cycle)
```

**Two levels of real-time:**
1. **Feature freshness** (seconds): session features in Redis updated live; ranker reads them.
2. **Model freshness** (hours): retrain/ramp ranker multiple times daily; candidate models refreshed daily.

---

## 10. Data Pipeline

```
   ┌──────────── INGESTION ────────────┐
   │ Events: impressions, clicks,      │
   │ watches, likes, skips, searches    │
   │ → Kafka (millions/sec)             │
   └───────────────┬───────────────────┘
                   ▼
   ┌──────────── PROCESSING ───────────┐
   │ Stream (Flink): real-time features │
   │ Batch (Spark): daily aggregates,   │
   │   model training data              │
   └───────────────┬───────────────────┘
                   ▼
   └──▶ Feature Store (Redis + offline) ──▶ Training ──▶ Model Registry
                                              │
                                              ▼
                                          Deploy to Serving
```

---

## 11. API / Serving Design

```
GET /recommendations?user_id=...&context={page,rail,device,geo}
   │
   ▼
Recommendation Service
   ├──▶ Fetch user features (Feature Store, ~5ms)
   ├──▶ Candidate generation (parallel, ~15ms)
   │      - CF (ANN over item index)
   │      - Content-based (ANN)
   │      - Trending/contextual
   ├──▶ Union + dedupe → ~1000 candidates
   ├──▶ Batch-score with ranker (feature fetch + model, ~30ms)
   ├──▶ Re-rank (diversity, policy, filters, ~5ms)
   └──▶ Return top-N + explanations
```

**Latency budget (p99 < 200ms):**
```
User feature fetch:     5ms
Candidate gen (x3 par): 15ms
Ranker feature fetch:  20ms
Ranker scoring (1000):  40ms   (batched inference on CPU/GPU)
Re-ranking + filters:   10ms
Network/overhead:       10ms
─────────────────────────────
Total:                ~100ms   (margin for p99)
```

---

## 12. Scaling ML Inference

| Challenge | Solution |
|---|---|
| **Ranker scoring 1000 candidates in <50ms** | Batch all candidates in one model call; use GBDT (fast CPU) or quantized DNN; model distillation |
| **Candidate ANN over 50M items** | In-memory HNSW / FAISS; shard by item partition; replica for read throughput |
| **100k RPS** | Stateless serving tier, horizontal autoscaling; cache common recommendations (short TTL) |
| **Feature Store hot reads** | Redis cluster, colocation with serving; pre-warm active users |
| **Model deployment** | Canary → ramp; shadow traffic for validation; instant rollback |

**Caching strategy:**
- Cache recommendation results per user with short TTL (60-300s).
- Invalidate on significant user action (click, watch) to force refresh.
- Pre-compute "default" recommendations for cold/anonymous users.

---

## 13. Metrics & Evaluation

### Offline
```
Retrieval:    Recall@k, NDCG (did the relevant item get retrieved?)
Ranking:      AUC, LogLoss, NDCG (did we order candidates well?)
```

### Online (what actually matters)
```
North-star:   Total watch time / session, retention (D7/D30), CTR
Guardrails:   Diversity, coverage (% items recommended), latency, cost
A/B testing:  Holdout group; measure lift vs control; guard against
              short-term metric gaming (e.g., clickbait ↑ CTR but ↓ watch time)
```

**Beware of Goodhart's Law**: optimizing CTR can promote clickbait. Always watch long-term metrics (retention, satisfaction) alongside short-term (CTR, watch).

---

## 14. Bottlenecks & Mitigations

| Bottleneck | Mitigation |
|---|---|
| **Candidate generation recall** | Multiple diverse generators (CF + content + graph); tune ANN params |
| **Ranker latency** (1000 items) | GBDT over DNN if latency tight; batch scoring; model distillation |
| **Feature Store read latency** | Redis cluster, colocation, pre-warm active users |
| **Training-serving skew** | Point-in-time feature joins; same feature definitions online & offline |
| **Cold start** (users & items) | Content-based + exploration + onboarding + freshness boost |
| **Feedback loops / filter bubbles** | Exploration (bandits), diversity (DPP), periodic retrain |
| **Data volume** (billions of impressions) | Columnar storage (Parquet), Spark, streaming (Flink) |
| **Model staleness** | Train multiple times/day; online feature freshness; canary deploy |

---

## 15. Interview Q&A

**Q1: Walk me through what happens when a user opens the app.**
A: (1) Recommendation service fetches user features from Feature Store (~5ms). (2) Candidate generators run in parallel — CF (ANN over item embeddings), content-based, trending/contextual — returning ~1000 candidates (~15ms). (3) Ranker scores all candidates using user+item+cross features (~40ms). (4) Re-ranking applies diversity, freshness, filters. (5) Top-N returned with explanations. Total ~100ms.

**Q2: Why a two-stage (candidate generation + ranking) funnel?**
A: Scoring 50M items per request is infeasible at 100k RPS. Candidate generation (cheap, ANN) narrows 50M → 1000 fast. Ranking (expensive, rich features) scores 1000 precisely. This balances recall (don't miss good items) with precision (order them well) at feasible latency/cost.

**Q3: How do you handle the cold start problem for a new user?**
A: Onboarding survey seeds initial taste; use demographic/geo priors ("users like you"); show popular/trending; employ contextual bandits to explore and learn quickly from first interactions. Within a few interactions, CF models engage. For new items: content-based rec from metadata + exploration allocation + freshness boost until interactions accrue.

**Q4: Collaborative filtering vs content-based — when to use which?**
A: CF discovers taste patterns from interactions (great when you have dense data) but suffers cold start. Content-based uses item features (handles new items, explainable) but over-specializes. Production systems use both: CF for personalization, content-based for cold start and "similar item" rails.

**Q5: How do you keep recommendations fresh in real-time?**
A: Two levels: (1) feature freshness — stream user actions (Kafka → Flink) into the Feature Store (Redis) so session features reflect the last few seconds; (2) model freshness — retrain ranker multiple times daily, refresh candidate models daily. The ranker reads real-time features at request time, so it "feels" current even between retrains.

**Q6: What's a feature store and why do you need it?**
A: A feature store provides consistent feature computation/serving between training and serving, with point-in-time correctness. It solves training-serving skew (same features online and offline) and provides low-latency reads (<10ms) for online serving while supporting batch joins for training. Examples: Feast, Tecton.

**Q7: How do you avoid feedback loops and filter bubbles?**
A: Exploration via multi-armed bandits (allocate slots to uncertain items). Diversity via DPP or simple de-duplication (don't show 10 similar items). Periodic full retrain to avoid drift. Monitor coverage (% of catalog recommended) and diversity metrics as guardrails.

**Q8: How do you scale the candidate generation ANN search?**
A: Pre-compute item embeddings (two-tower item tower), index in FAISS/ScaNN/HNSW in memory. Shard by item partition if 50M+ items. Read replicas for query throughput. ANN is approximate but recall@1000 ~99%, latency ~10ms.

**Q9: What metrics do you optimize, and what are the pitfalls?**
A: Offline: recall@k (retrieval), AUC/NDCG (ranking). But offline metrics are proxies — the north star is online engagement (watch time, retention). Pitfall: optimizing CTR alone promotes clickbait (Goodhart's Law). Always guardrail with long-term metrics and diversity/coverage.

**Q10: How would you design "because you watched X" recommendations?**
A: Co-occurrence / item-to-item similarity. Precompute item-item affinity (Jaccard/lift on co-watch graph, or cosine similarity of item embeddings). At serving, look up the seed item's top-k similar items, merge into candidate set, rank, and attach the explanation metadata.

**Q11: How do you handle multi-objective ranking (click vs watch vs share)?**
A: Multi-task ranker with shared bottom layers and task-specific heads predicting P(click), P(watch), P(share). Combine into a final score via weighted sum (weights tunable per surface). Weights reflect business priorities (e.g., watch time valued over raw clicks).

**Q12: How do you measure training-serving skew? |
A: Log features at serving time alongside predictions; compare against training-pipeline features for the same impression. Track distribution drift. Use the feature store to guarantee identical computation. Skew manifests as offline metrics >> online metrics.

---

## 16. Summary Cheatsheet

```
Funnel:        candidate gen (recall, ANN, ~1000) → ranking (precision, rich feats) → re-rank (policy/diversity)
Candidate gen: two-tower CF (ANN), content-based, co-occurrence, trending — run in parallel, union
Ranking:       GBDT/DNN with user+item+cross+context features, multi-task objectives
Real-time:     Kafka→Flink→FeatureStore(Redis) for session features; retrain ranker 2-4×/day
Cold start:    onboarding + content-based + bandit exploration + freshness boost
Scale:         in-memory ANN (sharded), batch ranker scoring, stateless serving + cache, GBDT for latency
Eval:          offline (recall@k, NDCG) + online A/B (watch time, retention) + diversity/coverage guardrails
Pitfall:       Goodhart's Law — don't over-optimize CTR; watch long-term + guardrail metrics
```

> **One-liner**: A production recommendation engine is a multi-stage funnel — fast ANN candidate generation (two-tower CF + content-based) feeding a rich-feature ranking model (GBDT/DNN) feeding a policy/diversity re-ranker — with a real-time feature store powering sub-200ms personalized responses, multi-armed-bandit exploration for cold start, and online A/B testing as the source of truth.
