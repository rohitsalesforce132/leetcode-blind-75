# System Design: Distributed Rate Limiter

> **Analogy:** A traffic cop at an intersection. Cars (requests) arrive in bursts. The cop lets a fixed number through per minute; the rest wait or are turned away. The "rules" (how many cars, how often) must be enforced consistently no matter which cop (server) a car happens to reach.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Requirements](#2-requirements)
3. [Back-of-Envelope Estimation](#3-back-of-envelope-estimation)
4. [API Design](#4-api-design)
5. [Algorithms](#5-algorithms)
6. [Single-Node Architecture](#6-single-node-architecture)
7. [Distributed Architecture](#7-distributed-architecture)
8. [Database / Storage Schema](#8-database--storage-schema)
9. [Bottlenecks & Trade-offs](#9-bottlenecks--trade-offs)
10. [Scaling Considerations](#10-scaling-considerations)
11. [Interview Q&A](#11-interview-qa)

---

## 1. Problem Statement

Design a **distributed rate limiter** that caps how many API requests a client (user, IP, API key) can make in a given time window. It must work across multiple servers — a client's Nth request must be rejected even if the previous N-1 hit different servers.

**Core flow:**
```
Client → API Gateway → Rate Limiter check → (allow) → Backend Service
                                              ↓ (deny)
                                          429 Too Many Requests
```

---

## 2. Requirements

### Functional Requirements
- Limit requests per client (by user ID, IP, API key, or combination) per time window.
- Support multiple limit types: per-second, per-minute, per-day, burst.
- Return clear rejection response with retry info (`Retry-After` header).
- Configurable limits per client / tier (free vs paid).

### Non-Functional Requirements
- **Low latency** — check must add <5ms; ideally <1ms.
- **High availability** — if the limiter is down, do we fail open or closed? (Usually fail-open to avoid outages.)
- **Eventually consistent** counters are acceptable for most use cases.
- **Scalable** — handle millions of clients, 100K+ RPS globally.

### Out of Scope
- Per-endpoint body-size limits, WAF / DDoS scrubbing (complementary systems).

---

## 3. Back-of-Envelope Estimation

| Metric | Value |
|--------|-------|
| Active API keys | 1 million |
| Requests / sec (peak) | 100,000 |
| Counter entry size | ~100 bytes (key + counts) |
| Hot keys in memory | ~1M keys × 100B = **100 MB** |
| Latency budget | <5ms end-to-end |
| Storage | Counters are ephemeral; TTL'd in Redis. Persistent audit log optional. |

**Key insight:** Rate limiting is a **hot-path, stateful** operation. The store must be in-memory and co-located or very close to the application.

---

## 4. API Design

### 4.1 Middleware / Library API
```python
allowed = rate_limiter.check(
    key="user:42",
    limit=100,
    window=60  # seconds
)
# returns: { "allowed": True/False, "remaining": 73, "retry_after": 12 }
```

### 4.2 HTTP Response Headers (expose to client)
```
X-RateLimit-Limit:     100
X-RateLimit-Remaining: 73
X-RateLimit-Reset:     1625000000
Retry-After: 12          # only on 429
```

### 4.3 Standalone Service API (if deployed separately)
```
POST /check
Body: { "key": "user:42", "limit": 100, "window": 60 }
→ 200 { "allowed": true, "remaining": 73 }
→ 200 { "allowed": false, "remaining": 0, "retry_after": 12 }
```

---

## 5. Algorithms

### 5.1 Token Bucket
> **Analogy:** A bucket holds tokens. Each request removes one token. Tokens drip in at a fixed rate. Empty bucket → deny.

```
        drip (refill)
          │
          ▼
      ┌───────┐
      │ ░░░░░ │  tokens (capacity = burst size)
      │ ░░░░░ │
      └───┬───┘
          │ consume 1 token per request
          ▼
       Request
```
- **Pros:** allows bursts up to bucket size; smooth average rate.
- **Cons:** requires storing `tokens` + `last_refill_time`.
- **Use case:** AWS API Gateway, Stripe.

**State:** `{ tokens: float, last_refill: timestamp }`

### 5.2 Leaky Bucket
> **Analogy:** A bucket with a hole. Requests pour in (may overflow → reject); they leak out at a constant rate.

```
       requests in
          │
          ▼
      ┌───────┐
      │ ▓▓▓▓▓ │ queue (FIFO)
      │ ▓▓░░░ │       │
      └───────┘       ▼
                   leak at constant rate → process
```
- **Pros:** smooths traffic to a perfectly constant outflow.
- **Cons:** adds latency (queue wait); memory for queue.
- **Use case:** traffic shaping on network links.

### 5.3 Fixed Window Counter
> Count requests in a fixed time window (e.g. 12:00–12:01). Reset at boundary.

```
Window 12:00:00 - 12:00:59:  count=98   ← allow
                          count=99   ← allow
                          count=100  ← allow
                          count=101  ← DENY
Window 12:01:00 - ...        count=0   ← reset
```
- **Pros:** simplest; one integer per key.
- **Cons:** **burst at edges** — 100 requests at 11:59:59 + 100 at 12:00:00 = 200 in one second.

### 5.4 Sliding Window Log
> Keep a sorted log of request timestamps. Drop entries older than the window. Reject if log size > limit.

```
now=100s, window=60s, limit=5
log = [42, 71, 88, 95, 99]  → keep only ≥40 → [42,71,88,95,99] (5) → next req DENY
```
- **Pros:** perfectly accurate.
- **Cons:** memory-heavy (log per key); O(N) cleanup. Rarely used in practice.

### 5.5 Sliding Window Counter (Hybrid) — Recommended
> Combine fixed windows. Estimate current window's weighted count.

```
prev_window_count = 80
curr_window_count = 20
elapsed_fraction  = 0.5 (halfway through current window)

estimated = prev_window_count × (1 - elapsed_fraction) + curr_window_count
          = 80 × 0.5 + 20 = 60
if estimated < limit(100): allow
```
- **Pros:** near-accurate, memory-light (2 integers).
- **Cons:** approximation (over-counts slightly at boundaries).
- **Use case:** most production systems (Cloudflare, LinkedIn).

---

## 6. Single-Node Architecture

```
┌──────────┐    ┌─────────────────────────┐
│  Client   │───▶│  App Server             │
└──────────┘    │  ┌───────────────────┐  │
                │  │ Rate Limiter      │  │
                │  │ (in-process,      │  │
                │  │  in-memory map)   │  │
                │  └───────────────────┘  │
                └─────────────────────────┘
```
- Works for a single server. State lives in process memory.
- **Breaks down** the moment you have >1 server behind a load balancer — client hits hit different nodes with independent counters.

---

## 7. Distributed Architecture

### 7.1 Redis-Backed (Most Common)
```
┌──────────┐    ┌─────────────┐    ┌────────────────┐    ┌──────────────┐
│  Client   │───▶│  Load       │───▶│  App Servers   │───▶│ Redis Cluster│
└──────────┘    │  Balancer   │    │  (rate limiter │    │ (shared      │
                └─────────────┘    │   library)     │    │  counters)   │
                                   └────────────────┘    └──────────────┘
```
Every app server reads/writes the **same** counter in Redis for a given key. Redis operations are atomic via Lua scripts.

**Redis Lua script for token bucket (atomic):**
```lua
-- KEYS[1] = bucket key
-- ARGV[1] = capacity, ARGV[2] = refill_rate, ARGV[3] = now, ARGV[4] = consume
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call("HMGET", key, "tokens", "ts")
local tokens = tonumber(bucket[1]) or capacity
local ts = tonumber(bucket[2]) or now

-- refill
local delta = math.max(0, now - ts)
tokens = math.min(capacity, tokens + delta * rate)

local allowed = tokens >= 1
if allowed then tokens = tokens - 1 end

redis.call("HMSET", key, "tokens", tokens, "ts", now)
redis.call("EXPIRE", key, math.ceil(capacity / rate) * 2)
return { allowed and 1 or 0, tokens }
```

### 7.2 Latency Optimization
A network round-trip to Redis adds 0.5–2ms. To hide it:
1. **Co-locate Redis** in the same AZ/datacenter as app servers.
2. **Local + global two-layer limiter**: allow 90% of limit locally (zero-RTT), check the remaining 10% against Redis. Reduces Redis load 10×.
3. **Connection pooling** to Redis (reuse connections).

### 7.3 Full Production Topology
```
                         ┌─────────────────────────────────────────────┐
                         │                  Internet                     │
                         └───────────┬─────────────────┬─────────────────┘
                                     │                 │
                              ┌──────▼──────┐   ┌──────▼──────┐
                              │  Edge / CDN  │   │  WAF / DDoS  │  (coarse limits)
                              └──────┬──────┘   └──────┬──────┘
                                     └────────┬────────┘
                                              ▼
                                     ┌────────────────┐
                                     │  API Gateway    │  (per-key limits,
                                     │  (Kong / Envoy) │   plugin-based)
                                     └────────┬───────┘
                                              │
                         ┌────────────────────┼────────────────────┐
                         ▼                    ▼                    ▼
                  ┌────────────┐       ┌────────────┐       ┌────────────┐
                  │ App Server  │       │ App Server  │  ...  │ App Server  │
                  │ + Limiter   │       │ + Limiter   │       │ + Limiter   │
                  │  library    │       │  library    │       │  library    │
                  └──────┬─────┘       └──────┬─────┘       └──────┬─────┘
                         │                    │                    │
                         └────────────────────┼────────────────────┘
                                              ▼
                                     ┌────────────────┐
                                     │ Redis Cluster   │  (6 nodes, 3 primary
                                     │ (shared state)  │   + 3 replica)
                                     └────────────────┘
                                              │
                                              ▼ (async, best-effort)
                                     ┌────────────────┐
                                     │ Analytics sink  │  (Kafka → ClickHouse)
                                     │ for audit/metering│
                                     └────────────────┘
```

---

## 8. Database / Storage Schema

Rate limiting state is **ephemeral** — no durable DB needed for counters. But we need durable config:

### Config Store (PostgreSQL / etcd)
```sql
CREATE TABLE rate_limit_rules (
    id            SERIAL PRIMARY KEY,
    client_id     BIGINT,           -- null = global rule
    api_key       VARCHAR(64),
    limit_type    VARCHAR(20),      -- 'token_bucket', 'sliding_window', ...
    limit_value   INT,              -- e.g. 100
    window_seconds INT,             -- e.g. 60
    tier          VARCHAR(20),      -- 'free', 'pro', 'enterprise'
    created_at    TIMESTAMPTZ DEFAULT now()
);
```

### Redis Key Layout (ephemeral state)
```
rl:{key}:{window_bucket}  →  integer counter   (SET with TTL)
rl:tb:{key}               →  hash {tokens, ts} (token bucket state)
```

---

## 9. Bottlenecks & Trade-offs

| Bottleneck | Impact | Mitigation |
|------------|--------|------------|
| Redis hot key | A single viral API key saturates one Redis shard | Local caching + two-layer limiter; "token bank" sampling |
| Redis network RTT | Adds 1–3ms per check | Co-location; pipeline; local layer |
| Synchronization / race conditions | Two servers allow simultaneously | Lua scripts / `INCR` atomicity; accept small over-counting |
| Clock skew across servers | Window boundaries drift | Use Redis server clock (single source of truth) |
| Fail-open vs fail-closed | If Redis down, allow all or deny all? | **Fail-open** for availability (log + alert); fail-closed for billing-critical |
| Memory growth | Millions of keys | TTL every key; eviction policy = `allkeys-lru` |

### Accuracy vs Availability
Rate limiting is inherently approximate in distributed systems. Options on a spectrum:
- **Exact** — distributed lock per key (slow, kills throughput).
- **Strong** — Redis atomic Lua (fast, ~99% accurate).
- **Weak** — local counters + periodic sync (fastest, ~90% accurate).
Pick based on whether you're protecting revenue (strong) or just smoothing traffic (weak).

---

## 10. Scaling Considerations

1. **Redis clustering:** Shard by key hash. A 6-node cluster handles 100K+ ops/sec.
2. **Geo-distributed limits:** If limits are global, route all checks to one region's Redis (latency cost) or accept per-region limits that sum loosely.
3. **Async config sync:** Push rule changes via pub/sub; each app server caches locally.
4. **Shadow mode:** Run a new limiter in parallel, log disagreements before cutover.
5. **Observability:** Emit metrics on allow/deny ratio, p99 latency, Redis errors. Alert if deny rate spikes (possible mis-config) or drops to zero (limiter dead).

---

## 11. Interview Q&A

**Q: Why Redis and not MySQL for counters?**
A: MySQL row-lock contention on `UPDATE counter SET c=c+1` at 100K QPS kills throughput. Redis is in-memory with atomic single-threaded ops (`INCR`, Lua scripts) — orders of magnitude faster.

**Q: What if Redis goes down?**
A: Default to **fail-open** (allow all requests, log them) to avoid a total outage of the protected service. Optionally fail-closed if the service is billing-sensitive. Always alert on Redis unavailability.

**Q: How do you handle the burst-at-window-edge problem?**
A: Use the **sliding window counter** (hybrid) or **token bucket** algorithm. Both smooth traffic across boundaries. Fixed-window counter has the edge-burst issue.

**Q: How accurate does rate limiting need to be?**
A: Usually within a few percent is fine. Over-counting slightly (allowing 102/100) is safer than under-counting (blocking paying users). Token bucket naturally errs on the side of allowing small bursts.

**Q: How do you limit by IP when clients are behind a NAT / corporate proxy?**
A: IP-based limits are coarse. Combine with user ID or API key. For anonymous traffic, IP is the only option — accept over-blocking of NAT'd users or raise the IP limit.

**Q: Can you do rate limiting entirely client-side?**
A: No — clients are untrusted. Client-side "remaining quota" hints (via headers) are UX aids, not enforcement. Enforcement must be server-side.

**Q: How do you handle "token bank" for long-idle clients?**
A: Token bucket naturally handles this — a client that hasn't called for an hour arrives to a full bucket (up to capacity). This is desirable: rewards idle clients with burst capacity.

**Q: How would you implement this as a library vs a service?**
A: **Library** (sidecar / in-process) is lower latency but each instance tracks only its own traffic → need shared store. **Service** (standalone) centralizes logic but adds a network hop. Most teams use a library + shared Redis.

**Q: What's the difference between rate limiting and throttling?**
A: Often used interchangeably. "Throttling" sometimes implies *shaping* (slowing down) rather than hard-rejecting. "Rate limiting" usually means hard reject (429). Align on definitions with your interviewer.

**Q: How do you test a rate limiter?**
A: (1) Unit-test the algorithm with mocked clock. (2) Load test with thousands of concurrent clients hitting the same key. (3) Chaos test: kill a Redis node, verify fail-open behavior.

---

## Summary

A distributed rate limiter's core challenge is **shared state across nodes**. The winning combination for most systems is the **token bucket** or **sliding window counter** algorithm backed by **Redis with atomic Lua scripts**, fronted by an in-process library that adds a local layer to reduce Redis load. The key trade-off is **accuracy vs availability** — and in most cases, failing open is the right call to protect the overall system.
