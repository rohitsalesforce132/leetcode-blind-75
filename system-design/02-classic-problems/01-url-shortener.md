# System Design: URL Shortener (bit.ly / TinyURL)

> **Analogy:** A coat check at a museum. You hand them a long, bulky coat (your long URL), they give you a tiny numbered ticket (the short code). Anyone with that ticket can retrieve your coat instantly.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Requirements](#2-requirements)
3. [Back-of-Envelope Estimation](#3-back-of-envelope-estimation)
4. [API Design](#4-api-design)
5. [Component Design (Build-Up)](#5-component-design-build-up)
6. [Encoding: Base62](#6-encoding-base62)
7. [Database Schema](#7-database-schema)
8. [Architecture Diagram](#8-architecture-diagram)
9. [Cache Layer](#9-cache-layer)
10. [Bottlenecks & Trade-offs](#10-bottlenecks--trade-offs)
11. [Scaling Considerations](#11-scaling-considerations)
12. [Interview Q&A](#12-interview-qa)

---

## 1. Problem Statement

Design a URL shortening service like **bit.ly** or **TinyURL**. A user submits a long URL; the service returns a short, unique alias. When the short URL is visited, the service redirects the browser to the original long URL.

**Core flow:**
```
User → POST long_url=https://example.com/very/long/path?query=1
Service → returns https://bit.ly/aB3x9Q
User visits short URL → 301/302 redirect → original long URL
```

---

## 2. Requirements

### Functional Requirements
- Given a long URL, return a much shorter unique alias.
- Given a short URL, redirect to the original long URL.
- Short links are immutable (the same long URL may get different shorts, or optionally the same).
- Optional: user accounts, custom aliases, analytics, expiration links.

### Non-Functional Requirements
- **High availability** — redirects must work even during partial outages.
- **Low latency** — redirects must be fast (<100ms).
- **Unpredictable / unreadable** short codes (anti-enumeration).
- **Durability** — shortened links must not disappear.

### Out of Scope (for this walkthrough)
- Analytics dashboard, A/B redirect routing, monetization.

---

## 3. Back-of-Envelope Estimation

| Metric | Value |
|--------|-------|
| New URLs / month | 100 million |
| Read : Write ratio | 100 : 1 |
| Redirects / month | ~10 billion |
| QPS (writes) | ~40/sec (100M / 30d / 86400s) |
| QPS (reads) | ~4,000/sec (10B / 30d / 86400s) |
| URL record size | ~500 bytes |
| Storage / 10 years | 100M × 12 × 10 × 500B ≈ **6 TB** |
| Bandwidth (reads) | 4000 × 500B = **2 MB/sec** ingress, more for egress with response |

**Key takeaways:** read-heavy (100:1), storage is modest (~6TB over a decade), QPS is achievable on a single well-tuned DB but we want redundancy.

---

## 4. API Design

### 4.1 Create Short URL
```
POST /api/v1/data/shorten
Body: { "long_url": "https://example.com/..." , "custom_alias": "mylink" (optional) }
Response 201:
{ "short_url": "https://bit.ly/aB3x9Q", "long_url": "https://...", "created_at": "..." }
```

### 4.2 Redirect
```
GET /{short_code}
→ HTTP 301 (Permanent) or 302 (Temporary) redirect
   Location: https://example.com/...
```

**301 vs 302:**
- **301** — browser caches permanently; reduces load on our service but breaks analytics (no subsequent hits).
- **302** — always hits our service; enables click analytics but slightly higher latency.
- bit.ly uses **302** to count clicks. Choose based on analytics needs.

### 4.3 Optional APIs
```
GET  /api/v1/data/shorten/{short_code}      # resolve metadata
DELETE /api/v1/data/shorten/{short_code}     # deactivate (soft delete)
GET  /api/v1/data/analytics/{short_code}     # click stats
```

---

## 5. Component Design (Build-Up)

### 5.1 Naïve v0 — Single Server
```
┌────────────┐     ┌──────────────────┐     ┌──────────┐
│  Browser   │────▶│  API Server      │────▶│  MySQL   │
└────────────┘     │  (encode/decode) │     │  (KV)    │
                   └──────────────────┘     └──────────┘
```
Works for thousands of URLs. Single point of failure, no cache, no scale.

### 5.2 v1 — Add Cache
Reads dominate 100:1. Put Redis in front of MySQL for redirects.

```
┌────────────┐     ┌───────────┐     ┌─────────┐     ┌───────┐
│  Browser   │────▶│  LB / CDN │────▶│  API    │────▶│ Redis │
└────────────┘     └───────────┘     │  Server │────▶│ MySQL │
                                     └─────────┘     └───────┘
```
Cache hit → sub-ms redirect. Miss → MySQL lookup + backfill cache.

### 5.3 v2 — Scale Out
Multiple API servers behind a load balancer. MySQL primary + read replicas. Redis cluster.

---

## 6. Encoding: Base62

Short codes use `[a-zA-Z0-9]` = 62 characters.

| Short code length | Combinations | Enough for? |
|-------------------|--------------|-------------|
| 6 chars           | 62^6 ≈ 56.8 billion | ~50 years at 100M/yr |
| 7 chars           | 62^7 ≈ 3.5 trillion | effectively forever |

**Two approaches to generate codes:**

### 6.1 Hash + Collision Retry (MD5/SHA → Base62)
```
hash = MD5(long_url + user_id + timestamp)   # 128 bits
code = base62_encode(hash)[:7]
```
- Pros: stateless, deterministic.
- Cons: collisions possible → must check DB and retry with salt. First 7 chars of MD5 can collide at scale.

### 6.2 Auto-Increment ID → Base62 (Recommended)
```
id   = DB auto_increment
code = base62_encode(id)        # unique by construction
```
- Pros: no collisions ever, deterministic.
- Cons: **enumerable** — attackers can scrape all URLs. Mitigate with:
  - XOR with a secret key before encoding, or
  - A pre-generated "ticket dispenser" (a Kafka queue of random unused codes).

### Base62 Encode (pseudo)
```python
BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
def encode(n):
    if n == 0: return "0"
    s = ""
    while n > 0:
        s = BASE62[n % 62] + s
        n //= 62
    return s
```

---

## 7. Database Schema

### Option A — Single `urls` table (MySQL/PostgreSQL)
```sql
CREATE TABLE urls (
    id           BIGSERIAL PRIMARY KEY,         -- auto-increment
    short_code   VARCHAR(10) UNIQUE NOT NULL,
    long_url     TEXT NOT NULL,
    user_id      BIGINT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    expires_at   TIMESTAMPTZ,
    is_active    BOOLEAN DEFAULT true,
    click_count  BIGINT DEFAULT 0
);
CREATE INDEX idx_short_code ON urls(short_code);
```

### Option B — NoSQL (DynamoDB / Cassandra)
If we only need `short_code → long_url` lookups:
```
Table: urls
PK: short_code
Attributes: long_url, user_id, created_at, expires_at
```
Wide-column stores shine for pure KV lookups at this read ratio.

### Sharding
When MySQL grows beyond one box, shard by `short_code` hash:
```
shard = hash(short_code) % N
```
Keeps read traffic balanced. Cross-shard joins are rare (we don't need them).

---

## 8. Architecture Diagram

```
                        ┌──────────────────────────────────┐
                        │           Client / Browser        │
                        └───────┬────────────────┬──────────┘
                            shorten              redirect
                                │                    │
                                ▼                    ▼
                        ┌──────────────┐    ┌────────────────┐
                        │   DNS / CDN   │───▶│  Load Balancer  │
                        │  (CloudFront) │    │  (Anycast / ALB)│
                        └──────────────┘    └────────┬───────┘
                                                    │
                          ┌─────────────────────────┼─────────────────┐
                          ▼                         ▼                 ▼
                   ┌────────────┐           ┌────────────┐     ┌────────────┐
                   │ Write API   │           │ Read API    │ ... │ Read API    │
                   │ (shorten)   │           │ (redirect)  │     │ (redirect)  │
                   └──────┬─────┘           └──────┬──────┘     └──────┬──────┘
                          │                        │                   │
                          │   ┌────────────────────┘                   │
                          ▼   ▼                                          │
                   ┌────────────────┐    cache miss     ┌───────────────────┐
                   │  Redis Cluster  │────────────────▶│  MySQL Sharded    │
                   │  (short→long)   │◀────────────────│  (Primary + N      │
                   │  + hot cache    │   backfill      │   read replicas)   │
                   └────────────────┘                  └───────────────────┘
                          │
                          ▼
                   ┌────────────────┐
                   │ Analytics      │  ← async click events
                   │ (Kafka→S3/     │     (Kafka fire-and-forget)
                   │  ClickHouse)   │
                   └────────────────┘
```

---

## 9. Cache Layer

**Eviction:** LRU is the natural fit — recently created URLs get the most traffic.

**What to cache:** `short_code → long_url` only. Don't cache the full row.

**TTL:** Set a long TTL (e.g. 24h) but backfill on miss. Hot links will stay warm.

**Capacity:** With ~10B reads/month and a 100:1 ratio, the top ~1M short URLs cover the vast majority of traffic (Zipf distribution). A 1-4GB Redis cluster handles this easily.

---

## 10. Bottlenecks & Trade-offs

| Bottleneck | Impact | Mitigation |
|------------|--------|------------|
| DB writes (40 QPS) | Not a bottleneck yet | Auto-increment + shard when needed |
| DB reads (4K QPS) | Can saturate single primary | Read replicas + Redis cache (cache hit ratio >95%) |
| Cache stampede on viral link | Thundering herd | Single-flight / request coalescing, short TTL on negative cache |
| Enumeration attacks | All URLs scraped | XOR secret or ticket dispenser |
| Hot shard | Uneven load | Consistent hashing + virtual nodes |
| Single point of failure | Outage | Multi-AZ, read replicas, Redis failover |

---

## 11. Scaling Considerations

1. **Geo-distribution:** Deploy read replicas + Redis per region. Writes go to a single global primary (or region-local primaries with async merge).
2. **CDN edge caching:** Put 301/302 responses on CloudFront with a short TTL so viral redirects never hit origin.
3. **Database sharding:** Shard by `short_code` hash once a single MySQL can't keep up (~50K+ QPS read).
4. **Analytics pipeline:** Clicks fire events to Kafka → ClickHouse/S3. Never block redirects on analytics.
5. **Custom aliases:** Reserve a separate namespace; enforce length and uniqueness checks synchronously.
6. **Rate limiting:** Protect the `/shorten` endpoint (see 02-rate-limiter.md) to stop abuse.

---

## 12. Interview Q&A

**Q: How do you handle hash collisions?**
A: With auto-increment ID + Base62, collisions are impossible. With hash-based codes, on insert conflict, regenerate with a different salt and retry (bounded retries). Always have a DB UNIQUE constraint as the last line of defense.

**Q: 301 vs 302 — which do you pick?**
A: 302 for analytics (every click hits origin), 301 for pure performance and lower cost (browser caches). bit.ly uses 302. Discuss the trade-off explicitly.

**Q: What if two users shorten the same long URL?**
A: Decide policy: (a) always create a new short (simple, idempotent on write), or (b) dedupe via `long_url` lookup table. Option (a) is simpler and lets per-user analytics work.

**Q: How do you delete a link?**
A: Soft delete (`is_active=false`). The redirect endpoint checks this flag and returns 404 or 410 Gone. Cache entries must be invalidated.

**Q: Can you make short codes unpredictable but still unique?**
A: Yes — auto-increment the ID, then XOR with a secret counter or pass through a format-preserving encryption (FPE). Output looks random but is a bijection.

**Q: How would you shard the DB?**
A: Shard by `hash(short_code) % N` for balanced reads. Use consistent hashing so adding shards doesn't rehash everything. Writes go to a single primary per shard.

**Q: What happens if Redis goes down?**
A: Requests fall through to MySQL (which can handle the base load temporarily). Circuit breaker prevents cascading failure. Deploy Redis in sentinel/cluster mode for HA.

**Q: How do you support expiration?**
A: Store `expires_at`. On redirect, check it; lazy-delete via a background sweeper job. Don't rely on TTL alone since the row persists in MySQL.

**Q: Estimate storage for 10 years.**
A: 100M URLs/yr × 12 (we said 100M/mo) ... recompute: 100M/mo × 120 months × 500 bytes ≈ 6 TB. A single MySQL box with attached SSDs handles this; sharding adds headroom.

**Q: Why not just use a single giant hash table (e.g. DynamoDB)?**
A: You can — DynamoDB is a great fit for pure `short→long` KV. The trade-off is cost vs. control: self-managed MySQL is cheaper at scale; DynamoDB is ops-light. Pick based on team size.

---

## Summary

The URL shortener is a **read-heavy, storage-modest** system whose main scaling levers are **caching** and **database sharding**. The interesting design decisions are the **encoding scheme** (auto-increment vs hash), **redirect semantics** (301 vs 302), and **cache strategy** for viral links. Everything else is standard web-service scaling.
