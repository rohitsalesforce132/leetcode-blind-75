# Alex Xu Vol.1 — Chapters 13–15: Large-Scale Application Deep Dives

> **Scope:** A detailed deep-dive analysis of three of the most iconic "large-scale app" interview questions from Alex Xu's *System Design Interview — An Insider's Guide (Vol.1)*:
> - **Ch.13** — Design a Search Autocomplete System (typeahead / "top-k")
> - **Ch.14** — Design YouTube (video sharing & streaming)
> - **Ch.15** — Design Google Drive (cloud file storage & sync)
>
> For each chapter we cover: problem framing, back-of-the-envelope estimation, high-level architecture (with ASCII diagrams), detailed component design, database schema, API design, scaling bottlenecks & solutions, the specific technologies that make it work, trade-offs, and 5 interview Q&A.

## Key Numbers to Memorize

These are the headline figures that come up repeatedly in interviews. Internalize them so you can recite them without looking.

| System | Headline number | What it tells you |
|---|---|---|
| Autocomplete | **~24k QPS read, ~0.4 GB/day write** | Read-heavy; batch the writes. |
| Autocomplete | **<100 ms response SLA** (Facebook typeahead) | Forces in-memory trie; no DB on hot path. |
| Autocomplete | **top-5, weekly rebuild** | Sticky popularity → staleness is tolerable. |
| YouTube | **150 TB/day upload storage** | Object storage, not block; shard by video. |
| YouTube | **~$150k/day CDN egress** ($0.02/GB) | Egress is the dominant cost; long-tail optimization is mandatory. |
| YouTube | **~7.5 PB/day streamed** | Bandwidth-heavy, not compute-heavy. |
| YouTube | **max 1 GB/upload, ~300 MB avg** | GOP-chunked resumable upload needed. |
| Google Drive | **500 PB allocated** (50M × 10 GB) | Provisioned vs. realized storage distinction matters. |
| Google Drive | **~240 upload QPS** | Low QPS, high coordination complexity per write. |
| Google Drive | **4 MB max block** (Dropbox reference) | Delta sync + de-dup granularity. |
| Google Drive | **>1M long-poll connections/server** (Dropbox 2012) | Reconnect storm is the real failure risk. |

**Rule of thumb across all three:** if you can quote the *order of magnitude* (PB vs. TB vs. GB; 10k vs. 100 QPS; cents/GB vs. dollars/GB) and tie it back to a design decision, you'll sound like someone who has actually built systems, not just memorized a book.

---

# Chapter 13 — Design a Search Autocomplete System

> **Analogy:** A librarian who has memorized the most popular book titles. As soon as you say the first letter, she already knows the 5 books people ask about most that start with that letter — and she updates her memory every night based on the day's requests.

Also known as **typeahead**, **search-as-you-type**, or **"design top-k"**. As the user types in a search box, the system returns the **top-k (5) most-popular matching queries** in real time.

## 13.1 Problem Statement & Requirements

### Clarifying Q&A (the conversation that scopes the problem)
| Candidate question | Interviewer answer |
|---|---|
| Match at beginning only, or anywhere? | **Prefix match only** (beginning of query) |
| How many suggestions? | **5** |
| How are they ranked? | By **historical query frequency** (popularity) |
| Spell check? | **No** |
| Language? | English (multi-language = follow-up) |
| Case / special chars? | All **lowercase alphabetic** |
| Scale? | **10 million DAU** |

### Functional Requirements
- Given a typed prefix, return the **top-5 most-frequent** completed queries.
- The ranking signal is **historical query frequency** (aggregate count).
- The set of candidate queries is updated as users type new queries.

### Non-Functional Requirements
- **Fast response time:** results must appear within **~100 ms** (Facebook's published threshold for typeahead) or the UI stutters.
- **Relevant:** suggestions must match the prefix.
- **Sorted:** by popularity (or a richer ranking model later).
- **Scalable:** handle very high read QPS (~tens of thousands per second).
- **Highly available:** the autocomplete box must keep working even if parts of the backend degrade.

## 13.2 Back-of-the-Envelope Estimation

Assumptions (English, lowercase):
- **10 M DAU**, **10 searches/user/day** → 100 M searches/day.
- **20 bytes/query** (4 words × 5 chars × 1 byte ASCII).
- For each character typed the client fires a request; a typical query is typed in ~6 keystrokes, but the book uses **20 requests per search** as a generous average (long queries + typing dynamics).
- **20% of queries are new** each day.

| Metric | Calculation | Value |
|---|---|---|
| Avg QPS | 10M × 10 × 20 / 86400 | **~24,000 QPS** |
| Peak QPS | QPS × 2 | **~48,000 QPS** |
| Daily new data | 10M × 10 × 20 B × 20% | **~0.4 GB/day** |

**Key insight:** this is a **read-heavy** system (QPS in the tens of thousands) writing a comparatively tiny amount of new signal data (~0.4 GB/day). The hot path is reads; writes can be batched/offline.

**Sanity check on the 24k QPS.** A single modest API server handles ~5–10k RPS of trivial lookups; with the trie cached in memory the per-request work is microseconds. So 24k avg / 48k peak QPS needs only **5–10 API server instances** behind a load balancer — very manageable. The real constraint isn't CPU, it's keeping the trie **in RAM** across the fleet and keeping the cache warm. At ~0.4 GB/day of new data, even a year of history is only ~150 GB before compression/de-dup — fits comfortably in a sharded Redis cluster.

## 13.3 High-Level Architecture (naïve first pass)

Two services:
1. **Data gathering service** — counts queries, updates a `frequency` table.
2. **Query service** — given a prefix, returns top-5 from that table.

```
            ┌──────────────┐   write    ┌────────────────────┐
  Users ──▶ │ Data Gather  │ ─────────▶ │ Frequency Table    │
            │ Service      │            │ (query, frequency) │
            └──────────────┘            └─────────┬──────────┘
                                                  │ SELECT query, freq
                                                  │ FROM t
            ┌──────────────┐   prefix             │ WHERE query LIKE 'tw%'
  Users ──▶ │ Query Service│ ◀────────── ─────────┘ ORDER BY freq DESC
            └──────────────┘                       LIMIT 5
```

This works at small scale, but `LIKE 'prefix%'` + `ORDER BY` over billions of rows is **O(n log n)** per request — far too slow for 24k QPS. The deep dive fixes this with a **Trie**.

## 13.4 Detailed Component Design

### 13.4.1 The Trie (prefix tree) — the heart of the system

A **trie** compactly stores strings so that all strings sharing a prefix share a path from the root.

**Basic trie properties**
- Root = empty string.
- Each node holds **one character** and up to 26 children (one per letter).
- A node where a complete query ends is marked (e.g. thicker border).

**Augmented trie (the version we need):** each node also stores the **top-5 queries** that pass through it. This trades **space for time** — the central optimization of the whole chapter.

```
                 root
                 /
                t
               / \
              r   w
             /|   |
            e y   i
           /|     |
         e ...    n
        (best:35, bet:29, bee:20, be:15, beer:10)
```

**Worked example.** Suppose the frequency table is:

| Query | Frequency |
|---|---|
| tree  | 10 |
| true  | 35 |
| try   | 29 |
| toy   | 15 |

A trie holding these has a root → `t` → `r`/`o` branches. Under `tr` sit `tree`, `true`, `try`. When the user types `tr`:

```
root → t → r  ──┬── ee  (tree:10)
                ├── ue  (true:35)
                └── y   (try:29)
```

**Naïve lookup algorithm (before optimization):**
1. Find the prefix node — `O(p)` where `p` = prefix length. (Walk `t`→`r`: 2 hops.)
2. Traverse the entire subtree, collecting all completed children — `O(c)`. (Collect `tree`, `true`, `try`.)
3. Sort children by frequency, take top-k — `O(c log c)`. (Sort → `[true:35, try:29, tree:10]`, take top-2 → `true`, `try`.)

Total: `O(p) + O(c) + O(c log c)` — too slow in the worst case (whole trie traversal). With billions of historical queries the subtree under a short prefix like `t` can be enormous.

**Two optimizations that collapse this to `O(1)`:**

| # | Optimization | Effect |
|---|---|---|
| 1 | **Cap prefix length** to ~50 chars (users rarely type more). | `O(p)` → `O(1)` (constant bound). |
| 2 | **Cache top-5 queries at every node.** | Step 2+3 collapse to a direct lookup → `O(1)`. |

After both, **the entire lookup is `O(1)`** — you walk a fixed small prefix and read the precomputed top-5 off the node. This is *the* key interview insight: precompute the answer at every prefix.

**Why caching top-5 per node is safe to rebuild weekly.** Empirically, the top-5 for common prefixes (`how to`, `best res…`, `weather`) barely move day-to-day. A weekly snapshot is therefore almost indistinguishable from a real-time index for the overwhelming majority of queries, while costing orders of magnitude less to compute and serve. Only the trending/breaking-news tail needs a faster path (see §13.7).

### 13.4.2 Data Gathering Service (realistic, batched)

Real-time trie updates on every keystroke are infeasible (billions of writes/day; top-5 rarely changes minute-to-minute). The redesigned pipeline:

```
 Users
   │  (sampled, append-only)
   ▼
┌─────────────────┐   raw logs    ┌──────────────┐
│ Analytics Logs  │ ────────────▶ │  Aggregators │  (e.g. weekly sum)
│ (file/DB)       │               └──────┬───────┘
└─────────────────┘                      │ aggregated (query, freq, time)
                                         ▼
                                ┌──────────────────┐
                                │   Workers        │  build trie snapshot
                                │ (offline, weekly)│
                                └────────┬─────────┘
                                         │ serialize
                            ┌────────────┴──────────┐
                            ▼                       ▼
                    ┌───────────────┐       ┌─────────────────┐
                    │  Trie Cache   │ ◀──── │   Trie DB       │
                    │ (in-memory)   │ snap  │ (Mongo / KV)    │
                    └───────┬───────┘       └─────────────────┘
                            │
                          serve
```

- **Analytics logs** — append-only, unindexed raw query events (sampled 1-in-N to save cost).
- **Aggregators** — sum occurrences per (query, time-window). Window size depends on freshness need: Twitter = seconds; Google keywords = weekly. We assume **weekly** rebuild.
- **Workers** — build the trie from aggregated data and persist it.
- **Trie Cache** — distributed in-memory copy (Redis/Memcached) refreshed from Trie DB on a schedule.
- **Trie DB** — durable snapshot. Two storage options:
  1. **Document store (MongoDB):** serialize the weekly trie snapshot as a document.
  2. **Key-value store:** map each prefix → its node data (the trie *as* a hash table). This is the **Prefix Hash Tree** idea from the Berkeley paper Xu cites.

### 13.4.3 Query Service (the hot read path)

```
  browser ──AJAX──▶ Load Balancer ──▶ API Servers ──▶ Trie Cache ──▶ top-5
                                       │ (miss)        ▲
                                       └───────────────┴── replenish from Trie DB
```

Optimizations on the read path:
- **AJAX** — no full-page refresh; the JS fetches suggestions asynchronously.
- **Browser caching** — `Cache-Control: private, max-age=3600`. Google itself caches typeahead results in the browser for 1 hour. `private` = don't cache on shared proxies; results are user-specific.
- **Data sampling** — don't log every keystroke; sample 1-in-N to cut log volume.

### 13.4.4 Trie Operations

- **Create** — workers build a fresh trie weekly from aggregated data; the new snapshot atomically replaces the old.
- **Update** — *Option A:* rebuild weekly (preferred). *Option B:* patch a single node — slow, because updating one node's frequency forces re-caching of top-5 in **every ancestor up to the root** (each ancestor stores the top-5 of its subtree).
- **Delete** — for hateful/dangerous queries, insert a **filter layer** in front of Trie Cache. Filter removes results at read time; the underlying DB row is purged asynchronously so the next weekly rebuild excludes it.

### 13.4.5 Scaling the Storage (sharding the trie)

Once the trie exceeds one machine's RAM:
- **Naïve sharding** by first character: `a–m` / `n–z`, etc. Up to 26 shards at level 1, then level 2 (`aa–ag`, `ah–an`, …).
- **Problem:** skewed distribution — far more words start with `c` than `x`.
- **Fix:** a **shard map manager** keeps a lookup table that assigns prefixes to shards based on **historical distribution**, balancing load (e.g. `s` alone on one shard, `u–z` combined on another if their volumes match).

## 13.5 Database Schema

### Trie DB as documents (MongoDB-style)
```json
{
  "_id": "tw",
  "top5": [
    {"q":"twitter","f":2350000},
    {"q":"twitch","f":1890000},
    {"q":"twilio","f":540000},
    {"q":"twd","f":410000},
    {"q":"twinkle","f":330000}
  ],
  "children": ["a","e","i","o"]
}
```

### Trie DB as key-value (hash table form)
| key (prefix) | value (node data) |
|---|---|
| `t` | `{top5:[...], children:[r,w]}` |
| `tw` | `{top5:[...], children:[i,o]}` |
| `twi` | `{top5:[...], children:[t,l]}` |

### Aggregated data table
| time | query | frequency |
|---|---|---|
| 2026-07-21 | twitter | 2,350,000 |
| 2026-07-21 | twitch  | 1,890,000 |

## 13.6 API Design

Single endpoint, GET, idempotent, cacheable:

```
GET /v1/autocomplete?prefix=<string>&client_id=<id>
→ 200 OK
  Cache-Control: private, max-age=3600
  Content-Type: application/json
  {
    "suggestions": [
      {"query":"twitter","score":2350000},
      {"query":"twitch", "score":1890000},
      {"query":"twilio", "score":540000},
      ...
    ]
  }
```

Notes:
- `prefix` is the partial string the user has typed.
- Response is small (5 short strings) → cheap to cache at the browser and at CDN edge.
- Auth via session cookie / bearer token; rate-limited per `client_id`.

## 13.7 Scaling Bottlenecks & Solutions

| Bottleneck | Solution |
|---|---|
| DB `LIKE`+`ORDER BY` too slow | Replace with in-memory **trie with cached top-5 per node** → `O(1)` lookup. |
| Real-time writes thrash the trie | **Batch/offline aggregation**; weekly (or short-window) rebuild. |
| Single trie too big for RAM | **Shard** by prefix using a shard-map manager keyed on historical distribution. |
| Per-region query popularity differs | Build **per-country tries** and serve from regional **CDN** caches. |
| Trending (breaking-news) queries | Sample more aggressively, **time-decay** the ranking, switch to **stream processing** (Kafka + Spark Streaming / Storm). |
| Hateful/dangerous suggestions | **Filter layer** in front of cache + async purge from DB. |

## 13.8 Specific Technologies

- **Trie / Prefix Hash Tree** — core data structure; precomputed top-k per node.
- **MongoDB** (document store) or **Redis / DynamoDB** (KV) for Trie DB.
- **Redis / Memcached** for Trie Cache.
- **Apache Kafka** for the analytics log stream.
- **Spark Streaming / Storm / Hadoop MapReduce** for real-time aggregation (trending case).
- **CDN** for regional trie snapshots.
- **AJAX + browser Cache-Control** on the client.

## 13.9 Trade-offs

| Decision | Pro | Con |
|---|---|---|
| Cache top-5 at every node | `O(1)` reads; meets 100 ms SLA. | Heavy memory cost; updating one node cascades to all ancestors. |
| Weekly rebuild vs. real-time | Simple, cheap, good enough for stable keywords. | Stale for trending topics. |
| Document store vs. KV for Trie DB | Document = easy snapshot/serialize. KV = easier to shard & update a single prefix. | KV needs a prefix→node mapping layer. |
| Sampling logs | Cuts cost dramatically. | Loses long-tail signal; may bias rankings. |
| First-char sharding | Simple. | Skewed (`c` ≫ `x`); needs historical rebalancing. |

## 13.10 Interview Q&A

**Q1. Walk me through the time complexity of returning the top-5 for a prefix.**
A: With the naïve trie it is `O(p) + O(c) + O(c log c)` (find prefix, walk subtree, sort). With the two optimizations — capping prefix length at ~50 and caching top-5 at each node — every step becomes constant-bounded, so the lookup is effectively **`O(1)`**. That is the central design win.

**Q2. How would you support real-time / trending queries?**
A: Three levers: (1) **shard** the working set so each shard is small enough to rebuild in minutes; (2) change the ranking model to **weight recent queries more** (time-decay); (3) move from batch aggregation to **stream processing** (Kafka → Spark Streaming / Storm) so the trie or a side-index is updated continuously rather than weekly.

**Q3. How do you delete a harmful suggestion?**
A: Two layers. (a) A **filter layer** in front of Trie Cache drops the suggestion at read time so it disappears immediately. (b) Asynchronously purge the underlying row in Trie DB so the next weekly rebuild excludes it permanently. This separates "fast user-facing removal" from "durable data cleanup."

**Q4. How do you shard a trie that no longer fits in one machine?**
A: Start with **first-character sharding** (up to 26 shards), then recurse to second/third character. Because letters are skewed, use a **shard-map manager** that consults historical query-volume distribution and assigns prefix ranges to shards so load is balanced (e.g. `s` alone vs. `u–z` combined). The shard map is just a lookup table consulted on every read.

**Q5. How would you extend this to multiple languages and per-country rankings?**
A: Store **Unicode** characters in trie nodes (each node's children map becomes a hash, not a fixed 26-array). For geographic relevance, build **separate tries per country/region** and host them in regional **CDN** PoPs so users get locally relevant suggestions with low latency. Ranking weights can also be tuned per region.

---

# Chapter 14 — Design YouTube

> **Analogy:** A global movie studio + shipping network. Creators drop off raw film at a local depot; the studio encodes it into every format/quality; copies are pre-shipped to cinemas (CDN edge nodes) near every viewer. When you press play, the nearest cinema streams it to you instantly.

## 14.1 Problem Statement & Requirements

### Scope (from the candidate–interviewer Q&A)
- Core features: **upload a video** and **watch (stream) a video**.
- Clients: **mobile app, web browser, smart TV**.
- **5 M DAU**, ~30 min/day per user.
- Accept most resolutions/formats; **max video size 1 GB**; encryption required.
- Leverage existing cloud infra (CDN, blob storage) — building them from scratch is unrealistic.

### Functional Requirements
- Upload videos (resumable, multi-format).
- Stream videos with **adaptive bitrate** (quality changes with bandwidth).
- Manage metadata (title, description, thumbnails).

### Non-Functional Requirements
- **Fast uploads**, **smooth streaming** (low time-to-first-frame).
- **Low infrastructure cost** (CDN egress is the dominant expense).
- **High availability, scalability, reliability.**
- International support (80+ languages).

## 14.2 Back-of-the-Envelope Estimation

- 5 M DAU, 5 videos watched/user/day → **25 M views/day**.
- 10% of users upload 1 video/day → **500k uploads/day**.
- Avg video size **300 MB**.

| Metric | Calculation | Value |
|---|---|---|
| Daily upload storage | 5M × 10% × 300 MB | **150 TB/day** |
| Daily CDN egress cost | 5M × 5 × 0.3 GB × $0.02 | **~$150,000/day** (~$55M/yr) |

**Key insight:** the system is **read- and bandwidth-dominated**; CDN egress dwarfs every other cost. Cost optimization is a first-class design concern, not an afterthought.

**Sanity check on the numbers.**
- *Storage:* 150 TB/day × 365 ≈ **55 PB/year** of raw uploads. But after transcoding into ~5 resolutions and keeping originals, multiply by ~5–10× → **~0.5 EB/year** of stored encoded video. Object storage (S3) at ~$23/TB-month means ~$11M/month just to *store* one year's corpus — non-trivial but far below the egress bill.
- *Egress:* 25M views/day × 300 MB = **7.5 PB/day** streamed. At $0.02/GB that's the $150k/day headline. Cloud providers give hyperscale customers (Netflix-class) steep discounts — often 60–80% off list — which is why building/owning your CDN becomes attractive only past a certain volume threshold. Bring this up: *"at our 5M DAU we're firmly in the cloud-CDN zone; the build-your-own inflection point is somewhere around 50–100M DAU."*
- *Upload bandwidth:* 500k uploads × 300 MB = **150 TB/day ingress**, which cloud providers generally don't charge for (ingress is free on AWS/GCP) — so upload bandwidth is a *latency* problem, not a *cost* problem. This is why the upload optimizations (GOP chunking, edge ingress) target speed, not dollars.

## 14.3 High-Level Architecture

Three top-level components:
- **Client** (mobile / web / smart TV).
- **CDN** — serves video bytes from edge nodes near users.
- **API servers** — everything *except* video streaming (metadata, upload URL, recommendations, auth).

Everything splits into two flows: **Video Upload** and **Video Streaming**.

### 14.3.1 Video Upload Flow

```
        ┌────────┐   1. request pre-signed URL     ┌──────────────┐
        │ Client │ ──────────────────────────────▶ │ API Servers  │
        └───┬────┘ ◀────────────────────────────── └──────┬───────┘
            │ 2. pre-signed URL                         │ b. metadata
            │                                           ▼
            │   ┌──────── Flow a: actual video ────────┐│
            ▼   ▼                                       ││
  ┌──────────────────┐  3. upload    ┌──────────────────┐│
  │  Original Storage│ ◀───────────  │  (via pre-signed) ││
  │  (blob / S3)     │               └──────────────────┘│
  └────────┬─────────┘                                     │
           │ 4. fetch                                       │
           ▼                                                │
  ┌──────────────────┐   5. transcode (DAG)   ┌─────────────┴──────┐
  │ Transcoding      │ ─────────────────────▶ │ Transcoded Storage │
  │ Servers          │                        │ (blob / S3)        │
  └────────┬─────────┘                        └─────────┬──────────┘
           │                                            │ 6. push to CDN
           │ 5b. completion event                       ▼
           ▼                                  ┌──────────────────┐
  ┌──────────────────┐   7. update meta     │      CDN          │
  │ Completion Queue │ ────▶ Completion ──▶ │ (edge caches)     │
  └──────────────────┘       Handler         └─────────┬─────────┘
                                                  8. notify client "ready"
```

**Flow a (the bytes)** and **Flow b (the metadata)** run **in parallel**:
- *Flow a:* client uploads the video (via pre-signed URL) → transcoding servers fetch it → produce multiple encodings → store transcoded files → push to CDN → emit completion event → completion handler updates metadata DB/cache → API server tells the client the video is ready.
- *Flow b:* client sends metadata (filename, size, format, user info) → API servers update metadata DB & cache.

### 14.3.2 Video Streaming Flow

```
  Client ──play──▶ CDN ──(adaptive bitrate manifest)──▶ Client plays
                    ▲
                    │ only popular videos live here
            ┌───────┴────────┐
            │ Transcoded Store│  (fallback for long-tail)
            └─────────────────┘
```

The client requests a **streaming manifest** (list of bitrate/resolution segments) and the CDN streams segments adaptively. **Downloading** = whole file copied first; **streaming** = continuous byte stream so playback starts immediately.

**Streaming protocols** (standardized transfer):
- **MPEG-DASH** (Dynamic Adaptive Streaming over HTTP).
- **Apple HLS** (HTTP Live Streaming).
- Microsoft Smooth Streaming; Adobe HDS.

The protocol dictates which encodings/players are compatible — pick one matching your client matrix.

## 14.4 Detailed Component Design

### 14.4.1 Video Transcoding — why and how

**Why transcode (4 reasons):**
1. Raw video is huge (1 hr HD@60fps = hundreds of GB).
2. Device/browser format compatibility (need multiple containers/codecs).
3. Deliver higher bitrate to fast networks, lower to slow ones.
4. Adapt to changing mobile network conditions (auto quality switch).

**Anatomy of an encoded file:**
- **Container** (`.mp4`, `.mov`, `.avi`) — the basket holding video + audio + metadata.
- **Codec** (H.264, VP9, HEVC) — the compression algorithm.

### 14.4.2 DAG Model for the processing pipeline

Different creators need different pipelines (watermarks, thumbnails, multiple resolutions). Borrowing from **Facebook's SVE**, the pipeline is expressed as a **Directed Acyclic Graph (DAG)** so tasks can run **sequentially or in parallel** and creators can configure their own.

```
                ┌─────────── Original Video ───────────┐
                ▼                 ▼                      ▼
            ┌──────┐         ┌────────┐              ┌──────────┐
            │Video │         │ Audio  │              │ Metadata │
            └──┬───┘         └───┬────┘              └──────────┘
       ┌───────┴────────┐        │
       ▼                ▼        ▼
  ┌──────────┐   ┌──────────┐  ┌──────────────┐
  │ Encode   │   │Thumbnail │  │ Audio Encode │
  │ 240/480/ │   │ (gen or  │  └──────────────┘
  │ 720/1080p│   │  upload) │
  └────┬─────┘   └────┬─────┘
       └──────┬───────┘
              ▼
        ┌──────────┐
        │ Watermark│
        └────┬─────┘
              ▼
        Encoded outputs (funny_720p.mp4, funny_1080p.mp4, …)
```

### 14.4.3 Video Transcoding Architecture (6 components)

```
  Original ──▶ ┌──────────────┐  stages   ┌───────────────┐  pick task/worker ┌──────────────┐
   Video       │ Preprocessor │ ────────▶ │ DAG Scheduler │ ────────────────▶ │  Resource    │
               │  • GOP split │           └───────────────┘                   │  Manager     │
               │  • DAG gen   │                                               │ (3 queues +  │
               │  • cache GOP │                                               │  scheduler)  │
               └──────┬───────┘                                               └──────┬───────┘
                      │ temp storage (blob for media, in-mem for meta)             │ dispatch
                      ▼                                                          ▼
                                                              ┌─────────────────────────────────┐
                                                              │       Task Workers               │
                                                              │  encode │ thumbnail │ watermark  │
                                                              └──────────────┬──────────────────┘
                                                                             ▼
                                                                  ┌───────────────────┐
                                                                  │  Encoded Video    │
                                                                  └───────────────────┘
```

- **Preprocessor** — (1) splits video into **GOP** (Group of Pictures) chunks, each independently playable (~few seconds); (2) handles GOP splitting for old clients that can't do it; (3) generates the DAG from config files; (4) caches GOPs in temp storage so failed encodes can retry.
- **DAG scheduler** — splits the DAG into stages of tasks, enqueues them.
- **Resource manager** — 3 queues + a scheduler:
  - *Task queue* (priority) — tasks to run.
  - *Worker queue* (priority) — worker utilization info.
  - *Running queue* — currently-bound task/worker pairs.
  - *Task scheduler* — picks highest-priority task, matches it to the optimal worker, binds them in the running queue, removes on completion.
- **Task workers** — run DAG tasks (encode, thumbnail, watermark…); different workers can specialize.
- **Temporary storage** — metadata in memory (small, hot); media in blob. Freed after processing.
- **Encoded video** — final output (e.g. `funny_720p.mp4`).

**Worked example — DAG scheduler staging.** Take the DAG from §14.4.2. The scheduler decomposes it into stages:

```
Stage 1 (parallel):   split → [video_stream] [audio_stream] [metadata]
Stage 2 (parallel):   video → {encode_240p, encode_480p, encode_720p, thumbnail}
                      audio → {encode_audio}
Stage 3 (sequential): all outputs → watermark → assemble manifests
```

The task scheduler pops the highest-priority ready task (e.g. `encode_720p`), finds a worker in the worker queue with a matching GPU/codec profile and spare capacity, binds them in the running queue, and dispatches. When `encode_720p` completes, any Stage-3 tasks whose *other* dependencies are also done become ready. This is essentially a **topological executor** with a priority-aware dispatcher — the same pattern Airflow/Prefect use for data pipelines.

**Resource manager scheduling loop (pseudocode):**
```python
while True:
    task   = task_queue.pop_highest_priority()   # blocked if empty
    worker = worker_queue.pop_best_match(task)   # by capability + load
    if worker is None:
        task_queue.push(task); sleep(backoff); continue
    running_queue.add((task, worker))
    worker.execute(task, on_done=lambda: on_complete(task, worker))

def on_complete(task, worker):
    running_queue.remove((task, worker))
    worker_queue.add(worker)                      # return worker to pool
    dag_scheduler.mark_done(task)                 # may unlock downstream tasks
```

### 14.4.4 System Optimizations

**Speed — parallelize uploads:** split the video into **GOP-aligned chunks** on the client; upload chunks in parallel; supports **resumable** upload (only re-send failed chunks).

**Speed — upload centers near users:** use **CDN PoPs as upload ingress** (US users upload to NA edge, Chinese users to Asia edge).

**Speed — parallelism everywhere:** decouple pipeline stages with **message queues** so the encoder doesn't block on the downloader; each stage consumes its queue independently.

**Safety — pre-signed upload URLs:** client asks API for a pre-signed URL (time-limited, scoped to one object); uploads go **directly to blob storage**, bypassing API servers. (Azure calls the equivalent "Shared Access Signature".)

**Safety — protect content (3 options):**
1. **DRM** — Apple FairPlay, Google Widevine, Microsoft PlayReady.
2. **AES encryption** — encrypt video, decrypt on authorized playback.
3. **Visual watermarking** — overlay logo/ID.

**Cost — exploit the long tail:** YouTube views follow a **long-tail distribution** — a few hits get most traffic, most videos get few/no views.

| Tactic | Effect |
|---|---|
| Serve only **popular** videos from CDN; long-tail from high-capacity origin servers. | Big CDN egress cut. |
| For unpopular content, store fewer encodings; **encode on demand**. | Less storage + transcode. |
| Regionally popular videos stay regional — don't fan out globally. | Less cross-region replication. |
| **Build your own CDN** + partner with ISPs (Netflix Open Connect model). | Cheaper bandwidth at huge scale. |

### 14.4.5 Error Handling Playbook

| Failure | Strategy |
|---|---|
| Upload error | Retry a few times. |
| Split error (old client) | Server-side GOP split. |
| Transcode error | Retry. |
| Preprocessor error | Regenerate DAG. |
| DAG scheduler error | Reschedule task. |
| Resource manager queue down | Use replica. |
| Task worker down | Retry on a new worker. |
| API server down | Stateless → reroute via LB. |
| Metadata cache down | Read from replicas; spin up replacement. |
| Metadata DB master down | Promote a slave. |
| Metadata DB slave down | Use another slave; replace. |

**Recoverable vs. non-recoverable** — the unifying principle:
- *Recoverable* (segment failed to transcode, transient network blip) → **retry** with backoff; if it exhausts attempts, escalate to a non-recoverable error code.
- *Non-recoverable* (malformed video format, corrupt input) → **stop** all running tasks for that video, return a clear error to the client, mark status `FAILED`. Don't burn worker cycles retrying something that will never succeed.

**Idempotency note.** Every task in the DAG must be idempotent (running `thumbnail` twice yields the same output), so retries never corrupt state. Use the `video_id` + stage + attempt as a deterministic key for output paths so duplicate writes collapse.

## 14.5 Database Schema (metadata)

Videos are in blob storage; the DB holds **metadata only**.

```sql
video_metadata
─────────────────────────────────────────────
video_id        PK
user_id         FK      -- uploader
title
description
status          ENUM    -- UPLOADING | PROCESSING | READY | FAILED
size_bytes
duration_sec
container       VARCHAR -- mp4, mov, ...
created_at
updated_at

video_encoding                  -- one row per (video, resolution/codec)
─────────────────────────────────────────────
encoding_id     PK
video_id        FK
resolution      VARCHAR         -- 240p, 480p, 720p, 1080p, 4k
codec           VARCHAR         -- H.264, VP9, HEVC
bitrate         INT
manifest_url    VARCHAR         -- CDN/HLS URL
file_path       VARCHAR         -- blob storage path
created_at

user
─────────────────────────────────────────────
user_id         PK
name, email, ...
```

## 14.6 API Design

```
# 1. Get pre-signed upload URL
POST /v1/videos/upload-url
  { "filename":"funny.mp4", "size":314159265, "content_type":"video/mp4" }
→ 200 { "upload_url":"https://storage.../funny.mp4?sig=...", "video_id":"v_123" }

# 2. Update metadata (runs in parallel with the upload)
POST /v1/videos/{video_id}/metadata
  { "title":"Funny Cat", "description":"...", "tags":[...] }

# 3. Streaming (the client requests a manifest from the CDN)
GET https://cdn.../v_123/manifest.mpd      # MPEG-DASH manifest
GET https://cdn.../v_123/720p/segment_42.ts
```

All APIs are HTTPS + authenticated (except the actual byte fetch, which uses the pre-signed URL).

## 14.7 Scaling Bottlenecks & Solutions

| Bottleneck | Solution |
|---|---|
| Huge upload bandwidth | Pre-signed URLs straight to blob; **GOP-chunked parallel uploads**; CDN-edge upload ingress. |
| Slow, CPU-bound transcoding | **DAG pipeline** with parallel task workers; resource manager scheduling. |
| CDN egress cost | Long-tail aware serving (popular→CDN, rest→origin); on-demand encoding; **own CDN** at huge scale. |
| Slow pipeline stages blocking each other | **Message queues** between stages → decoupled parallel execution. |
| Device/format diversity | Multiple codec/resolution encodings + adaptive-bitrate streaming protocols (DASH/HLS). |
| Component failures | Retry for recoverable; stop+notify for non-recoverable; stateless API tier; DB master/slave failover. |

## 14.8 Specific Technologies

- **Blob storage** (Amazon S3 / equivalent) for original + transcoded video.
- **CDN** (CloudFront / Akamai / self-built Open Connect-style) for delivery.
- **Transcoding**: FFmpeg / cloud media-convert; codecs H.264 / VP9 / HEVC.
- **DAG pipeline** (à la Facebook SVE) for flexible, parallel processing.
- **Message queues** (Kafka/SQS) for completion events and stage decoupling.
- **GOP (Group of Pictures)** chunking for parallel/resumable upload.
- **Adaptive streaming protocols**: MPEG-DASH, HLS.
- **Pre-signed URLs** (S3) / Shared Access Signatures (Azure).
- **DRM**: FairPlay / Widevine / PlayReady; AES encryption; watermarking.

## 14.9 Trade-offs

| Decision | Pro | Con |
|---|---|---|
| Use cloud CDN + blob vs. build your own | Fast to ship; reliable. | Egress cost; vendor lock-in. |
| Build own CDN (Netflix model) | Dramatically cheaper at hyperscale; ISP peering. | Giant capex/engineering project. |
| Store many encodings per video | Best adaptive-bitrate UX. | Storage + transcode cost; wasteful for long-tail. |
| On-demand encoding for unpopular videos | Saves storage/transcode. | Latency on first view. |
| GOP-chunked upload | Parallel + resumable. | Client complexity (old clients can't split). |
| Pre-signed URL upload | Offloads bytes from API tier; secure. | Requires careful URL expiry/scoping. |

## 14.10 Interview Q&A

**Q1. Why must we transcode every uploaded video?**
A: Four reasons: (1) raw video is enormous (HD@60fps can be hundreds of GB/hr); (2) format/codec compatibility across devices and browsers; (3) to serve **multiple bitrates** so adaptive streaming can match each viewer's bandwidth; (4) to allow quality auto-switching when mobile network conditions change. Without transcoding you'd ship one giant, incompatible file and couldn't adapt to the viewer.

**Q2. Explain the DAG model and why it matters.**
A: A Directed Acyclic Graph expresses the video-processing pipeline as stages of tasks (inspect → split into video/audio/metadata → encode + thumbnail + watermark → assemble). Edges encode dependencies; nodes with no dependency between them run **in parallel**. This gives flexibility (creators configure their own pipeline via config files) and high throughput (the scheduler and resource manager keep workers saturated). Facebook's SVE uses exactly this model.

**Q3. How do you reduce the enormous CDN cost?**
A: Exploit the **long-tail** view distribution. (1) Serve only popular videos from CDN; push long-tail to origin/high-capacity storage. (2) Store fewer encodings for unpopular videos and **encode on demand**. (3) Keep regionally-popular videos regional — don't replicate globally. (4) At hyperscale, **build your own CDN** and peer with ISPs (Netflix Open Connect) to cut bandwidth charges drastically.

**Q4. How do pre-signed upload URLs work and why use them?**
A: The client first calls an API server to obtain a **time-limited, object-scoped signed URL** for blob storage, then uploads the bytes **directly to storage** (S3/Azure) — the API servers never touch the large file. This (a) keeps the API tier stateless and cheap, (b) secures uploads (only authorized users get a valid URL), and (c) enables large/resumable uploads without proxying through your servers. Azure's equivalent is the Shared Access Signature.

**Q5. How would you extend this design for live streaming?**
A: The upload→encode→stream pipeline is similar but with key differences: (1) **much stricter latency** requirements → use a low-latency streaming protocol (e.g. LL-HLS, WebRTC); (2) **lower parallelism benefit** because chunks are already tiny and processed in real time; (3) **different error handling** — any slow retry is unacceptable, so failures must fail-fast. The DAG model still applies but stages are streamed/pipelined rather than batched.

---

# Chapter 15 — Design Google Drive

> **Analogy:** A magic filing cabinet. You drop a document in one drawer at home; the cabinet instantly makes identical copies appear in the drawer at your office and on your phone, keeps every old version, and pings your collaborator that something changed — all without sending the whole document each time.

## 15.1 Problem Statement & Requirements

### Scope (from clarifying Q&A)
- Core features: **upload/download files**, **file sync across devices**, **file revisions**, **sharing**, **notifications** on edit/delete/share.
- Both **web and mobile**; **any file type**; files encrypted at rest; **max 10 GB/file**.
- **50 M signed-up users, 10 M DAU.**
- *Out of scope:* real-time collaborative editing (Google Docs co-editing).

### Functional Requirements
- Add files (drag & drop).
- Download files.
- **Sync** files across all of a user's devices automatically.
- View file revision history.
- Share files with other users.
- Notify relevant clients when a file is added/edited/deleted/shared.

### Non-Functional Requirements
- **Reliability** — data loss is unacceptable.
- **Fast sync speed** — users abandon slow sync.
- **Low bandwidth usage** — mobile data plans matter.
- **Scalability** — high traffic volume.
- **High availability** — works during partial outages.
- **Strong consistency** — a file must look identical on all clients at the same time.

## 15.2 Back-of-the-Envelope Estimation

- 50 M users, 10 M DAU; 10 GB free space each.
- 2 uploads/day, avg **500 KB** each; 1:1 read:write ratio.

| Metric | Calculation | Value |
|---|---|---|
| Total allocated space | 50M × 10 GB | **500 PB** |
| Upload QPS | 10M × 2 / 86400 | **~240 QPS** |
| Peak upload QPS | × 2 | **~480 QPS** |

**Key insight:** unlike YouTube (read/egress dominated), Google Drive is **write/sync-heavy** with a **massive total storage footprint** (500 PB). The hard problems are **sync correctness**, **bandwidth efficiency**, and **storage cost** — not raw QPS.

**Sanity check on the 500 PB.** Most users never come close to their 10 GB quota — real-world utilization for a free tier is typically 10–30%. So *actual* stored data is likely **50–150 PB**, not 500 PB. But you still provision against the quota ceiling (users will fill it eventually), and the *cost* of the allocated-but-empty headroom is near zero on object storage (you pay for what you store, not what you *could* store). De-dup across users (same shared PDF, same OS installer) can cut stored bytes another 20–40%. Mention both levers — interviewers reward showing you know the difference between *allocated* and *realized* storage.

**Why QPS is low but the system is still hard.** 240 upload QPS is trivial for a modern API tier — a handful of boxes. The difficulty is entirely in **correctness and fan-out**: every write must (a) hit the metadata DB transactionally, (b) trigger block-server processing, (c) notify every other online device of the user, (d) be buffered for offline devices, (e) respect sharing ACLs. The *coordination* complexity per write is what makes Google Drive harder than its modest QPS suggests.

## 15.3 High-Level Architecture

The chapter builds up from a **single server** → **sharded** → **decoupled + S3** → the final multi-component design. The final architecture:

```
                       ┌─────────┐
                       │  User   │ (browser / mobile)
                       └────┬────┘
                            │ HTTPS
                            ▼
                    ┌───────────────┐
                    │ Load Balancer │
                    └───────┬───────┘
              ┌─────────────┴──────────────┐
              ▼                            ▼
      ┌───────────────┐            ┌────────────────┐
      │  API Servers  │ ◀────────▶ │ Metadata Cache │
      │ (auth, meta)  │            └────────┬───────┘
      └───────┬───────┘                     │
              │                             ▼
              │                     ┌─────────────────┐
              │                     │ Metadata DB     │
              │                     │ (relational,    │
              │                     │  sharded+repl)  │
              │                     └─────────────────┘
              ▼
      ┌───────────────┐   blocks   ┌─────────────────┐
      │ Block Servers │ ─────────▶ │  Cloud Storage  │ (S3, replicated)
      │ (chunk, comp, │            │   (hot)         │
      │  encrypt)     │            └─────────────────┘
      └───────┬───────┘
              │  also archives inactive data
              ▼
      ┌───────────────┐
      │ Cold Storage  │ (S3 Glacier — cheap, infrequent access)
      └───────────────┘

      ┌────────────────────────┐         ┌──────────────────┐
      │ Notification Service   │ ◀────── │ Offline Backup   │
      │ (long-poll / pub-sub)  │         │ Queue            │
      └───────────┬────────────┘         └──────────────────┘
                  │ file-changed events
                  ▼
              (clients)
```

### Component roles
- **Block servers** — split files into blocks, compress, encrypt, upload only changed blocks (delta sync).
- **Cloud storage (S3)** — stores file blocks as objects; cross-region replicated.
- **Cold storage (Glacier)** — inactive data, much cheaper.
- **Load balancer** — distributes API requests.
- **API servers** — auth, user profile, file metadata, everything except the byte path.
- **Metadata DB** — relational (ACID), sharded + replicated; stores user/device/file/version/block metadata.
- **Metadata cache** — hot metadata for fast reads.
- **Notification service** — pub/sub; tells clients a file changed elsewhere.
- **Offline backup queue** — buffers changes for offline clients until they reconnect.

## 15.4 Detailed Component Design

### 15.4.1 Block Servers — bandwidth is the scarcest resource

Two optimizations to **minimize bytes transferred**:

1. **Delta sync** — when a file changes, upload **only the modified blocks**, not the whole file (rsync-style algorithm).
2. **Compression** — compress each block by type (gzip/bzip2 for text; codec-specific for images/video).

**Block server pipeline on a new file:**
```
  file ──▶ split into blocks (≤4MB, Dropbox-style)
        ──▶ compress each block
        ──▶ encrypt each block
        ──▶ upload blocks to cloud storage
        ──▶ record (block_id, hash, order) in metadata DB
```

**Delta sync on edit** — only changed blocks (e.g. block 2 and block 5) are re-uploaded; unchanged blocks are reused by hash.

### 15.4.2 Strong Consistency

Default requirement: a file must appear **identical on all clients simultaneously**.

- Memory caches are **eventually consistent** by default → insufficient.
- To enforce strong consistency:
  - Keep cache replicas consistent with the master.
  - **Invalidate cache on DB write** (write-through / invalidate).
- Relational DBs give ACID for free; NoSQL requires you to **program ACID into sync logic**.
- **Decision:** use a **relational database** so ACID is native.

### 15.4.3 Metadata Database Schema

```sql
-- (highly simplified; most important tables only)

user
────────────────────────────────────
user_id      PK
username
email
profile_photo

device                                  -- a user can have many devices
────────────────────────────────────
device_id    PK
user_id      FK
device_type  ENUM   -- ios, android, web, desktop
push_id             -- for mobile push notifications

namespace                               -- root dir of a user
────────────────────────────────────
namespace_id PK
user_id      FK
name

file                                    -- latest version of a file
────────────────────────────────────
file_id      PK
namespace_id FK
parent_id            -- folder
name
size
type                 -- mime type
status               -- UPLOADING | UPLOADED | ...
created_at
updated_at

file_version                            -- version history (rows read-only)
────────────────────────────────────
version_id   PK
file_id      FK
size
created_at
-- existing rows immutable to preserve revision integrity

block                                   -- one row per block of a version
────────────────────────────────────
block_id     PK
version_id   FK
index               -- position to reconstruct in order
hash                -- for de-dup and integrity
storage_key         -- S3 object key
size
```

A file of any version is **reconstructed by joining its blocks in `index` order**.

### 15.4.4 Upload Flow (sequence)

Two parallel requests from the client:

```
   Client 1
   ├─(A) add file metadata───────────────┐
   │                                    ▼
   │                          API Server ──▶ Metadata DB (status=PENDING)
   │                                          │
   │                                          ▼ event
   │                                  Notification Service ──▶ Client 2 ("file being added")
   │
   └─(B) upload file content────────────┐
                                       ▼
                             Block Server
                                  │  chunk/compress/encrypt
                                  ▼
                             Cloud Storage
                                  │  completion callback
                                  ▼
                             API Server ──▶ Metadata DB (status=UPLOADED)
                                  │ event
                                  ▼
                             Notification Service ──▶ Client 2 ("file ready")
```

### 15.4.5 Download Flow (sequence)

Triggered when a file changed elsewhere; the client learns via notification (online) or pulls on reconnect (offline).

```
  1. Notification Service → Client 2: "file X changed"
  2. Client 2 → API Server: GET metadata of changes
  3. API Server → Metadata DB → returns metadata
  4. Client 2 ← metadata
  5. Client 2 → Block Server: download new blocks
  6. Block Server ← Cloud Storage: fetch blocks
  7. Client 2 ← blocks (reconstruct file)
```

### 15.4.6 Notification Service

Purpose: keep all of a user's clients consistent by telling them about remote changes.

Two options:
- **Long polling** (Dropbox's choice) — client holds an open request; server responds when a change arrives; client reconnects immediately after.
- **WebSocket** — persistent bidirectional connection.

**Chosen: long polling**, because:
- Communication is **one-way** (server → client) — no need for bidirectional.
- Notifications are **infrequent, non-bursty** — WebSocket's real-time bidirectional strength (chat apps) is overkill.
- Simpler to operate at scale.

### 15.4.7 Saving Storage Space

Version history × cross-region replication fills storage fast. Three tactics:

| Tactic | Mechanism |
|---|---|
| **De-duplicate blocks** | Two blocks with the **same hash** are stored once (at account level). |
| **Intelligent versioning** | Cap number of versions; **weight recent versions** more; drop old ones when limit hit. |
| **Move cold data to Glacier** | Inactive files → Amazon S3 Glacier (much cheaper than S3). |

### 15.4.8 Failure Handling

| Component | Failure mode | Strategy |
|---|---|---|
| Load balancer | Down | Secondary takes over (heartbeat-monitored). |
| Block server | Down | Other servers pick up pending jobs. |
| Cloud storage | Region down | Fetch from replicated region. |
| API server | Down | Stateless → LB reroutes. |
| Metadata cache | Node down | Read from replicas; spin up replacement. |
| Metadata DB — master | Down | Promote a slave; bring up new slave. |
| Metadata DB — slave | Down | Use another slave; replace. |
| Notification service | Down | All long-poll connections drop; clients **reconnect** (slow — millions of connections per machine per Dropbox's 2012 talk). |
| Offline backup queue | Down | Consumers re-subscribe to the replicated queue. |

**The notification-server reconnect storm.** This is the subtlest failure mode. A single notification server may hold **>1 million open long-poll connections** (Dropbox's 2012 figure). If it dies, all those clients try to reconnect simultaneously. Naively letting them all reconnect would overwhelm the replacement pool. Production mitigations:
- **Exponential backoff with jitter** on the client so reconnects spread out over time.
- **Gradual admission** at the notification tier — accept new connections at a bounded rate, queue the rest.
- **Connection draining** on planned shutdowns so traffic shifts before the box goes dark.

**Why "data loss is unacceptable" shapes the whole design.** This single non-functional requirement is what forces: (a) cross-region S3 replication (a region can burn down); (b) the offline backup queue (an offline client's pending changes are never silently dropped); (c) version history that is append-only/read-only (you can't accidentally overwrite a prior revision); (d) a relational DB with ACID (partial writes must roll back, not leave half-committed file metadata).

## 15.5 API Design

All APIs are **HTTPS + authenticated** (SSL protects data in transit).

```
# 1. Upload a file
#   Two modes:
#   • simple upload   — small files
#   • resumable upload — large files / flaky networks
POST https://api.example.com/files/upload?uploadType=resumable
  Params:
    uploadType = resumable
    data       = local file
  # 3-step resumable protocol:
  #   1. initial request → retrieve resumable URL
  #   2. upload data, monitor state
  #   3. if interrupted → resume

# 2. Download a file
POST https://api.example.com/files/download
  { "path": "/recipes/soup/best_soup.txt" }

# 3. Get file revisions
POST https://api.example.com/files/list_revisions
  { "path": "/recipes/soup/best_soup.txt", "limit": 20 }
```

## 15.6 Scaling Bottlenecks & Solutions

| Bottleneck | Solution |
|---|---|
| Single-server disk full | **Shard** metadata DB by `user_id`; move file bytes to **S3** (object storage). |
| Data loss risk | **Cross-region replication** (S3 same-region + cross-region). |
| Bandwidth on every edit | **Delta sync** + **compression** at block servers. |
| Storage bloat from versions | **Block de-dup** by hash; capped/weighted versioning; **Glacier** for cold data. |
| Multi-client inconsistency | **Strong consistency** via relational ACID + cache invalidation on write. |
| Sync conflicts | First-writer-wins; later writer gets a conflict, shown both copies to merge/override. |
| Offline clients | **Offline backup queue** buffers changes until reconnect. |
| Notification fan-out at scale | **Long polling**; millions of connections per server; graceful reconnect on failure. |

## 15.7 Specific Technologies

- **Block storage / object storage** — Amazon S3 for file blocks; **S3 Glacier** for cold data.
- **Block servers** — chunk (≤4 MB), compress (gzip/bzip2/codec), encrypt; **delta sync** (rsync/librsync algorithm).
- **Relational DB** (MySQL/PostgreSQL) — chosen for native **ACID** strong consistency; sharded + replicated.
- **Metadata cache** — Redis/Memcached with write-invalidation.
- **Notification service** — **long polling** (Dropbox-style) or WebSocket.
- **Offline backup queue** — replicated message queue (Kafka/SQS).
- **Load balancer** with heartbeat failover.
- **Resumable upload** protocol (Google Drive API-style 3-step).
- **SSL/TLS** for transport; encryption-at-rest for blocks.

## 15.8 Trade-offs

| Decision | Pro | Con |
|---|---|---|
| **Block servers** vs. client-uploads-direct | Centralizes chunk/compress/encrypt logic (one place, secure, cross-platform). | File traverses the network twice (client→block→S3). |
| Client-uploads-direct | Faster (one hop). | Must reimplement chunk/compress/encrypt on iOS/Android/Web; client is hackable → bad place for crypto. |
| **Relational DB** (ACID) | Strong consistency for free. | Harder to shard at hyperscale than NoSQL. |
| **Long polling** vs WebSocket | Simpler; fits one-way, low-frequency notifications. | Reconnect storm on server failure; not truly real-time. |
| **Delta sync + compression** | Massive bandwidth savings. | CPU cost at block servers; rsync algorithm complexity. |
| **Cold storage (Glacier)** | Cheap for inactive data. | Slow retrieval; lifecycle policy complexity. |
| **First-writer-wins** conflict resolution | Simple, deterministic. | Later writer must manually merge; poor for heavy co-editing (hence Docs is out of scope). |

## 15.9 Interview Q&A

**Q1. Why split files into blocks instead of storing whole files?**
A: Three reasons. (1) **Delta sync** — when a file changes, only the modified blocks are re-uploaded, saving bandwidth (critical on mobile). (2) **De-duplication** — blocks with identical hashes are stored once, even across versions or users, saving storage. (3) **Resumable uploads** — a failed upload only re-sends the failed blocks, not the whole file. Dropbox uses a 4 MB max block size as a reference.

**Q2. How does the system keep files consistent across a user's devices?**
A: Strong consistency is enforced at the metadata layer. We use a **relational DB** (native ACID) and **invalidate the cache on every write** so cache and DB never diverge. Any mutation triggers the **notification service**, which tells every other online client to pull the latest metadata and blocks. Offline clients get buffered changes from the **offline backup queue** when they reconnect. Conflicts (two simultaneous edits) are resolved first-writer-wins, with the later writer shown both copies to merge.

**Q3. Why long polling instead of WebSocket for notifications?**
A: The traffic is **one-way** (server → client) and **infrequent** — there's no burst of bidirectional data that would justify WebSocket's persistent bidirectional channel (which shines for chat). Long polling is simpler to operate and matches the access pattern. The trade-off is the **reconnect storm** when a notification server fails (each machine may hold >1M connections per Dropbox's 2012 talk) — reconnection must be gradual.

**Q4. How do you handle the case where the same file is edited simultaneously on two devices?**
A: First-writer-wins: whichever mutation reaches the metadata DB first commits; the second writer receives a **sync conflict**. The system presents that user with **both copies** — their local version and the latest server version — and lets them merge or override. (True real-time collaborative editing, like Google Docs, uses differential synchronization and is explicitly out of scope here.)

**Q5. Walk me through the storage cost-reduction strategies.**
A: Three levers. (1) **Block de-duplication** — blocks with the same hash are stored once, which catches both intra-user (revisions) and inter-user (shared files) redundancy. (2) **Intelligent versioning** — cap the number of retained versions, weight recent ones more heavily, and experiment to find the optimal cap (a heavily-edited doc could otherwise have 1000+ copies). (3) **Cold storage tiering** — move data inactive for months/years to **Amazon S3 Glacier**, which is far cheaper than standard S3, accepting slower retrieval in exchange.

---

# Cross-Chapter Synopsis

| Dimension | Ch.13 Autocomplete | Ch.14 YouTube | Ch.15 Google Drive |
|---|---|---|---|
| Dominant load | **Read-heavy** (24k QPS) | **Bandwidth-heavy** (PB/day egress) | **Write/sync-heavy** (500 PB stored) |
| Core data structure | **Trie** with cached top-k | **DAG** transcoding pipeline | **Block** storage + delta sync |
| Hot path latency target | **< 100 ms** | time-to-first-frame ~seconds | fast sync, no SLA stutter |
| Key cloud service | Cache + CDN | **CDN + blob** | **S3 + Glacier** |
| Freshness model | weekly rebuild (or streaming for trending) | near-real-time transcode | real-time notification + delta sync |
| Biggest cost driver | Memory (trie in RAM) | **CDN egress** | **Storage volume** |
| Consistency model | Eventually consistent (weekly snapshot) | Metadata strong; video eventual | **Strong** (ACID + cache invalidation) |
| Signature trade-off | Space-for-time (cache top-k at every node) | CDN cost vs. UX | Centralized block servers vs. direct upload |

### Common patterns across all three
1. **Decouple with queues** — completion queue (YouTube), offline backup queue (Drive), aggregators (Autocomplete).
2. **Shard by a natural key** — prefix (Autocomplete), video_id (YouTube), user_id (Drive).
3. **Cache aggressively on the read path** — Trie Cache, metadata cache, CDN.
4. **Move bytes off the API tier** — pre-signed uploads (YouTube), block servers (Drive), CDN (both).
5. **Handle failures with retries + replicas + stateless tiers** — the error-handling playbooks are structurally identical across all three chapters.

## Sharding Strategy Comparison

All three systems outgrow a single machine, but they shard on **different keys** for **different reasons**:

| System | Shard key | Why this key | Skew risk | Mitigation |
|---|---|---|---|---|
| **Autocomplete** | Prefix (first/second char) | A lookup for `tw` only needs the `t`-shard; the trie is naturally partitioned by prefix. | **High** — `c`, `s`, `t` are far more common than `x`, `z`, `q`. | Shard-map manager rebalances prefix ranges by historical volume. |
| **YouTube** | `video_id` (hash) | Each video's metadata + encodings are independent; uniform hash avoids hotspots from viral videos. | **Low** on metadata (uniform hash). **High** on CDN (viral video = hot edge). | CDN caches the viral video broadly; origin serves the long tail. |
| **Google Drive** | `user_id` (hash) | A user's entire namespace lives on one shard → no cross-shard joins for that user's file tree. | **Moderate** — power users (10 GB full, many files) vs. casual users. | Consistent hashing + virtual nodes; rebalance on overload signals. |

**Key takeaway for the interview:** always justify *why* you picked a shard key in terms of the **access pattern**. Autocomplete shards by prefix because reads are prefix-scoped. Drive shards by `user_id` because reads are user-scoped. YouTube shards by `video_id` because there's no natural cross-video access pattern. Picking the wrong key (e.g., sharding Drive by `file_id` instead of `user_id`) forces expensive cross-shard fan-out on every "list my files" query — a classic interview trap.

## Freshness Models Compared

The three chapters sit on a spectrum of **how stale data can be**:

```
   Stalest ◀──────────────────────────────────────────────▶ Freshest
   ┌──────────────────────┐  ┌────────────────────┐  ┌─────────────────────┐
   │ Autocomplete         │  │ YouTube            │  │ Google Drive        │
   │ (weekly trie rebuild)│  │ (near-real-time    │  │ (real-time sync +   │
   │                      │  │  transcode, ~min)  │  │  instant notify)    │
   └──────────────────────┘  └────────────────────┘  └─────────────────────┘
   Trade: cost/simplicity    Trade: upload latency    Trade: consistency +
   for stable keywords       vs. viewer readiness     bandwidth cost
```

- **Autocomplete** tolerates the most staleness because keyword popularity is sticky; a weekly snapshot is ~indistinguishable from real-time for 99% of prefixes.
- **YouTube** sits in the middle: a video is "uploading" for seconds-to-minutes while transcoding finishes; viewers tolerate a brief delay before a fresh upload is playable.
- **Google Drive** has the tightest freshness requirement — a file saved on your laptop must appear on your phone *immediately*, or the product feels broken. This is what forces the real-time notification service + delta-sync architecture rather than a simpler poll-based one.

When the interviewer asks "how fresh does the data need to be?", your answer should map to where on this spectrum the product sits, and that answer then dictates whether you need streaming pipelines (Autocomplete-trending), async queues (YouTube transcode), or synchronous notification (Drive).

---

# How to Pitch These in an Interview

A 45–60 minute system-design interview rewards a repeatable structure. All three chapters in this file follow Alex Xu's four-step framework. Here's how to run each one under time pressure.

## The 4-Step Framework (memorize this rhythm)

1. **Understand & scope (3–5 min)** — ask clarifying questions; nail functional + non-functional requirements; agree on scale numbers.
2. **High-level design (10–15 min)** — sketch the boxes; get buy-in before diving deep.
3. **Deep dive (15–25 min)** — pick 1–2 components the interviewer cares about and go deep.
4. **Wrap-up (3–5 min)** — bottlenecks, failure modes, future extensions, trade-offs.

## Per-Chapter "First 5 Minutes"

### Autocomplete — what to establish immediately
- "Prefix match only, top-5, ranked by historical frequency, English, 10M DAU, <100 ms response." Say this back explicitly to lock scope.
- Volunteer the **read-heavy** insight early: "tens of thousands of QPS reads vs. ~0.4 GB/day of new data — so the write path can be batched."
- Anchor the whole design on the **trie with cached top-5 per node** and the `O(1)` lookup — that's the headline the interviewer wants to hear.

### YouTube — what to establish immediately
- "Upload + stream, multi-client, max 1 GB, leverage cloud CDN/blob."
- Lead with the **cost number**: "$150k/day CDN egress dominates everything." This signals you understand the real constraint and sets up the long-tail optimization discussion later.
- State the two-flow split (**upload** vs. **streaming**) up front — it organizes the entire whiteboard.

### Google Drive — what to establish immediately
- "Sync + revisions + sharing + notifications, web+mobile, 10 GB cap, 50M users / 10M DAU."
- Lead with two non-functional priorities: **reliability (no data loss)** and **strong consistency**. These two constraints dictate almost every downstream choice (S3 replication, relational ACID DB, block servers, append-only version history).

## Common Pitfalls (what sinks candidates)

| Pitfall | Chapter | Fix |
|---|---|---|
| Jumping to the trie without estimating QPS first | 13 | Do the back-of-envelope; it justifies why a SQL `LIKE` won't scale. |
| Forgetting the **update cascade** in the trie (ancestors must re-cache top-5) | 13 | Mention it proactively when discussing Option B updates. |
| Designing your own CDN/blob from scratch | 14 | The interviewer explicitly wants you to *leverage* cloud services. State this. |
| Treating all videos equally for CDN placement | 14 | Bring up the **long-tail distribution** — it's the cost lever. |
| Storing files in the relational DB | 15 | Metadata DB only; bytes go to S3. State this explicitly. |
| Skipping the sync-conflict story | 15 | First-writer-wins + show-both-copies; interviewers love this. |
| No failure handling | all | Always reserve 3 min for the error playbook. |
| Over-engineering | all | Time-box; say "I'd go deeper on X if we had time, but given 45 min I'll focus on Y." |

## Diagram Discipline
- Draw **two clearly separated flows** (upload vs. stream/sync) — never one tangled blob.
- Label every arrow with the **data** that flows and the **protocol** (HTTPS, long-poll, pre-signed URL, message queue).
- Keep a consistent legend: `[ ]` = service, `( )` = data store, `~~>` = async/event.

## The "One More Thing" Candidates Miss
- **Autocomplete:** the **filter layer** for hateful/dangerous suggestions — shows product maturity.
- **YouTube:** **idempotent task keys** so retries don't corrupt the DAG — shows operational depth.
- **Google Drive:** the **reconnect storm** mitigation on notification-server failure — shows you've thought about production scale, not just the happy path.

Mentioning any one of these in the last two minutes is often what separates a "hire" from a "strong hire" signal.

---

*Source: Alex Xu, *System Design Interview — An Insider's Guide (Volume 1)*, Chapters 13–15. This document is a study deep-dive; refer to the book for the original figures and full discussion.*
