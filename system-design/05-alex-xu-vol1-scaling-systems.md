# System Design: Alex Xu Vol1 Chapters 9–12 — Scaling Real-World Systems

> **Analogy:** This file is the "second half" of Alex Xu's System Design Interview Volume 1 — the chapter arc where individual components stop being enough and we start composing **distributed pipelines, async fanout, persistent connections, and pre-computed read paths**. Web Crawler (a batch/throughput beast), Notification System (a fanout/decoupling exercise), News Feed (the canonical push-vs-pull dilemma), and Chat System (stateful connections at 50M scale) collectively cover nearly every pattern an interviewer can throw at you.

---

## Table of Contents

1. [Chapter 9 — Web Crawler](#chapter-9--web-crawler)
2. [Chapter 10 — Notification System](#chapter-10--notification-system)
3. [Chapter 11 — News Feed System](#chapter-11--news-feed-system)
4. [Chapter 12 — Chat System](#chapter-12--chat-system)
5. [Cross-Chapter Synthesis](#cross-chapter-synthesis)

---

## Chapter 9 — Web Crawler

### 9.1 Problem Statement and Requirements

A **web crawler** (also called a *robot* or *spider*) is a system that systematically browses the web, downloading pages and following hyperlinks to discover new content. The canonical use case is **search-engine indexing** (Googlebot), but crawlers are also used for:

- **Web archiving** — national libraries (Library of Congress, EU web archive) preserve snapshots.
- **Web mining** — financial firms scrape annual reports and shareholder materials.
- **Web monitoring** — copyright/trademark infringement detection (e.g., Digimarc).

**Functional requirements (clarified through Q&A):**
- Primary purpose: **search engine indexing**.
- Crawl volume: **1 billion pages per month**.
- Content type: **HTML only** (PDFs/images out of scope for v1).
- Must handle **newly added and edited pages** (recrawl).
- Must **store HTML pages for 5 years**.
- **Duplicate content must be ignored.**

**Non-functional requirements — "characteristics of a good crawler":**
- **Scalability** — web is billions of pages; must parallelize aggressively.
- **Robustness** — bad HTML, dead servers, malicious links, spider traps must not crash the crawler.
- **Politeness** — never flood a single host with too many requests/sec.
- **Extensibility** — minimal changes to support new content types (e.g., images later).

---

### 9.2 Back-of-the-Envelope Estimation

| Metric | Calculation | Value |
|--------|-------------|-------|
| Pages / month | given | 1,000,000,000 |
| QPS (avg) | 1B / (30·24·3600) | **~400 pages/sec** |
| Peak QPS | 2 × avg | **~800 pages/sec** |
| Avg page size | given | 500 KB |
| Storage / month | 1B × 500 KB | **500 TB / month** |
| 5-year storage | 500 TB × 12 × 5 | **30 PB** |

**Key takeaways:**
- Throughput target (~400 QPS sustained, 800 peak) is modest per-node but the *scale of state* (URL frontier, dedup sets, content store) is enormous.
- 30 PB demands a **distributed/object store** (S3/HDFS) — never a single DB.
- Network egress is the dominant cost driver — duplicate suppression and politeness both reduce it.

---

### 9.3 High-Level Architecture

The crawler is a **pipeline** of components, each doing one job well:

```
                         ┌──────────────┐
                         │  Seed URLs   │
                         └──────┬───────┘
                                ▼
                      ┌──────────────────┐
                      │   URL Frontier   │  (FIFO queues: to-download)
                      │   (prioritized   │
                      │    + polite)     │
                      └──────┬───────────┘
                             │ dequeues URLs
                             ▼
                ┌──────────────────────────┐
                │     HTML Downloader       │
                │   (HTTP, distributed,     │
                │    timeout, robots.txt)   │
                └──────┬──────────┬─────────┘
                       │          │
                       ▼          ▼
              ┌──────────────┐  ┌────────────────┐
              │ DNS Resolver │  │  Robots Cache  │
              │  (+ cache)   │  │                │
              └──────────────┘  └────────────────┘
                       │
                       ▼ (raw HTML)
              ┌──────────────────┐
              │ Content Parser   │  (validate, normalize)
              └────────┬─────────┘
                       ▼
                ┌──────────────┐    seen?
                │ Content Seen │──────► discard
                │    ? (hash)  │
                └──────┬───────┘
                       │ new
                       ▼
              ┌──────────────────┐
              │ Content Storage  │  (disk + hot mem cache)
              └──────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  URL Extractor   │  (parse <a href>)
              └────────┬─────────┘
                       ▼
                ┌──────────────┐
                │ URL Filter   │  (blacklist, extensions)
                └──────┬───────┘
                       ▼
                ┌──────────────┐    seen?
                │  URL Seen ?  │──────► discard
                │ (bloom/HT)   │
                └──────┬───────┘
                       │ new
                       ▼
                   back to URL Frontier
```

---

### 9.4 Detailed Component Design

#### 9.4.1 Seed URLs
Starting points for the crawl. For a whole-web crawl you partition URL space by **locality** (country-specific popular sites) or **topic** (shopping, sports, health). Seed selection is open-ended — "think out loud" — there's no perfect answer.

#### 9.4.2 URL Frontier
The FIFO queue of URLs to download. This is *the* central design problem because it must enforce **politeness**, **priority**, and **freshness** simultaneously. It is split into **front queues** (priority) and **back queues** (politeness) — see §9.4.3.

#### 9.4.3 URL Frontier — Politeness + Priority
The single most-tested crawler concept. Standard BFS over a FIFO has two bugs:
1. **Impoliteness** — links from one page mostly point to the same host (e.g., Wikipedia internal links). A naive parallel crawler hammers one origin server → effectively a self-DoS.
2. **No priority** — every URL is treated equal; an Apple homepage and a random forum post get the same crawl budget.

**Politeness design (back queues):**
```
   incoming URLs
        │
        ▼
   ┌──────────────┐        ┌────────────────────┐
   │ Queue Router │──┐     │   Mapping Table    │
   └──────────────┘  │     │ host → queue_id    │
                     │     └────────────────────┘
                     ▼
       ┌─────────┬─────────┬─────────┬─────────┐
       │  b1     │  b2     │  b3     │  ... bn │   (each queue:
       │ host A  │ host B  │ host C  │         │    one host only)
       └────┬────┴────┬────┴────┬────┴────┬────┘
            │         │         │         │
            ▼         ▼         ▼         ▼
       ┌──────────────────────────────────────┐
       │           Queue Selector             │
       │  (worker thread ↔ FIFO queue map)    │
       └──────┬─────────┬──────────┬──────────┘
              ▼         ▼          ▼
         [worker1]  [worker2]  [workerN]
          only pulls from its assigned queue;
          inserts delay between downloads
```
- **Queue router** guarantees each back queue `bi` contains URLs from a single host.
- **Mapping table** maps `hostname → queue_id`.
- **Worker threads** each pull from exactly one back queue, with a **delay** between downloads — guaranteeing one-at-a-time-per-host.

**Priority design (front queues):**
```
                       URLs
                        │
                        ▼
                ┌────────────────┐
                │   Prioritizer  │   compute priority
                │  (PageRank,    │   (traffic, freshness,
                │   traffic)     │    update freq)
                └───────┬────────┘
                        ▼
        ┌───────┬───────┬───────┬───────┐
        │  f1   │  f2   │  f3   │  ...  │   priority tiers
        │ high  │  med  │  low  │       │   (f1 highest)
        └───┬───┴───┬───┴───┬───┴───────┘
            │       │       │
            ▼       ▼       ▼
        ┌──────────────────────────┐
        │    Queue Selector        │
        │ biased random:           │
        │ P(f1) > P(f2) > P(f3)    │
        └────────────┬─────────────┘
                     │
                     ▼
              (into back queues)
```
- Each front queue `fi` has an assigned priority tier.
- **Queue selector** picks queues with a **biased random** so high-priority queues are selected more often.

**Combined URL Frontier** = front queues (priority) → prioritizer router → back queues (politeness) → workers.

#### 9.4.4 Freshness
Web pages change constantly. Recrawl strategies:
- Recrawl based on **update history** (pages that change hourly get crawled hourly).
- **Prioritize** important pages for more frequent recrawl.
- Detect changes via checksum/hash deltas to avoid re-storing unchanged pages.

#### 9.4.5 Storage for URL Frontier
- **Hundreds of millions of URLs** in a real search crawler.
- All-in-memory: not durable, doesn't scale.
- All-on-disk: slow, becomes I/O bottleneck.
- **Hybrid:** bulk URLs on disk + in-memory **buffers** for enqueue/dequeue, periodically flushed. This is essentially a write-ahead-log pattern.

#### 9.4.6 HTML Downloader
- Uses HTTP; respects `robots.txt` (cached, periodically refreshed).
- **Robots.txt example** (Amazon): `User-agent: Googlebot` / `Disallow: /creatorhub/*` — crawler must skip these.
- Performance optimizations:
  1. **Distributed crawl** — partition URL space across many servers running many threads each.
  2. **Cache DNS Resolver** — DNS is synchronous and slow (10ms–200ms); cache `domain→IP` and refresh via cron. Otherwise crawler threads block on each other's DNS lookups.
  3. **Locality** — co-locate crawl servers with target hosts geographically (faster downloads; applies to cache/queue/storage too).
  4. **Short timeout** — bail on slow/dead hosts to avoid wasting worker time.

#### 9.4.7 Robustness
- **Consistent hashing** to distribute load across downloaders (add/remove nodes cleanly).
- **Persist crawl state + data** so a crashed crawl can resume.
- **Exception handling** that doesn't crash the system.
- **Data validation** at every boundary.

#### 9.4.8 Extensibility
Plug in new modules without redesign:
- `PNG Downloader` module → image support.
- `Web Monitor` module → copyright infringement detection.

#### 9.4.9 Detect & Avoid Problematic Content
1. **Redundant content** — ~30% of web pages are duplicates. Detect via hash/checksum.
2. **Spider traps** — infinite URL depth (`/foo/bar/foo/bar/...`). Mitigate with max URL length; manually blacklist trap sites (no automatic algorithm fully solves this).
3. **Data noise** — ads, spam, code snippets; exclude via filters.

---

### 9.5 Database Schema

A crawler rarely uses a single RDBMS; the "schema" is more accurately a **set of stores**:

```sql
-- URL Frontier state (could be KV like RocksDB/LevelDB)
CREATE TABLE url_frontier (
    url           TEXT PRIMARY KEY,
    host          TEXT NOT NULL,
    priority      INT  NOT NULL,
    enqueued_at   BIGINT NOT NULL,
    last_crawled  BIGINT          -- null if never
);
CREATE INDEX idx_frontier_host ON url_frontier(host);
CREATE INDEX idx_frontier_prio ON url_frontier(priority, enqueued_at);

-- Already-visited URLs (Bloom filter or hash table; conceptually)
CREATE TABLE url_seen (
    url            TEXT PRIMARY KEY,
    content_hash   BYTEA,         -- checksum of last fetch
    first_seen     BIGINT,
    last_seen      BIGINT
);

-- Content metadata
CREATE TABLE page_metadata (
    url            TEXT PRIMARY KEY,
    content_hash   BYTEA NOT NULL,   -- for dedup
    status_code    INT,
    fetched_at     BIGINT NOT NULL,
    content_len    INT,
    storage_path   TEXT              -- pointer into object store
);

-- Content itself: object/blob storage (S3/HDFS), NOT a row store
--   path: s3://crawler-content/<shard>/<content_hash>.html
```

The "Content Seen?" component is conceptually `SELECT 1 FROM page_metadata WHERE content_hash = ?`.

---

### 9.6 API Design

A web crawler has no public user-facing API, but internally exposes control/admin APIs:

```
POST /admin/seeds
  Body: { "urls": ["https://example.com", ...] }
  → 202 { "job_id": "..." }

GET  /admin/stats
  → 200 { "pages_crawled": 1_002_341_987,
          "frontier_size": 18_432_119_002,
          "qps_current": 412,
          "dup_rate": 0.29 }

POST /admin/recrawl
  Body: { "url": "...", "priority": "high" }

GET  /content/{url_hash}
  → 200 <raw HTML bytes>      (with Last-Modified, ETag)

POST /admin/module/png_downloader/enable
```

Internal services call the **download queue** via message broker (Kafka/RabbitMQ) rather than REST.

---

### 9.7 Scaling Bottlenecks and Solutions

| Bottleneck | Symptom | Solution |
|-----------|---------|----------|
| **DNS resolution latency** | Threads block waiting on DNS; throughput collapses | Custom DNS cache (cron-refreshed); pre-resolve hot domains |
| **Single-host hammering (impoliteness)** | Origin servers rate-limit/ban you | Back queues + per-host worker mapping + inter-download delay |
| **Frontier I/O** | 100s of millions of URLs can't fit in RAM, disk is slow | Hybrid: disk for bulk + in-memory enqueue/dequeue buffers (WAL) |
| **Duplicate content (30% dup rate)** | Wastes 30% of storage + bandwidth | Content hashing + "Content Seen?" check before storage |
| **Spider traps** | Infinite loops, millions of bogus URLs | Max URL length + manual blacklisting + anomaly detection |
| **Downloader hotspot** | One shard handles a popular host | Consistent hashing across downloaders; rebalance on add/remove |
| **Network egress cost** | 30 PB in 5 years; bandwidth is the cost | Dedup at the edge, conditional GETs (If-Modified-Since), compression |
| **Single point of failure** | One crawler node dies → lost work | Persist crawl state to durable store; checkpoint; resume |

---

### 9.8 Specific Technologies Discussed

- **Message Queue / Kafka** — for decoupling downloader workers from frontier (implied by the distributed design).
- **Bloom filter** — probabilistic "URL Seen?" structure (space-efficient, false positives possible, no false negatives).
- **Hash table** — alternative deterministic "URL Seen?" / "Content Seen?" implementation.
- **Consistent hashing** — load distribution across downloader fleet (cross-ref Chapter 5).
- **Robots Exclusion Protocol (`robots.txt`)** — politeness standard.
- **Rabin fingerprinting / checksums** — content dedup.
- **PageRank** — priority signal.

---

### 9.9 Trade-offs

| Choice | Pro | Con |
|--------|-----|-----|
| **BFS vs DFS traversal** | BFS keeps depth bounded & predictable | BFS still impolite without frontier smarts |
| **In-memory frontier** | Fast enqueue/dequeue | Not durable, doesn't scale to 100M+ URLs |
| **Disk frontier** | Durable, scales | I/O-bound; becomes bottleneck |
| **Hybrid disk+buffer** | Best of both | Complexity of buffer-flush logic |
| **Bloom filter for URL Seen** | Tiny memory footprint | False positives → some URLs wrongly skipped |
| **Hash table for URL Seen** | Exact, no skips | Memory-heavy at 100M+ scale |
| **Distributed crawl** | Massive parallelism | Coordination overhead, network cost |
| **Caching DNS** | Eliminates per-request DNS latency | Stale entries → wrong IPs after DNS changes |

---

### 9.10 Interview Q&A — Web Crawler (5 questions)

**Q1: How do you ensure the crawler is "polite" to websites?**
A: Politeness means not overloading any single host. The URL Frontier uses **back queues** — one FIFO queue per host, mapped via a mapping table — with each **worker thread** bound to exactly one queue and a **delay** between downloads. This guarantees at most one in-flight request per host at a time and a configurable inter-request gap. We also respect `robots.txt` (cached, periodically refreshed) and use conditional GETs when recrawling.

**Q2: How do you detect and avoid spider traps?**
A: Spider traps (e.g., infinite URL depth `/foo/bar/foo/bar/...`) cause the crawler to loop forever. There is no perfect automatic detector. Mitigations: (1) cap maximum URL length, (2) cap maximum pages per host per crawl cycle, (3) anomaly detection — sites with abnormally high page counts get flagged, (4) manual blacklisting of confirmed traps. Some traps require human review.

**Q3: How do you avoid crawling duplicate content?**
A: ~29% of the web is duplicate content. After download + parse, we compute a **hash/checksum** of the page (e.g., Rabin fingerprint) and check a **"Content Seen?"** store. If the hash matches an existing entry, we discard the page. We also dedup at the **URL level** with a Bloom filter / hash table ("URL Seen?") so the same URL is never enqueued twice.

**Q4: How would you make the crawler scalable to billions of pages?**
A: Three layers: (1) **Distributed downloaders** with consistent hashing to partition URL space across hundreds of servers, each running multiple threads. (2) **Hybrid frontier storage** — bulk on disk, in-memory buffers for fast enqueue/dequeue. (3) **Decouple pipeline stages** with message queues (Kafka) so the downloader, parser, deduper, and URL extractor scale independently. Add checkpointing + persistent state so failed nodes can resume.

**Q5: How do you keep crawled data fresh?**
A: Recrawl on a schedule. Two signals drive recrawl priority: (1) **update history** — pages that change hourly recrawl hourly; static pages monthly. (2) **Page importance** — high PageRank / high-traffic pages recrawl more often. On recrawl, use conditional GETs (`If-Modified-Since` / `If-None-Match`) to skip unchanged pages and save bandwidth/storage.

---

### 9.12 Extended Deep-Dive: URL Frontier Internals

The URL Frontier is sophisticated enough to warrant a closer look. Here is the **complete data flow** combining priority (front queues) and politeness (back queues):

```
                         ┌─────────────┐
                         │  New URLs   │
                         │  (extracted │
                         │   + filtered)│
                         └──────┬──────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      Prioritizer      │
                    │  (PageRank, traffic,  │
                    │   update frequency)   │
                    └───────────┬───────────┘
                                │ assign priority tier
                                ▼
            ┌────────┬─────────┬─────────┬─────────┐
            │  f1    │  f2     │  f3     │  ...fn  │   FRONT QUEUES
            │ (high) │ (med)   │ (low)   │         │   (priority)
            └───┬────┴────┬────┴────┬────┴─────────┘
                │         │         │
                └─────────┼─────────┘
                          │ biased random select
                          ▼
                   ┌─────────────┐
                   │  Front→Back │
                   │   Router    │
                   └──────┬──────┘
                          │
                          ▼
            ┌────────┬─────────┬─────────┬─────────┐
            │  b1    │  b2     │  b3     │  ...bn  │   BACK QUEUES
            │host A  │host B   │host C   │         │   (politeness:
            │        │         │         │         │    one host each)
            └───┬────┴────┬────┴────┬────┴─────────┘
                │         │         │
                ▼         ▼         ▼
           [worker1] [worker2]  [workerN]
            pull + delay between pulls
```

**Why this two-tier design?** Front queues solve *what* to crawl next (priority). Back queues solve *how* to crawl politely (one host at a time, with delay). The router between them is the bridge.

**Memory vs disk trade-off for the frontier:**
- 100M+ URLs cannot fit in RAM.
- Disk-only is too slow for enqueue/dequeue at 400 QPS.
- **Hybrid:** keep enqueue/dequeue **buffers in memory**, periodically flush to disk. Essentially a write-ahead log — durable on flush, fast in between.

**Bloom filter vs hash table for "URL Seen?":**

| Approach | Memory (100M URLs) | False Positives | False Negatives | Lookup |
|----------|-------------------|-----------------|-----------------|--------|
| Bloom filter | ~100 MB (10 bits/URL) | Yes (~1%) | **No** (safe) | O(k) |
| Hash table | ~5–10 GB | No | No | O(1) avg |

Bloom filters are the standard choice — false positives just mean occasionally skipping a URL that *wasn't* actually seen, which is acceptable.

---

### 9.13 Robots.txt Deep-Dive

`robots.txt` (Robots Exclusion Protocol) is the politeness contract between sites and crawlers. Before crawling any host, fetch and cache its `robots.txt`:

```
# https://www.amazon.com/robots.txt (excerpt)
User-agent: Googlebot
Disallow: /creatorhub/*
Disallow: /rss/people/*/reviews
Disallow: /gp/pdp/rss/*/reviews
Disallow: /gp/cdp/member-reviews/
Disallow: /gp/aw/cr/
```

- **Cache robots.txt** to avoid re-fetching per request.
- **Periodically refresh** (e.g., daily) via cron.
- **Respect** `Crawl-delay` directives where present.
- Some sites serve **different rules per User-Agent** — your crawler must identify itself.

---

## Chapter 10 — Notification System

### 10.1 Problem Statement and Requirements

A **notification system** alerts users with important information — breaking news, product updates, events, offers. It has become indispensable: think Netflix "new episode," Slack @mention, banking SMS.

**Three notification types:**
1. **Mobile push notification** (iOS via APNS, Android via FCM)
2. **SMS message** (Twilio, Nexmo)
3. **Email** (Sendgrid, Mailchimp)

**Clarified requirements:**
- Support **all three** formats.
- **Soft real-time** — deliver ASAP, but slight delay under peak load is acceptable.
- **iOS, Android, web/desktop** devices.
- Notifications triggered by **client apps** or **server-side scheduled jobs**.
- **Users can opt-out.**
- Volume: **10M push / day, 1M SMS / day, 5M email / day** (16M total/day).

---

### 10.2 Back-of-the-Envelope Estimation

| Metric | Value |
|--------|-------|
| Total notifications / day | 16,000,000 |
| Avg QPS | 16M / 86400 ≈ **185/sec** |
| Peak QPS (×2–5) | ~500–1000/sec |
| Push / day | 10M |
| SMS / day | 1M |
| Email / day | 5M |

Notification payloads are small (KB), but the **third-party API latency** (APNS/FCM/Twilio) is the bottleneck — typically 50–500ms per call. A single server doing synchronous sends caps at ~tens of QPS.

---

### 10.3 High-Level Architecture (Initial)

```
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ Service 1│  │ Service 2│  │ Service N│   (microservices, cron jobs)
  └─────┬────┘  └─────┬────┘  └─────┬────┘
        │             │             │
        └─────────────┼─────────────┘
                      ▼
            ┌────────────────────┐
            │ Notification       │  (single server — SPOF!)
            │ Server             │
            └─────┬──────────┬───┘
                  │          │
        ┌─────────┘          └──────────┐
        ▼                               ▼
  ┌──────────┐                ┌──────────────┐
  │   DB     │                │   Cache      │
  └──────────┘                └──────────────┘
        │
        ▼
  ┌───────────────────────────────────────────┐
  │ Third-party services: APNS / FCM /        │
  │ Twilio / Sendgrid                         │
  └─────┬────────┬────────┬────────┬──────────┘
        ▼        ▼        ▼        ▼
      iOS      Android    SMS     Email
```

**Three problems with this naive design:**
1. **Single point of failure** — one notification server.
2. **Hard to scale** — DB, cache, and notification processing are coupled in one process.
3. **Performance bottleneck** — HTML rendering + waiting on third-party APIs blocks the single server under load.

---

### 10.4 High-Level Architecture (Improved — with Message Queues)

```
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │Service 1 │ │Service 2 │ │Service N │
  └────┬─────┘ └────┬─────┘ └────┬─────┘
       │            │            │
       └────────────┼────────────┘
                    ▼ POST /v3/sms/send  (internal API only)
          ┌──────────────────────┐
          │ Notification Servers │   (horizontally scaled;
          │  - validate          │    auth + rate-limit)
          │  - auth check        │
          │  - rate limit        │
          └─────┬──────────┬─────┘
                │          │
          ┌─────▼───┐ ┌────▼────┐
          │ Cache   │ │   DB    │  (user info, device tokens,
          │ (user,  │ │ (notif  │   templates, settings, log)
          │ device, │ │  log,   │
          │ templa.)│ │ setting)│
          └─────────┘ └─────────┘
                │
                ▼ (notification event)
   ┌──────────────────────────────────────────┐
   │              Message Queues              │
   │  ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐ │
   │  │ iOS  │ │ And  │ │ SMS  │ │  Email  │ │  (one queue per channel)
   │  │ PN Q │ │ PN Q │ │  Q   │ │    Q    │ │
   │  └──┬───┘ └──┬───┘ └──┬───┘ └────┬────┘ │
   └─────┼────────┼────────┼──────────┼──────┘
         ▼        ▼        ▼          ▼
   ┌──────────────────────────────────────┐
   │             Workers                  │   (pull events, send)
   └─────┬────────┬────────┬──────────────┘
         ▼        ▼        ▼
     [APNS]    [FCM]   [Twilio] [Sendgrid]
         │        │        │          │
         ▼        ▼        ▼          ▼
       iOS     Android    SMS       Email
```

**Why one queue per channel?** So an outage in (say) FCM doesn't block iOS/SMS/Email delivery — failures are isolated.

**Workflow:**
1. A service calls the notification server API.
2. Notification server fetches metadata (user info, device token, settings) from cache/DB.
3. A notification event is enqueued to the appropriate channel queue (e.g., iOS PN queue).
4. Workers pull events from the queue.
5. Workers call the third-party service.
6. Third-party service delivers to the user device.

---

### 10.5 Detailed Component Design

#### 10.5.1 Reliability — Preventing Data Loss
Notifications can be **delayed or re-ordered, but never lost.** This is the cardinal rule.
- **Persist notification data** in a notification log DB *before* sending.
- **Retry mechanism** — failed sends go back to the queue for retry.
- A **notification log table** records every send attempt and its status.

#### 10.5.2 Exactly-Once Delivery? No.
The short answer: **distributed systems cannot guarantee exactly-once delivery** (network partitions, retries, duplicates from third parties). We aim for **at-least-once** and add **deduplication**:
- Each notification event carries a unique **event_id**.
- On arrival, check if `event_id` was seen before → if yes, discard.
- This reduces (not eliminates) duplicates.

#### 10.5.3 Notification Template
Millions of notifications share similar formats. A **preformatted template** with parameter substitution avoids rebuilding each notification:
```
BODY: You dreamed of it. We dared it. [ITEM_NAME] is back — only until [DATE].
CTA:  Order Now. Or, Save My [ITEM_NAME]
```
Benefits: consistent format, fewer errors, faster authoring.

#### 10.5.4 Notification Settings (user opt-out)
Users can be overwhelmed. Fine-grained control stored per channel:
```sql
CREATE TABLE notification_setting (
    user_id   BIGINT,
    channel   VARCHAR(20),   -- 'push', 'email', 'sms'
    opt_in    BOOLEAN,
    PRIMARY KEY (user_id, channel)
);
```
Before sending, the system checks this table — if `opt_in = false`, the notification is suppressed.

#### 10.5.5 Rate Limiting
Cap notifications per user per time window (e.g., max 5/day). Prevents users from disabling notifications entirely out of annoyance. Implemented via token bucket / sliding window in Redis.

#### 10.5.6 Retry Mechanism
If a third-party service fails, the notification is **re-enqueued** with exponential backoff. After N retries, alert the dev team.

#### 10.5.7 Security in Push Notifications
`appKey` / `appSecret` authenticate API callers — only verified clients can send push notifications via our API. APIs are internal-only or behind auth to prevent spam.

#### 10.5.8 Monitor Queued Notifications
A key metric: **total queued messages**. A large backlog means workers can't keep up → autoscale more workers.

#### 10.5.9 Event Tracking
Analytics service tracks **open rate, click rate, engagement**. Integration with the notification system feeds a data pipeline (Kafka → analytics warehouse).

---

### 10.6 Database Schema

```sql
-- User table
CREATE TABLE users (
    user_id     BIGINT PRIMARY KEY,
    email       VARCHAR(255),
    phone       VARCHAR(32),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Device table (a user can have multiple devices)
CREATE TABLE devices (
    device_token  VARCHAR(255) PRIMARY KEY,
    user_id       BIGINT NOT NULL REFERENCES users(user_id),
    platform      VARCHAR(16) NOT NULL,   -- 'ios', 'android', 'web'
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at  TIMESTAMPTZ
);

-- Notification setting (opt-in per channel)
CREATE TABLE notification_setting (
    user_id   BIGINT,
    channel   VARCHAR(20),   -- 'push', 'email', 'sms'
    opt_in    BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (user_id, channel)
);

-- Notification log (the durability guarantee)
CREATE TABLE notification_log (
    notification_id  BIGINT PRIMARY KEY,    -- Snowflake ID
    user_id          BIGINT NOT NULL,
    channel          VARCHAR(20) NOT NULL,
    template_id      BIGINT,
    payload          JSONB,                 -- rendered body
    status           VARCHAR(16) NOT NULL,  -- 'queued','sent','failed','retried'
    attempts         INT DEFAULT 0,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    sent_at          TIMESTAMPTZ
);
CREATE INDEX idx_notif_log_status ON notification_log(status, created_at);

-- Templates
CREATE TABLE notification_template (
    template_id   BIGINT PRIMARY KEY,
    name          VARCHAR(128),
    channel       VARCHAR(20),
    body          TEXT,                     -- with [PLACEHOLDERS]
    locale        VARCHAR(8)
);
```

---

### 10.7 API Design

```
POST https://api.example.com/v3/sms/send
Headers: Authorization: Bearer <appKey+appSecret signature>
Body:
{
  "event_id": "uuid-...",          // for dedup
  "user_id": 42,
  "to": "+15551234567",            // or device_token for push
  "template_id": 7,
  "params": { "ITEM_NAME": "PS5", "DATE": "Dec 25" },
  "channel": "sms"
}
→ 202 Accepted
  { "notification_id": "...", "status": "queued" }

GET  /v3/notifications/{notification_id}
→ 200 { "status": "sent", "sent_at": "..." }

POST /v3/settings
Body: { "channel": "email", "opt_in": false }
```

**Internal-only access:** these endpoints are gated so external abusers can't spam.

---

### 10.8 Scaling Bottlenecks and Solutions

| Bottleneck | Solution |
|-----------|----------|
| Single notification server (SPOF) | Horizontal scaling behind LB |
| Coupled DB/cache/processing | Move DB+cache out; use MQ to decouple |
| Third-party API latency (50–500ms) | Async workers pull from MQ; non-blocking |
| One channel outage blocks others | **Separate queue per channel** (iOS/Android/SMS/Email) |
| Data loss on failure | Persist to `notification_log` before send; retry |
| Duplicate delivery | `event_id` dedup at worker |
| User overwhelm | Per-user rate limiting + opt-out settings |
| Worker backlog during peak | Autoscale workers; monitor queue depth |
| Spam / abuse | `appKey`/`appSecret` auth on all APIs |

---

### 10.9 Specific Technologies Discussed

- **APNS** (Apple Push Notification Service) — iOS push.
- **FCM** (Firebase Cloud Messaging) — Android push. *Unavailable in China → use JPush, Pushy.*
- **Twilio / Nexmo** — SMS.
- **Sendgrid / Mailchimp** — Email.
- **Message Queue (RabbitMQ / Kafka)** — decouple notification servers from workers, buffer peak load.
- **Cache (Redis)** — user info, device tokens, templates.
- **Analytics service** — open rate, click rate.

---

### 10.10 Trade-offs

| Choice | Pro | Con |
|--------|-----|-----|
| Sync send (call 3rd party inline) | Simple | Blocks; throughput-limited |
| Async MQ + workers | High throughput; isolates channel failures | Operational complexity |
| Per-channel queue | Failure isolation | More infra to manage |
| Single combined queue | Simpler | One slow channel blocks all |
| Exactly-once delivery | Ideal UX | **Impossible** in distributed systems |
| At-least-once + dedup | Achievable, near-ideal | Occasional duplicates |
| Build email/SMS server in-house | Control | Poor deliverability, no analytics |
| Use commercial (Sendgrid/Twilio) | Reliability, analytics | Cost + vendor lock-in |

---

### 10.11 Interview Q&A — Notification System (5 questions)

**Q1: How do you prevent data loss in the notification system?**
A: Two mechanisms. First, **persist every notification to a log table before attempting delivery** — the message is durable the moment it's written. Second, **retry** failed sends by re-enqueuing the message with exponential backoff. Even if a worker crashes mid-send, the message remains in the queue/log and is reprocessed. Combined with at-least-once semantics + dedup, this guarantees no notification is silently dropped.

**Q2: Can recipients receive a notification exactly once? Why or why not?**
A: No — exactly-once delivery is **impossible** in a distributed system (network partitions, duplicate ACKs, retry storms). We aim for **at-least-once** and add a **deduplication layer**: every event carries a unique `event_id`, and workers check a "seen events" set before sending. This collapses the vast majority of duplicates, but the system must tolerate the rare duplicate.

**Q3: Why do you use a separate message queue for each notification channel?**
A: **Failure isolation.** If FCM has an outage (common in some regions), we don't want iOS/SMS/Email delivery to stall behind a single clogged queue. Each channel has its own queue and worker pool, so a slow/failing third party only affects its own channel. Workers for healthy channels keep draining normally.

**Q4: How would you handle a notification surge (e.g., Black Friday)?**
A: The MQ acts as a buffer — notification servers enqueue events fast (just a DB write + enqueue), and workers drain at their own pace. We **monitor queue depth** as the key autoscaling signal: when backlog crosses a threshold, we add more workers. The notification log DB and cache must also be provisioned for peak. Rate limiting per user still applies to avoid spamming individuals even during a surge.

**Q5: How do you respect user notification preferences?**
A: A `notification_setting` table stores `(user_id, channel, opt_in)`. Before any send, the worker checks this table — if `opt_in = false` for that channel, the notification is suppressed and logged as `skipped`. Users can configure this granularly (push on, email off, SMS on). Combined with per-user rate limiting, this prevents notification fatigue and opt-outs.

---

### 10.12 Extended Deep-Dive: End-to-End Notification Lifecycle

Tracing a single notification from trigger to delivery clarifies how all the pieces interact:

```
1. Trigger
   ┌─────────────────┐
   │ Billing Service │  "payment due in 3 days for user 42"
   └────────┬────────┘
            │ POST /v3/sms/send
            ▼
2. Notification Server
   ┌─────────────────────────────────────────────┐
   │  - auth check (appKey/appSecret)            │
   │  - validate payload                         │
   │  - rate-limit check (user 42: 3/5 today OK) │
   │  - fetch template #7 from cache             │
   │  - render: "Your payment of $49 is due..."  │
   │  - check notification_setting (user 42,     │
   │    sms, opt_in=true) → proceed              │
   │  - WRITE notification_log row (status=      │
   │    'queued', event_id=uuid)                 │
   └────────┬────────────────────────────────────┘
            │ enqueue event
            ▼
3. Message Queue (SMS queue)
   ┌──────────────────┐
   │ [event_id, user, │  ← buffered; peak load absorbed
   │  rendered body]  │
   └────────┬─────────┘
            │ worker pulls
            ▼
4. Worker
   ┌─────────────────────────────────────────────┐
   │  - dedup: event_id seen before? → discard   │
   │  - call Twilio API with rendered body       │
   │  - Twilio responds 200 OK (msg sid=...)     │
   │  - UPDATE notification_log SET status=      │
   │    'sent', sent_at=now()                    │
   │  - emit analytics event (open_rate track)   │
   └─────────────────────────────────────────────┘
            │
            ▼ (if Twilio had failed)
   ┌─────────────────────────────────────────────┐
   │  - status='failed', attempts++              │
   │  - if attempts < MAX_RETRIES: re-enqueue    │
   │    with exponential backoff                 │
   │  - else: alert dev team                     │
   └─────────────────────────────────────────────┘
            │
            ▼
5. Delivery
   ┌─────────────────┐
   │  User's phone   │  SMS arrives
   └─────────────────┘
```

**Key observations:**
- The **notification log write happens before the queue** — durability is guaranteed the instant the API returns 202.
- **Dedup happens at the worker**, not the server, because retries can re-deliver the same event.
- **Analytics events** (delivered, opened, clicked) flow to a separate pipeline for open-rate/click-rate dashboards.
- **Backoff** prevents thundering-herd retries when a third party is down.

---

### 10.13 Channel-Specific Considerations

| Channel | Latency | Cost | Delivery Guarantee | Regional Notes |
|---------|---------|------|--------------------|----------------|
| **iOS Push (APNS)** | <1s | Free (Apple) | Best-effort | Global |
| **Android Push (FCM)** | <1s | Free (Google) | Best-effort | **Unavailable in China** → JPush/Pushy |
| **SMS (Twilio)** | 2–10s | $$/msg | High (carrier-grade) | Phone-number formatting per region |
| **Email (Sendgrid)** | seconds–minutes | Cheap | Soft (spam filters) | DKIM/SPF setup required |

**Extensibility principle:** the per-channel queue + worker abstraction means adding a new channel (e.g., WhatsApp Business API) is just *one more queue + worker* — no redesign.

---

## Chapter 11 — News Feed System

### 11.1 Problem Statement and Requirements

A **news feed** is the constantly updating list of stories in the middle of a user's home page — status updates, photos, videos, links, likes from people/pages/groups they follow. This is the canonical Facebook/Instagram/Twitter design question.

**Clarified requirements:**
- **Mobile + web** app.
- **Publish a post** and see friends' posts on the news feed.
- Sorted **reverse-chronologically** (keep it simple; ranked feed is out of scope).
- Up to **5000 friends** per user.
- **10 million DAU**.
- Feed can contain **images and videos** (media files).

---

### 11.2 Back-of-the-Envelope Estimation

| Metric | Value |
|--------|-------|
| DAU | 10,000,000 |
| Avg posts / user / day | ~10 (generous) |
| New posts / day | ~100,000,000 |
| Posts QPS (write) | ~1,200/sec |
| Feed reads / DAU / day | ~10 |
| Feed read QPS | ~12,000/sec (avg) |
| Avg post size (text + metadata) | ~1 KB |
| Avg media size | ~200 KB |
| Storage / day (posts) | 100M × ~1 KB = ~100 GB text |
| Storage / day (media) | varies; CDN offloads most |
| 5-year post storage | ~180 TB text |

**Read:write ratio** is heavily read-dominant (~10:1). This asymmetry is what justifies pre-computing feeds.

---

### 11.3 High-Level Architecture

Two flows: **feed publishing** and **news feed building**.

```
                        ┌───────────┐
                        │   User    │
                        └─────┬─────┘
                              │ POST /v1/me/feed?content=Hello
                              ▼
                      ┌───────────────┐
                      │ Load Balancer │
                      └───────┬───────┘
                              ▼
                      ┌───────────────┐
                      │  Web Servers  │  (auth, rate-limit, route)
                      └───────┬───────┘
                          ┌───┴───┐
                          ▼       ▼
                ┌─────────────┐   ┌──────────────────┐
                │ Post Service│   │ News Feed Service │
                │ (write DB)  │   │  (read cache)     │
                └──────┬──────┘   └─────────┬─────────┘
                       │                    │
                       ▼                    ▼
                ┌──────────────┐   ┌──────────────────┐
                │ Fanout       │   │ News Feed Cache  │
                │ Service      │   │ (post_id, user_id)│
                │ (push to     │   └──────────────────┘
                │  friends)    │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │ Notification │
                │ Service      │
                └──────────────┘
```

---

### 11.4 Detailed Component Design

#### 11.4.1 Web Servers
- Enforce **authentication** (valid `auth_token`).
- Enforce **rate limiting** to prevent spam/abuse.
- Route to internal services (post service, news feed service).

#### 11.4.2 Post Service
Persists the post to DB + cache. Simple write path.

#### 11.4.3 Fanout Service — THE Heart of the System
Fanout = delivering a post to all friends. Two models:

**Fanout-on-write (push):**
- New post is delivered to friends' caches immediately at write time.
- News feed is **pre-computed**.

**Fanout-on-read (pull):**
- News feed is generated at read time by querying friends' recent posts.
- **On-demand** model.

| Model | Pros | Cons |
|-------|------|------|
| **Push (write)** | Real-time feed; fast read (pre-computed) | **Hotkey problem** for users with many friends; wastes compute on inactive users |
| **Pull (read)** | Better for inactive users; no hotkey | Slow reads (not pre-computed) |

**Hybrid approach (what we use):**
- Push model for **majority of users** (fast reads).
- Pull model for **celebrities / users with many followers** (avoids hotkey overload).
- **Consistent hashing** distributes fanout work to mitigate hotkeys.

**Fanout service workflow:**
1. Fetch friend IDs from the **graph database** (Neo4j-style — optimized for friend relationships).
2. Get friends info from **user cache**, apply filters (muted users, restricted sharing).
3. Send friends list + new post ID to **message queue**.
4. **Fanout workers** pull from MQ and store `<post_id, user_id>` in the **news feed cache**.
5. Only IDs are stored (not full objects) to keep memory small. Cache has a configurable size limit (users rarely scroll past thousands).

#### 11.4.4 News Feed Retrieval
1. User requests `/v1/me/feed`.
2. LB → web servers → news feed service.
3. News feed service fetches **post IDs** from news feed cache.
4. Service **hydrates** the feed — fetches full user/post objects from user cache + post cache.
5. Media (images/videos) come from **CDN**.
6. Fully hydrated JSON returned to client.

---

### 11.5 Database Schema

```sql
-- Posts (sharded by post_id; snowflake ID)
CREATE TABLE posts (
    post_id      BIGINT PRIMARY KEY,        -- snowflake (time-sortable)
    user_id      BIGINT NOT NULL,
    content      TEXT,
    media_urls   JSONB,                     -- [url1, url2, ...]
    created_at   TIMESTAMPTZ NOT NULL,
    like_count   INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    is_deleted   BOOLEAN DEFAULT FALSE      -- tombstone
);
CREATE INDEX idx_posts_user_time ON posts(user_id, created_at DESC);

-- Users
CREATE TABLE users (
    user_id      BIGINT PRIMARY KEY,
    username     VARCHAR(64),
    display_name VARCHAR(128),
    avatar_url   TEXT,
    created_at   TIMESTAMPTZ
);

-- Friendship graph (in graph DB conceptually)
CREATE TABLE friendships (
    user_id      BIGINT,
    friend_id    BIGINT,
    status       VARCHAR(16),     -- 'active', 'muted', 'restricted'
    created_at   TIMESTAMPTZ,
    PRIMARY KEY (user_id, friend_id)
);
```

**News feed cache (Redis — the heart of read path):**
```
key:   feed:user:{user_id}
type:  ZSET
value: member = post_id,  score = created_at timestamp
       (keeps last ~1000 posts; older evicted)
```

---

### 11.6 API Design

```
POST /v1/me/feed
Params:
  content:    "Hello world"
  auth_token: <token>
  media:      [url1, url2]    (optional)
→ 201 { "post_id": "...", "created_at": "..." }

GET /v1/me/feed?cursor=<token>&limit=20
Params:
  auth_token: <token>
→ 200 { "posts": [...], "next_cursor": "..." }
```

---

### 11.7 Cache Architecture — 5 Layers

Cache is critical. Xu divides it into **5 tiers**:

| Layer | Stores | Purpose |
|-------|--------|---------|
| **News Feed** | `<post_id, user_id>` mappings per user | Pre-computed feed IDs |
| **Content** | Full post data; popular posts in **hot cache** | Hydrate feed efficiently |
| **Social Graph** | User relationship data | Friend lookups for fanout |
| **Action** | Like/reply/reshare state per user | Render interactions |
| **Counters** | Like count, reply count, follower/following | Avoid DB counts |

---

### 11.8 Scaling Bottlenecks and Solutions

| Bottleneck | Solution |
|-----------|----------|
| Celebrity fan-out (hotkey) | Hybrid: pull for celebrities, push for normal |
| Inactive users waste pre-compute | Pull model for cold users |
| News feed cache size | Store only IDs; cap feed length (~1000) |
| Slow hydration | Multi-tier cache; CDN for media |
| DB write throughput | Shard posts by `post_id` (snowflake) |
| Feed staleness | Async fanout through MQ; tombstones for deletes |
| Fanout worker backlog | Autoscale workers; monitor queue depth |
| Friend graph queries | Use graph DB (Neo4j) for relationship traversal |

---

### 11.9 Specific Technologies Discussed

- **Graph database (Neo4j)** — friend relationships, friend-of-friend recommendations.
- **Message Queue (Kafka)** — decouple fanout service from workers.
- **Fanout service** — the push/pull/hybrid decision engine.
- **Redis** — news feed cache (ZSET), content cache, user cache.
- **CDN** — media (images, videos) for fast retrieval.
- **Consistent hashing** — distribute fanout to avoid hotspots.

---

### 11.10 Trade-offs

| Choice | Pro | Con |
|--------|-----|-----|
| Push (fanout-on-write) | Fast reads (pre-computed) | Hotkey for celebs; waste on inactive |
| Pull (fanout-on-read) | No hotkey; good for inactive | Slow reads |
| Hybrid | Best of both | Operational complexity |
| Store IDs in feed cache | Small memory | Extra hydration step |
| Store full objects in cache | No hydration | Huge memory |
| Ranked feed | Better engagement | Much more complex (ML pipeline) |
| Reverse-chrono | Simple, predictable | Less relevant |

---

### 11.11 Interview Q&A — News Feed (5 questions)

**Q1: Explain the difference between fanout-on-write and fanout-on-read. Which would you choose?**
A: **Fanout-on-write (push)** pre-computes each friend's feed at post time — fast reads, but expensive for users with many followers (hotkey) and wasteful for inactive users. **Fanout-on-read (pull)** computes the feed at read time by querying friends' recent posts — cheap writes, no hotkey, but slow reads. I'd choose a **hybrid**: push for normal users (fast reads), pull for celebrities (avoid millions of writes per post). This is what production systems (Facebook/Twitter) actually do.

**Q2: How do you handle the celebrity (hotkey) problem?**
A: When a celebrity posts, pushing to millions of followers would saturate the fanout service. Solution: **detect celebrities** (e.g., follower count > threshold) and **skip the push** for them — store the post once. Followers pull the celebrity's recent posts on-demand at read time and merge with their pre-computed feed. **Consistent hashing** also helps distribute fanout load across workers.

**Q3: How do you keep the news feed cache memory-bounded?**
A: Store only **post IDs** in the feed cache (not full post objects) — `<post_id, user_id>` mappings. Set a configurable cap (~1000 posts per feed) since users rarely scroll past the latest content. Older entries are evicted (LRU or ZSET trim). Full post objects live in a separate content cache and are hydrated on read.

**Q4: What happens when a user deletes a post?**
A: The post is marked `is_deleted = TRUE` (tombstone) in the post store. The news feed cache is **not** scanned to remove it (too expensive). Instead, at read time, the feed service hydrates post IDs and **filters out tombstoned posts**. A background compaction job eventually removes tombstoned IDs from feed caches.

**Q5: How would you extend this to a ranked (non-chronological) feed?**
A: Add a **ranking pipeline**: post events → Kafka → ML model that scores each (user, post) pair based on signals (affinity, recency, popularity, post type). Replace the Redis ZSET score (currently `created_at`) with the rank score. The pre-computed feed becomes a ranked feed. This adds significant complexity (feature pipeline, model serving, A/B testing) but dramatically improves engagement.

---

### 11.12 Extended Deep-Dive: Fanout Service Internals

The fanout service is the most operationally complex component. Here is its internal architecture:

```
                    ┌─────────────────────┐
                    │  New post event     │
                    │  (post_id, user_id) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Fanout Service     │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
   ┌──────────────────┐  ┌──────────┐  ┌────────────────┐
   │ 1. Fetch friend  │  │ 2. Filter│  │ 3. Hybrid      │
   │    IDs from      │  │   friends│  │    decision    │
   │    Graph DB      │  │   (mute, │  │                │
   │   (Neo4j)        │  │    hide) │  │ celebrity?     │
   └──────────────────┘  └──────────┘  │  → pull instead│
                                        │  inactive?     │
                                        │  → skip push   │
                                        └───────┬────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │  Message Queue (Kafka)│
                                    │  (per-shard topic)    │
                                    └───────────┬───────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │   Fanout Workers      │
                                    │   (autoscaled)        │
                                    └───────────┬───────────┘
                                                │
                                                ▼
                                    ┌───────────────────────┐
                                    │  News Feed Cache      │
                                    │  (Redis ZSET/user)    │
                                    │  ZADD feed:user:{id}  │
                                    │     <ts> <post_id>    │
                                    └───────────────────────┘
```

**The hybrid decision logic (per friend):**
```
for each friend F of poster:
    if F.follows(poster) and not F.muted(poster):
        if poster.is_celebrity (followers > THRESHOLD):
            skip push — F will pull poster's recent posts at read time
        elif F.is_inactive (no login in 30 days):
            skip push — save compute
        else:
            enqueue (post_id, F.user_id) to fanout MQ
```

**Why a graph database for friend lookups?**
- Friend-of-friend queries ("people you may know") are O(depth) in a graph DB vs expensive joins in SQL.
- Neo4j / TigerGraph / custom (Facebook's TAO, Twitter's FlockDB) — optimized for adjacency traversals.
- The follow graph is read-heavy (every post triggers a fanout) and write-light (occasional follow/unfollow).

---

### 11.13 News Feed Cache — ZSET Structure

The Redis ZSET (sorted set) is the workhorse of the read path:

```
# Per-user feed, capped at ~1000 posts
ZADD feed:user:42  1625000005  post:555      # post 555, ts 1625000005
ZADD feed:user:42  1625000003  post:554
ZADD feed:user:42  1625000001  post:553

# Read top 20 most recent
ZRANGE feed:user:42 0 19 REV
→ [post:555, post:554, post:553, ...]

# Trim to last 1000 (evict old)
ZREMRANGEBYRANK feed:user:42 0 -1001

# Pagination (cursor-based)
ZRANGE feed:user:42 20 39 REV
```

**Why ZSET and not a list?**
- O(log N) insert, O(log N + M) range query — fast for both fanout writes and feed reads.
- Score (timestamp) gives free sorting — no separate sort step.
- Easy to cap size with `ZREMRANGEBYRANK`.
- Can replace score with a rank score for ranked feeds without schema change.

---

## Chapter 12 — Chat System

### 12.1 Problem Statement and Requirements

Design a chat app (Facebook Messenger / WhatsApp / WeChat style).

**Clarified requirements:**
- **1-on-1 chat + group chat** (max 100 members).
- **Mobile + web**.
- **50 million DAU**.
- Features: 1-on-1, group, **online indicator**, **multiple device support**, **push notifications**.
- **Text only** (no attachments for v1).
- Message size limit: **100,000 characters**.
- End-to-end encryption: **not required** (discuss if time allows).
- **Chat history stored forever.**

---

### 12.2 Back-of-the-Envelope Estimation

| Metric | Value |
|--------|-------|
| DAU | 50,000,000 |
| Concurrent users (≈ DAU × 30%) | ~15,000,000 |
| Messages / user / day | ~60 |
| Messages / day | ~3,000,000,000 |
| Msg QPS (write) | ~35,000/sec |
| Msg QPS (peak) | ~100,000/sec |
| Msg size (avg) | ~100 bytes (text) |
| Storage / day | 3B × 100B = ~300 GB/day |
| 5-year storage | ~550 TB |
| Memory per connection | ~10 KB |
| Memory for 1M concurrent conns | ~10 GB |

**Critical insight:** a single modern server *could* theoretically hold 1M connections (~10 GB RAM), but no production system does this — single point of failure is a deal-breaker.

---

### 12.3 Protocol Choice — Polling vs Long Polling vs WebSocket

The receiver side is the hard part: HTTP is client-initiated, but we need server→client push.

| Technique | How | Pros | Cons |
|-----------|-----|------|------|
| **Polling** | Client asks server every N seconds | Simple | Wasteful; most polls return empty; costly |
| **Long polling** | Client holds connection open until msg or timeout | Less wasteful than polling | Sender/receiver may hit different servers; can't detect disconnect cleanly; inefficient for idle users |
| **WebSocket** | Bidirectional, persistent connection upgraded from HTTP | True bidirectional; works through firewalls (port 80/443) | Requires stateful connection management |

**Decision: WebSocket** for both sender and receiver. Simplifies client/server design since the same protocol handles both directions.

> Note: WebSocket is only for real-time messaging. Login, signup, profile, etc. still use traditional HTTP request/response.

---

### 12.4 High-Level Architecture

Three service categories:

```
┌─────────────────────────────────────────────────────────────────┐
│                            Client                               │
│            (mobile + web, persistent WebSocket)                 │
└────────────┬────────────────────────────────────┬──────────────┘
             │ WebSocket (real-time)              │ HTTP (auth/profile)
             ▼                                    ▼
   ┌───────────────────┐               ┌─────────────────────┐
   │  Stateful Layer   │               │  Stateless Layer    │
   │                   │               │                     │
   │  ┌─────────────┐  │               │  ┌───────────────┐  │
   │  │ Chat Server │  │               │  │  API Server   │  │
   │  │ (msg relay) │  │               │  │ (login/signup)│  │
   │  └─────────────┘  │               │  └───────────────┘  │
   │                   │               │                     │
   │  ┌─────────────┐  │               │  ┌───────────────┐  │
   │  │ Presence    │  │               │  │ Service       │  │
   │  │ Server      │  │               │  │ Discovery     │  │
   │  │ (online/off)│  │               │  │ (Zookeeper)   │  │
   │  └─────────────┘  │               │  └───────────────┘  │
   └───────────────────┘               └─────────────────────┘
             │                                    │
             │                                    ▼
             │                          ┌──────────────────┐
             │                          │  Notification    │
             │                          │  Server (PN)     │
             │                          └──────────────────┘
             ▼
   ┌───────────────────┐
   │  Key-Value Store  │   (chat history — HBase/Cassandra)
   │  + Relational DB  │   (user profile, settings, friends)
   └───────────────────┘
```

- **Chat servers** — facilitate message sending/receiving (stateful, persistent connections).
- **Presence servers** — manage online/offline status (stateful).
- **API servers** — login, signup, profile (stateless, HTTP).
- **Notification servers** — push notifications when recipient offline.
- **Service discovery** (Zookeeper) — recommends best chat server for a client.
- **Key-value store** — chat history persistence.

---

### 12.5 Detailed Component Design

#### 12.5.1 Service Discovery (Zookeeper)
Primary role: **recommend the best chat server for a client** based on geography, capacity, etc.

```
1. User A logs in via app.
2. Load balancer → API servers (authenticate).
3. Service discovery finds best chat server for User A
   (e.g., Server 2 — geographically close, has capacity).
4. Server info returned to User A.
5. User A connects to Chat Server 2 via WebSocket.
```

#### 12.5.2 Message Flow — 1-on-1 Chat
```
User A sends "hi" to User B:

1. User A → Chat Server 1 (via WebSocket).
2. Chat Server 1 gets a message_id from ID generator (Snowflake).
3. Chat Server 1 sends the message to the message sync queue.
4. Message stored in key-value store.
5a. If User B online → message forwarded to Chat Server 2
    (where User B is connected) → forwarded to User B.
5b. If User B offline → push notification from PN servers.
6. Chat Server 2 → User B via persistent WebSocket.
```

#### 12.5.3 Message Sync Across Multiple Devices
Each device maintains `cur_max_message_id`. New messages for a user are those where:
- `recipient_id == current_user_id`, AND
- `message_id > cur_max_message_id` (on that device).

Each device independently pulls its delta from the KV store.

#### 12.5.4 Group Chat Flow
For small groups (≤100 members): **copy the message to each recipient's sync queue (inbox)**.

```
User A sends message in group {A, B, C}:
  → copy to User B's inbox (sync queue)
  → copy to User C's inbox (sync queue)

Each recipient just checks their own inbox for new messages.
```

This **write-amplification** is acceptable for small groups (WeChat caps at 500 with this model). For very large groups, a different strategy (e.g., read-amplification) is needed.

#### 12.5.5 Online Presence
**Presence servers** manage online/offline status via WebSocket.

**Flows that change status:**
- **Login** — WebSocket established → status = online, `last_active_at` saved in KV.
- **Logout** — explicit → status = offline.
- **Disconnection** (network drop) — naive approach (mark offline immediately) is bad because users flicker on/off (tunnels, weak signal). **Solution: heartbeat mechanism.**
  - Client sends a heartbeat every 5 seconds.
  - If no heartbeat within X seconds (e.g., 30s), mark offline.
  - Smooths out transient disconnects.

**Presence fanout** — pub/sub model:
```
Each friend pair has a channel (e.g., channel A-B).
When User A's status changes:
  → publish to channel A-B, A-C, A-D
Friends B, C, D subscribe to their respective channels
and receive the update via WebSocket.
```

For very large groups (100K members), fetching status only on entry/refresh avoids 100K events per status change.

---

### 12.6 Storage — Why Key-Value Store for Chat History

**Two data types:**
1. **Generic data** (user profile, settings, friends) → **relational DB** (replicated + sharded).
2. **Chat history** → **key-value store** (HBase, Cassandra).

**Why KV for chat history?**
- **Enormous volume** — Facebook/WhatsApp process 60 billion messages/day.
- **Only recent chats accessed frequently** — old data is cold.
- **Random access needed** occasionally (search, mentions, jump-to-message).
- **Read:write ratio ≈ 1:1** for 1-on-1 chat.
- **Horizontal scaling** is natural for KV stores.
- **Low latency** for data access.
- **Relational DBs struggle with the long tail** — large indexes make random access expensive.
- **Proven at scale** — Facebook Messenger uses HBase; Discord uses Cassandra.

---

### 12.7 Database Schema

#### Message table for 1-on-1 chat
```sql
-- Key-value store (Cassandra-style)
CREATE TABLE message_1to1 (
    message_id   BIGINT,         -- PK; snowflake (sortable by time)
    from_user_id BIGINT,
    to_user_id   BIGINT,
    content      TEXT,
    created_at   TIMESTAMPTZ,
    PRIMARY KEY (message_id)
);
-- Secondary index on (from_user_id, to_user_id) for conversation retrieval
```
`message_id` (not `created_at`) decides sequence — two messages can have the same timestamp.

#### Message table for group chat
```sql
CREATE TABLE message_group (
    channel_id   BIGINT,          -- partition key (group id)
    message_id   BIGINT,          -- clustering key (snowflake)
    sender_id    BIGINT,
    content      TEXT,
    created_at   TIMESTAMPTZ,
    PRIMARY KEY ((channel_id), message_id)
);
```
Composite PK `(channel_id, message_id)` — `channel_id` is the partition key because all group queries operate within a channel.

#### Message ID Generation
Requirements: **unique + sortable by time** (newer IDs > older IDs).

Options:
1. **MySQL `auto_increment`** — but NoSQL usually doesn't support this.
2. **Snowflake** (global 64-bit sequence generator) — Chapter 7.
3. **Local sequence number** — IDs unique only within a group/channel. Sufficient because message ordering only matters within a conversation. Easier to implement.

---

### 12.8 API Design

```
# Real-time messaging (over WebSocket, JSON frames)
{ "type": "message", "to": <user_id>, "content": "hi" }
{ "type": "message", "channel_id": <id>, "content": "hello group" }

# REST (stateless operations)
POST /api/v1/auth/login       → { token }
GET  /api/v1/users/{id}        → user profile
GET  /api/v1/messages?with=<user_id>&before=<msg_id>&limit=20   → history
POST /api/v1/groups            → create group
POST /api/v1/groups/{id}/members  → add member

# Presence (over WebSocket)
{ "type": "heartbeat" }
{ "type": "presence_update", "user_id": 42, "status": "online" }
```

---

### 12.9 Scaling Bottlenecks and Solutions

| Bottleneck | Solution |
|-----------|----------|
| **Single server SPOF** | Distributed chat servers; service discovery picks best per client |
| **Connection management** | WebSocket with efficient connection pooling; ~10 KB per connection |
| **Message ordering** | Snowflake IDs (time-sortable, unique) — not timestamps |
| **Multi-device sync** | `cur_max_message_id` per device; pull delta from KV |
| **Group write amplification** | Inbox-per-recipient model for small groups; read-amplification for large |
| **Presence flicker (tunnels)** | Heartbeat mechanism with X-second grace period |
| **Large group presence fanout** | Fetch status only on entry/refresh for huge groups |
| **Offline recipients** | Push notification via PN servers |
| **Chat server failure** | Zookeeper reassigns clients to a new chat server |
| **Message loss** | Persist to KV store before relay; retry + queue |
| **Search across history** | Secondary indexes / search index (Elasticsearch) on KV store |

---

### 12.10 Specific Technologies Discussed

- **WebSocket** — bidirectional persistent connection (port 80/443, firewall-friendly).
- **Polling / Long polling** — alternatives evaluated and rejected.
- **Zookeeper** — service discovery.
- **Snowflake** — distributed unique ID generator (Chapter 7).
- **HBase** — Facebook Messenger's chat history store.
- **Cassandra** — Discord's chat history store.
- **Heartbeat mechanism** — presence liveness.
- **Pub/Sub model** — presence fanout.
- **Push notification (APNS/FCM)** — offline message delivery (Chapter 10).
- **Keep-alive (HTTP)** — reduces TCP handshakes on sender side.

---

### 12.11 Trade-offs

| Choice | Pro | Con |
|--------|-----|-----|
| WebSocket (both directions) | Simple, bidirectional, firewall-friendly | Stateful connection management |
| HTTP + long polling | Works without WS support | Inefficient; messy disconnect handling |
| KV store for chat history | Horizontal scale, low latency | No transactions, eventual consistency |
| Relational DB for chat | ACID, familiar | Doesn't scale to billions of msgs/day |
| Inbox-per-recipient (group) | Simple sync for recipients | Write amplification |
| Single message store (group) | No write amplification | Complex read fanout |
| Global Snowflake IDs | Globally ordered | Coordination overhead |
| Local sequence IDs | Simple, no global coord | Not globally meaningful |
| Heartbeat-based presence | Smooths flicker | X-second delay before offline |

---

### 12.12 Interview Q&A — Chat System (5 questions)

**Q1: Why WebSocket over HTTP long polling for a chat system?**
A: WebSocket is **bidirectional and persistent** — once upgraded from HTTP, the server can push messages to the client at any time without the client polling. Long polling has three problems: (1) sender and receiver may hit different stateless servers (the message can't find the long-poll connection), (2) the server can't reliably detect client disconnects, (3) it's inefficient — idle users still trigger periodic reconnects after timeouts. WebSocket uses port 80/443 so it works through firewalls, and using it for both directions simplifies the design.

**Q2: How do you sync messages across a user's multiple devices?**
A: Each device maintains a `cur_max_message_id` — the highest message ID it has seen. When a device comes online, it queries the KV store for messages where `recipient_id == user_id AND message_id > cur_max_message_id`. Because each device has its own cursor, a phone and a laptop can independently pull their own deltas. This works because message IDs are monotonically increasing (Snowflake).

**Q3: How does the group chat message flow work? Why copy to each recipient's inbox?**
A: When User A sends a group message, the system **copies the message to each recipient's sync queue (inbox)** — one copy for B, one for C, etc. Each recipient only checks their own inbox to get new messages, which **simplifies the sync flow**. This is good for **small groups** (WeChat caps at 500) because the write amplification is acceptable. For very large groups, write amplification becomes prohibitive and a read-amplification model (single store, fanout at read) is better.

**Q4: How do you handle the online presence indicator, especially with flaky connections?**
A: Presence servers track status via WebSocket. The naive approach (mark offline on disconnect) fails because users flicker on/off (tunnels, weak signal). Solution: **heartbeat mechanism** — the client sends a heartbeat every 5 seconds; if the server doesn't receive one within X seconds (e.g., 30s), it marks the user offline. Status changes fan out to friends via a **pub/sub model** (each friend pair has a channel). For very large groups, status is fetched only on entry/refresh to avoid 100K events per change.

**Q5: Why use a key-value store instead of a relational database for chat history?**
A: Four reasons: (1) **Scale** — chat systems generate billions of messages/day (Facebook/WhatsApp: 60B/day); KV stores horizontally scale naturally. (2) **Access pattern** — only recent chats are hot; old data is cold, and KV stores handle this long tail well. (3) **Latency** — KV stores provide very low latency for the 1:1 read/write ratio of chat. (4) **Proven** — Facebook Messenger uses HBase, Discord uses Cassandra. Relational DBs struggle when indexes grow huge — random access becomes expensive. Generic data (profile, settings) still uses relational DBs with replication/sharding.

---

### 12.13 Extended Deep-Dive: WebSocket Connection Lifecycle

Understanding the WebSocket lifecycle clarifies why it's the right choice and where the complexity lives:

```
   Client                              Server
     │                                   │
     │ 1. HTTP GET /ws  (Upgrade: websocket)│
     │ ─────────────────────────────────►│
     │                                   │
     │ 2. HTTP 101 Switching Protocols   │
     │ ◄─────────────────────────────────│
     │                                   │
     │ ════════ WebSocket established ═══│  (now bidirectional)
     │                                   │
     │ 3. { "type":"message", "to":42,   │
     │      "content":"hi" }             │
     │ ─────────────────────────────────►│
     │                                   │
     │ 4. { "type":"message",            │
     │      "from":42, "content":"hey" } │
     │ ◄─────────────────────────────────│
     │                                   │
     │ 5. { "type":"heartbeat" }         │  (every 5s)
     │ ─────────────────────────────────►│
     │                                   │
     │ 6. { "type":"presence",           │
     │      "user":43,"status":"online"} │
     │ ◄─────────────────────────────────│
     │                                   │
     │ 7. TCP FIN / abnormal close       │  (network drop)
     │ ═════════════════════════════════│
     │                                   │
     │ 8. (server waits X=30s for        │
     │     heartbeat before marking      │
     │     user offline)                 │
```

**Why port 80/443 matters:** WebSocket upgrades from HTTP, so it uses the same ports as web traffic. This means it passes through **firewalls and proxies** that block non-standard ports — critical for enterprise/mobile networks.

**Connection management at scale:**
- Each connection holds ~10 KB of server memory (buffers, state).
- At 1M concurrent connections/server → ~10 GB RAM (theoretically feasible on one box, but never done in production — SPOF).
- A fleet of chat servers behind service discovery handles the real load.
- **Sticky connections:** once a client connects to Chat Server N, it stays there (stateful). Service discovery remembers the mapping.

---

### 12.14 Extended Deep-Dive: Presence Fanout Patterns

Presence updates must reach friends in real-time. The pub/sub model scales differently for different group sizes:

**Small friend list (typical, ≤500 friends):**
```
User A comes online:
   ┌─────────────┐
   │ Presence    │
   │ Server      │
   └──────┬──────┘
          │ publish
          ▼
   ┌──────────────────────────────────────┐
   │  Channels (one per friend pair)      │
   │                                      │
   │  channel A-B  →  User B subscribes   │
   │  channel A-C  →  User C subscribes   │
   │  channel A-D  →  User D subscribes   │
   │  ...                                 │
   └──────────────────────────────────────┘
          │
          ▼ (via WebSocket)
   Friends B, C, D see "A is online" instantly
```

**Large group (100K members) — the problem:**
- Each status change → 100K events → 100K WebSocket writes.
- A user toggling online/offline in a tunnel → floods the system.

**Solution for large groups:**
- **Don't fanout.** Instead, fetch presence **on-demand**: when a user opens the group member list or refreshes, the client queries current presence.
- This trades real-time accuracy for scalability — acceptable for large groups where per-member presence isn't critical.

**WeChat's approach (capped at 500 members):** uses the fanout model because 500 is manageable. Beyond that, the on-demand model kicks in.

---

### 12.15 Extended Deep-Dive: Message ID Generation Strategies

Message ordering is critical — messages must display in the order they were sent. The ID generator is surprisingly subtle:

| Strategy | Unique? | Time-Sortable? | Coordination | Use Case |
|----------|---------|----------------|--------------|----------|
| MySQL `auto_increment` | Global yes | Yes (monotonic) | Central DB (bottleneck) | Small scale only |
| **Snowflake** (64-bit) | Global yes | Yes | Decentralized (worker ID + datacenter ID) | **Large scale, global ordering** |
| Local sequence per channel | Within channel only | Yes | None (per-channel counter) | Chat (ordering only matters in-channel) |

**Snowflake ID structure (64 bits):**
```
| 1 bit  |  41 bits         | 10 bits      | 12 bits     |
| unused |  timestamp (ms)  | machine ID   | sequence    |
|        |  (~69 years)     | (1024 nodes) | (4096/ms)   |
```

**Why local sequence IDs work for chat:** message ordering only matters *within a conversation* (1-on-1 or group channel). There's no need for globally meaningful ordering. A per-channel counter is simpler — no Snowflake coordination, no cross-datacenter clock sync.

---

## Cross-Chapter Synthesis

These four chapters form a coherent arc about **scaling real-world distributed systems**. The patterns recur:

### Recurring Pattern 1: Message Queues for Decoupling
- **Notification System (Ch.10):** MQ decouples notification servers from workers; one queue per channel.
- **News Feed (Ch.11):** MQ decouples fanout service from fanout workers.
- **Chat System (Ch.12):** Message sync queue (inbox per recipient).
- **Web Crawler (Ch.9):** Implied — distributed downloaders coordinated via queues.

**Takeaway:** When a producer and consumer have different throughput characteristics, put a queue between them. The queue absorbs bursts, isolates failures, and lets each side scale independently.

### Recurring Pattern 2: Caching Is Mandatory at Scale
- **Web Crawler:** Hot content in memory; DNS cache; robots.txt cache.
- **News Feed:** 5-layer cache architecture (feed/content/graph/action/counters).
- **Chat System:** Recent messages cached client-side; presence in KV.
- **Notification System:** User info, device tokens, templates cached.

**Takeaway:** At scale, the DB is the source of truth but **never the read path**. Design multi-tier caching from the start.

### Recurring Pattern 3: Fanout — Push vs Pull
- **News Feed (Ch.11):** The canonical push-vs-pull dilemma. Hybrid for celebrities.
- **Notification System (Ch.10):** Push to multiple devices per user.
- **Chat System (Ch.12):** Group chat = fanout to each recipient's inbox; presence = pub/sub fanout.

**Takeaway:** Whenever one event must reach N recipients, you face the push-vs-pull decision. Push = fast reads, expensive writes (write amplification). Pull = cheap writes, slow reads. **Hybrid** based on recipient count is almost always the production answer.

### Recurring Pattern 4: Politeness / Rate Limiting
- **Web Crawler (Ch.9):** Per-host back queues + delays = don't hammer one server.
- **Notification System (Ch.10):** Per-user rate limiting = don't spam one user.
- **News Feed (Ch.11):** Rate-limit post creation to prevent spam.

**Takeaway:** Any system that touches an external endpoint (a website, a user, an API) needs rate limiting to avoid abuse/overload.

### Recurring Pattern 5: Deduplication and Exactly-Once
- **Web Crawler (Ch.9):** URL Seen (Bloom filter) + Content Seen (hash) to avoid re-crawling.
- **Notification System (Ch.10):** `event_id` dedup; at-least-once + dedup (exactly-once is impossible).
- **Chat System (Ch.12):** `cur_max_message_id` per device prevents re-delivery.

**Takeaway:** Distributed systems produce duplicates. Design dedup at the boundary, accept at-least-once semantics, and never promise exactly-once.

### Recurring Pattern 6: Stateful vs Stateless Services
- **Chat System (Ch.12):** Chat servers and presence servers are **stateful** (persistent WebSocket). API servers are **stateless**.
- **News Feed (Ch.11):** Web servers stateless; news feed cache holds the state.
- **Notification System (Ch.10):** Notification servers stateless; MQ + DB hold the state.

**Takeaway:** Keep as much of the system **stateless** as possible (easy to scale, no SPOF). Push state into dedicated stores (cache, KV, MQ). Only make a service stateful when the latency of stateless + external lookup is unacceptable (real-time connections).

### Recurring Pattern 7: Hybrid Storage
- **Web Crawler (Ch.9):** Disk for bulk URLs + in-memory buffers (hybrid frontier).
- **News Feed (Ch.11):** Graph DB for relationships + KV cache for feeds + RDBMS for posts.
- **Chat System (Ch.12):** RDBMS for profile/settings + KV store for chat history.

**Takeaway:** No single database wins. Pick the store that matches each workload's access pattern.

---

### Quick-Reference: Chapter → Core Concept

| Chapter | Core Concept | Killer Detail |
|---------|-------------|---------------|
| 9 — Web Crawler | URL Frontier (priority + politeness) | Back queues per host + front queues per priority tier |
| 10 — Notification System | MQ-decoupled fanout with retries | One queue per channel for failure isolation |
| 11 — News Feed | Push vs Pull (hybrid) | Celebrities pull; normal users push; consistent hashing mitigates hotkeys |
| 12 — Chat System | WebSocket + stateful servers | Heartbeat for presence; inbox-per-recipient for group chat; KV store for history |

---

### Final Notes for Interview Preparation

1. **Always start by clarifying scope.** Every chapter opens with Q&A. Ambiguity kills designs.
2. **Estimate first.** Back-of-the-envelope numbers drive every storage/caching decision.
3. **Draw the high-level architecture, then deep-dive.** Get buy-in before details.
4. **Identify the bottleneck.** Each chapter has *one* signature problem (frontier politeness, MQ decoupling, push-vs-pull, stateful connections).
5. **Discuss trade-offs explicitly.** "It depends" is the right answer — explain what it depends on.
6. **Know the technologies and *why* they're used.** APNS/FCM, Kafka, Redis, HBase, Cassandra, Zookeeper, Snowflake, WebSocket.
7. **Wrap up with scaling talking points** — sharding, replication, multi-DC, monitoring.

---

*Source: Alex Xu, *System Design Interview — An Insider's Guide* (Volume 1), Chapters 9–12.*
