# Alex Xu Vol 1 — Distributed Systems Design (Chapters 4-8)

> **Source:** "System Design Interview — An Insider's Guide (2nd Edition)" by Alex Xu
> **Coverage:** Rate Limiter, Consistent Hashing, Key-Value Store, Unique ID Generator, URL Shortener

---

## Chapter 4: Design a Rate Limiter

### Problem Statement

Control the rate of client requests to an API. If requests exceed the threshold, excess calls are blocked (HTTP 429).

**Real-world examples:**
- User can write max 2 posts per second
- Max 10 account creations per day per IP
- Max 5 reward claims per week per device

**Why rate limit?**
1. Prevent DoS attacks (resource starvation)
2. Reduce cost (fewer API calls to paid third-party services)
3. Prevent server overload from bots/misbehavior

### Requirements

```
FUNCTIONAL:
  • Limit excessive requests accurately
  • Support different rate-limit rules (per user, per IP, per API)

NON-FUNCTIONAL:
  • Low latency (don't slow down API response time)
  • Minimal memory usage
  • Distributed rate limiting (shared across servers)
  • Clear exception messages for throttled users
  • High fault tolerance (rate limiter failure ≠ system failure)
```

### Where to Put the Rate Limiter?

```
OPTION 1: Client-side
  ❌ Unreliable — clients can be forged/malicious

OPTION 2: Server-side (in application code)
  ✓ Full control of algorithm
  ✓ No external dependency
  ❌ Takes engineering time to build

OPTION 3: API Gateway (middleware)
  ✓ Supports rate limiting, SSL termination, auth, IP whitelisting
  ✓ Managed service (AWS API Gateway, Kong, etc.)
  ❌ Less control over algorithm
  ❌ Vendor lock-in
```

### The 5 Rate Limiting Algorithms

#### Algorithm 1: Token Bucket

```
┌───────────────────────┐
│    TOKEN BUCKET       │
│    Capacity: 4        │   Refiller adds 2 tokens/sec
│    ┌─┐┌─┐┌─┐┌─┐      │   If full, extra tokens overflow
│    │T││T││T││T│      │
│    └─┘└─┘└─┘└─┘      │
│                       │   Each request consumes 1 token
│  Tokens: 4/4 (FULL)   │   If no token → request dropped
└───────────────────────┘

Parameters:
  • bucket_size: max tokens allowed
  • refill_rate: tokens added per second

Pros: Allows bursts, memory efficient, easy to implement
Cons: Two parameters to tune (bucket_size and refill_rate)

USED BY: Amazon, Stripe
```

#### Algorithm 2: Leaking Bucket

```
┌───────────────────────┐
│   LEAKING BUCKET      │
│   (FIFO Queue)        │
│                       │
│   → Request 4         │   Requests enter queue
│   → Request 5         │   Processed at FIXED rate
│   → Request 6         │   If queue full → drop
│   ───────────────     │
│   → Processing...     │   Outflow rate: 2 req/sec
└───────────────────────┘

Parameters:
  • bucket_size: queue capacity
  • outflow_rate: fixed processing rate

Pros: Smooth traffic, fixed outflow rate
Cons: Bursts fill queue, recent requests may be dropped

USED BY: Shopify
```

#### Algorithm 3: Fixed Window Counter

```
Time:  |--- 2:00:00 ---|--- 2:01:00 ---|--- 2:02:00 ---|
Count:        3/3 (max)       3/3 (max)       2/3

PROBLEM: At 2:00:59, 5 requests arrive.
         At 2:01:01, 5 more arrive.
         In the 2-second window 2:00:59→2:01:01: 10 requests!
         That's 2× the limit in a rolling 1-second window.

Pros: Memory efficient, simple
Cons: Traffic spike at window boundaries allows 2× the limit

FIX: Sliding Window (below)
```

#### Algorithm 4: Sliding Window Log

```
Keep a sorted log of request timestamps.

When a new request arrives:
  1. Remove all timestamps older than the current window
  2. Add new timestamp to log
  3. If log size ≤ allowed count → ACCEPT
  4. Else → REJECT

Example (2 requests/min limit):
  Timeline: [1:00, 1:10, 1:20, 1:45, 2:00]
  At 2:00: remove timestamps < 1:00 → [1:00, 1:10, 1:20, 1:45, 2:00]
  Count = 5 > 2 → REJECT

Pros: Very accurate (no boundary problem)
Cons: Memory intensive (stores every timestamp)
```

#### Algorithm 5: Sliding Window Counter (RECOMMENDED)

```
Hybrid of Fixed Window + Sliding Window Log.

Formula:
  estimated_count = count_in_previous_window × overlap_percentage
                    + count_in_current_window

Example: 100 requests/min limit
  Previous window (1:00-2:00): 84 requests
  Current window (2:00-2:00:30): 12 requests (30% into window)

  estimated = 84 × (1 - 0.5) + 12 = 42 + 12 = 54
  54 < 100 → ACCEPT

Pros: Smooth, memory efficient (only store 2 counters per window)
Cons: Approximation (assumes uniform distribution)

THIS IS THE RECOMMENDED ALGORITHM — best balance of accuracy and efficiency.
```

### High-Level Architecture

```
┌────────┐      ┌──────────────────┐      ┌──────────┐
│ Client │─────>│  Rate Limiter    │─────>│ API Server│
│        │      │  Middleware      │      │          │
└────────┘      │                  │      └──────────┘
                │  ┌────────────┐  │
                │  │ Redis      │  │
                │  │ (counter   │  │
                │  │  store)    │  │
                │  └────────────┘  │
                └──────────────────┘

Flow:
  1. Client sends request
  2. Rate limiter checks Redis for counter
  3. If under limit → forward to API server
  4. If over limit → return HTTP 429
  5. Redis stores: user_id → counter, updated per window
```

### Distributed Rate Limiting

```
PROBLEM: With multiple rate limiter instances, each has its own counter.
  User hits Instance 1 (counter=1), then Instance 2 (counter=1).
  Both allow the request. Total: 2 requests when limit is 1.

SOLUTION: Shared Redis store. All instances read/write the same counter.

CHALLENGE: Race condition. Two instances check Redis simultaneously,
  both see counter < limit, both increment.

FIX: Redis Lua script for atomic check-and-increment:
  if current_count < limit then
      increment counter
      return ALLOW
  else
      return DENY
  end
```

### Interview Q&As

**Q: "Which rate limiting algorithm would you choose?"**

"Sliding window counter. It's the best balance of accuracy and memory efficiency. It combines the memory savings of fixed window (only stores 2 counters) with the accuracy of sliding window log (smooth transitions between windows). Token bucket is a close second for APIs that need to handle bursts."

**Q: "How do you handle rate limiting in a distributed environment?"**

"I use Redis as a shared counter store. All rate limiter instances read and write to the same Redis. To handle race conditions where two instances check the counter simultaneously, I use a Redis Lua script for atomic check-and-increment. The script checks the counter and increments it in a single Redis operation — no other request can interfere."

**Q: "What happens if the Redis goes down?"**

"If Redis fails, I fall back to a per-instance counter with a circuit breaker. Each instance tracks its own count temporarily. This allows some over-limiting (not great), but keeps the system available. When Redis recovers, instances sync their counts. I prefer availability over perfect rate limiting — a slightly over-limit request is better than a complete service outage."

---

## Chapter 5: Design Consistent Hashing

### The Rehashing Problem

```
Traditional approach: hash(key) % N (N = number of servers)

  4 servers: hash(key) % 4
  ┌─────────┬──────────┬──────────┐
  │ Key     │ hash     │ Server   │
  │ key0    │ 183      │ 183%4=3  │ Server 3
  │ key1    │ 23       │ 23%4=3   │ Server 3
  │ key2    │ 199      │ 199%4=3  │ Server 3
  │ key3    │ 5        │ 5%4=1    │ Server 1
  └─────────┴──────────┴──────────┘

PROBLEM: If Server 1 goes offline → N changes from 4 to 3
  Now: hash(key) % 3 gives DIFFERENT results for almost ALL keys!

  ┌─────────┬──────────┬──────────┐
  │ Key     │ hash     │ Server   │
  │ key0    │ 183      │ 183%3=0  │ Server 0 (was Server 3!)
  │ key1    │ 23       │ 23%3=2   │ Server 2 (was Server 3!)
  │ key2    │ 199      │ 199%3=1  │ Server 1 (was Server 3!)
  │ key3    │ 5        │ 5%3=2    │ Server 2 (was Server 1!)
  └─────────┴──────────┴──────────┘

  → Nearly ALL keys are remapped. Cache miss storm!
  → Only k/n keys should be remapped, but hash%N remaps nearly all.
```

### Consistent Hashing Solution

```
STEP 1: Create a hash ring (0 to 2^160 - 1)

         Server 0
        /         \
       /           \     Server 1
      /             \   /
     /               \ /
    0 ──────────────── 2^160

STEP 2: Map servers onto the ring using hash(server_IP)

         Server 0 (hash: 10%)
        /         \
       /           \     Server 1 (hash: 70%)
      /             \   /
     /               \ /
    0 ──────────────── 100%

STEP 3: Map keys onto the ring using hash(key)

    key3 (5%)     key0 (15%)
         Server 0 (10%)
            ↓
         key3 → goes clockwise → Server 0

STEP 4: Key lookup — go CLOCKWISE from key until you find a server

  key3 (5%) → clockwise → Server 0 (10%) → stored on Server 0
  key0 (15%) → clockwise → Server 1 (70%) → stored on Server 1
  key1 (55%) → clockwise → Server 1 (70%) → stored on Server 1
  key2 (85%) → clockwise → Server 0 (10%, wrap around) → Server 0
```

### Adding/Removing Servers

```
ADD Server 4 (at 40%):
  Before: key3(5%)→S0, key0(15%)→S1, key1(55%)→S1, key2(85%)→S0
  After:  key3(5%)→S0, key0(15%)→S4 ← CHANGED!, key1→S1, key2→S0

  Only key0 is remapped! (1/4 of keys, not all of them)

REMOVE Server 1:
  Only keys on Server 1 are remapped to the next server clockwise.
  Rest are unaffected.
```

### Virtual Nodes (The Fix for Uneven Distribution)

```
PROBLEM: With few servers, the ring is unevenly partitioned.
  Server 1 might get 80% of the keys by bad luck.

SOLUTION: Virtual nodes (replicas)
  Instead of 1 position per server, place MULTIPLE virtual nodes.

  Server 0 → s0_0, s0_1, s0_2, ..., s0_200 (200 virtual positions)
  Server 1 → s1_0, s1_1, s1_2, ..., s1_200

  With 200 virtual nodes per server:
  Standard deviation ≈ 5% of mean → very balanced!

  Tradeoff: More virtual nodes = better balance but more memory
            to store the positions.
```

### Real-World Usage

```
USED BY:
  • Amazon DynamoDB (data partitioning)
  • Apache Cassandra (data partitioning across cluster)
  • Discord (chat application user routing)
  • Akamai CDN (content routing)
  • Google Maglev (network load balancer)
```

### Interview Q&As

**Q: "Why is consistent hashing better than hash % N?"**

"When a server is added or removed with hash%N, nearly ALL keys are remapped because N changes. With consistent hashing, only k/n keys are remapped (the keys in the affected partition). This prevents cache stampedes and minimizes data movement during scaling events."

**Q: "What are virtual nodes and why are they needed?"**

"With few physical servers on the ring, the partitions can be very uneven — one server might get 80% of the traffic. Virtual nodes solve this by placing each server at multiple positions on the ring. With 200 virtual nodes per server, the standard deviation drops to about 5%, giving near-uniform distribution."

---

## Chapter 6: Design a Key-Value Store

### Requirements

```
FUNCTIONAL:
  • put(key, value) — store a key-value pair
  • get(key) — retrieve value by key

NON-FUNCTIONAL:
  • Key size: small (up to 1KB)
  • Value size: large (up to 1MB)
  • Big data volume
  • High availability (system responds even during failures)
  • Scalability (add/remove nodes easily)
  • Tunable consistency (strong or eventual)
  • Configurable CAP tradeoff
```

### CAP Theorem

```
CAP: You can only guarantee 2 of 3 properties simultaneously:

  C (Consistency): All reads see the latest written data
  A (Availability): Every request gets a response (not an error)
  P (Partition tolerance): System works despite network partitions

In distributed systems, P is non-negotiable (network WILL fail).
So the real choice is between:
  CP (Consistency + Partition tolerance): When partitioned, return ERROR
  AP (Availability + Partition tolerance): When partitioned, return STALE data

Most key-value stores choose AP (DynamoDB, Cassandra) because
availability is more important for most use cases.
```

### Architecture Components

```
┌──────────────────────────────────────────────────────────────┐
│                   KEY-VALUE STORE ARCHITECTURE                │
│                                                              │
│  ┌──────────────┐                                           │
│  │ Client       │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│  │ Coordinator  │────>│  Consistent  │────>│  Replication ││
│  │ (receives    │     │  Hashing     │     │  (N copies   ││
│  │  request)    │     │  (find node) │     │   per key)   ││
│  └──────────────┘     └──────────────┘     └──────────────┘│
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│  │ Versioning   │     │  Membership  │     │  Failure     ││
│  │ (detect      │     │  (which      │     │  Detection   ││
│  │  conflicts)  │     │   nodes alive)│     │  (gossip)    ││
│  └──────────────┘     └──────────────┘     └──────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### Consistency Models

```
QUORUM (n, w, r):
  n = number of replicas per key
  w = write quorum (min writes to acknowledge)
  r = read quorum (min reads to acknowledge)

  Strong consistency: w + r > n (reads always see latest write)
  Eventual consistency: w + r ≤ n (reads may see stale data)

  Example: n=3, w=2, r=2
    Write: acknowledged when 2 of 3 replicas confirm
    Read: reads from 2 of 3 replicas, returns latest version
    → w + r = 4 > 3 = n → strong consistency

  Example: n=3, w=1, r=1
    → w + r = 2 ≤ 3 = n → eventual consistency (faster but may be stale)
```

### Conflict Resolution with Vector Clocks

```
PROBLEM: Two clients write to the same key simultaneously.
  Both writes go to different replicas. Which one wins?

VECTOR CLOCK: [server, version] pairs

  Client A writes key1 → {value: "A", clock: {S1: 1}}
  Client B writes key1 → {value: "B", clock: {S2: 1}}

  System detects conflict: neither clock is descendant of the other.

  RESOLUTION OPTIONS:
    1. Last-write-wins (LWW) — use timestamp (may lose data)
    2. Semantic resolution — application decides
    3. Expose both versions to client — client resolves
```

### Write Path (SSTable + Memtable)

```
1. Write → commit log (WAL — write-ahead log for durability)
2. Write → memtable (in-memory sorted table)
3. When memtable is full → flush to SSTable (on disk)
4. SSTables are periodically compacted (merged)

READ PATH:
1. Check memtable (in memory — fast)
2. Check SSTables (on disk — slower)
3. Use Bloom filter to quickly skip SSTables that DON'T have the key

This is the LSM-tree architecture used by Cassandra, HBase, LevelDB.
```

### Interview Q&As

**Q: "How do you handle conflicts in a distributed key-value store?"**

"I use vector clocks to detect concurrent writes. Each write carries a vector clock — a list of (node, version) pairs. When the system receives two writes with clocks where neither is a descendant of the other, it knows they're concurrent. The system then resolves using last-write-wins for simple cases, or exposes both versions to the application layer for semantic resolution. Amazon Dynamo uses this approach."

**Q: "What is the CAP theorem and which do you choose?"**

"CAP says you can guarantee Consistency, Availability, or Partition tolerance — but only two at once. Since network partitions are unavoidable in distributed systems, P is always present. So the real choice is CP vs AP. For a key-value store used as a cache, I'd choose AP — prefer returning stale data over returning an error. For a financial transaction store, I'd choose CP — prefer erroring over inconsistency."

---

## Chapter 7: Design a Unique ID Generator

### Requirements

```
• IDs must be globally unique
• IDs are roughly sortable by time (approximate time ordering)
• IDs are 64-bit integers
• System generates 10,000+ IDs per second
```

### Option 1: Auto-Increment (❌)

```
MySQL: id BIGINT AUTO_INCREMENT

PROBLEM: Single point of failure. If DB goes down, no IDs.
         Doesn't scale across multiple data centers.
         Hard to synchronize across shards.
```

### Option 2: UUID (⚠️)

```
UUID: 128-bit: f47ac10b-58cc-4372-a567-0e02b2c3d479

Pros: No coordination needed, globally unique
Cons: 128 bits (not 64), NOT sortable by time, indexing is slower
```

### Option 3: Snowflake (✅ — THE ANSWER)

```
Twitter's Snowflake ID — 64-bit structured ID:

┌─────────┬──────────┬───────────┬────────────┐
│  1 bit  │ 41 bits  │ 10 bits   │ 12 bits    │
│ (sign)  │ (timestamp)│(machine) │(sequence)  │
│  0      │          │           │            │
└─────────┴──────────┴───────────┴────────────┘

SIGN BIT (1 bit): Always 0 (positive number)

TIMESTAMP (41 bits): Milliseconds since custom epoch (Nov 4, 2010)
  → 41 bits = 2^41 ms = ~69 years of timestamps
  → This makes IDs roughly sortable by time

MACHINE ID (10 bits): 2^10 = 1,024 machines
  → Each server gets a unique machine ID
  → Distributed via ZooKeeper or config

SEQUENCE (12 bits): 2^12 = 4,096 IDs per millisecond per machine
  → Resets every millisecond
  → Total: 1,024 machines × 4,096 = ~4 billion IDs/ms

Example Snowflake ID breakdown:
  ID: 1234567890123456789
  → timestamp bits → 2024-07-24 09:30:45.123 UTC
  → machine ID → server #42
  → sequence → #7 (7th ID generated that millisecond)
```

### Snowflake Advantages

```
✓ 64-bit (fits in BIGINT, efficient indexing)
✓ Roughly time-ordered (sortable)
✓ Decentralized (no single point of failure)
✓ High throughput (4,096 IDs/ms per machine)
✓ 69 years of unique timestamps
```

### Interview Q&As

**Q: "What if the clock goes backward (NTP sync)?"**

"Clock skew is a real concern. If a server's clock moves backward (e.g., NTP synchronization), it might generate duplicate IDs. I handle this by: (1) recording the last timestamp — if current time < last timestamp, refuse to generate (or wait until clock catches up). (2) Using a margin of error — if the clock moves backward by less than a few milliseconds, use the last timestamp with an incremented sequence number. Twitter's Snowflake handles this in production."

---

## Chapter 8: Design a URL Shortener

### Requirements

```
FUNCTIONAL:
  • long_to_short(long_url) → returns short URL (e.g., bit.ly/abc123)
  • short_to_long(short_url) → redirects to original URL

NON-FUNCTIONAL:
  • Short URLs: 7 characters (readable, easy to type)
  • High read:write ratio (100:1 — mostly redirects)
  • Predictable latency (<100ms for redirect)
  • High availability (redirects must always work)
```

### Estimation

```
ASSUMPTIONS:
  • 100M new URLs per month (writes)
  • 10B redirects per month (reads, 100:1 ratio)
  • 10-year retention

STORAGE:
  • Each URL record: short_url (7 chars) + long_url (2KB avg) + metadata (500B)
    ≈ 2.5 KB per record
  • 10-year records: 100M × 12 × 10 = 12 billion records
  • Storage: 12B × 2.5 KB = 30 TB

QPS:
  • Write QPS: 100M / 30 / 24 / 3600 = ~40 writes/sec
  • Read QPS: 10B / 30 / 24 / 3600 = ~4,000 reads/sec
  • Peak read QPS: ~8,000

BANDWIDTH:
  • Read: 4,000 × 2.5KB = 10 MB/sec = ~800 GB/day
```

### The Short URL Encoding (Base62)

```
Base62: uses 62 characters [a-z, A-Z, 0-9]

7 characters = 62^7 = 3.5 trillion combinations
→ More than enough for 12 billion URLs

ENCODING:
  1. Generate a unique ID (Snowflake): 1234567890
  2. Convert to Base62: 1234567890 → "dnhssr"

DECODING:
  1. "dnhssr" → convert from Base62 → 1234567890
  2. Look up in database → get long URL
```

### Architecture

```
┌────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ User   │───>│ Load     │───>│ Web      │───>│ Database │
│        │    │ Balancer │    │ Server   │    │ (NoSQL)  │
│ POST   │    │          │    │          │    │          │
│ /api/  │    └──────────┘    └──────────┘    └──────────┘
│ shorten│                         │
└────────┘                         │
                                   ▼
┌────────┐    ┌──────────┐    ┌──────────┐
│ User   │───>│ Load     │───>│ Web      │
│        │    │ Balancer │    │ Server   │
│ GET    │    │          │    │          │
│ /abc123│    └──────────┘    └──────────┘
│ (redirect)                      │
└────────┘                        ▼
                           ┌──────────────────┐
                           │ Cache (Redis)    │
                           │ short→long lookup│
                           └──────────────────┘
                                    │
                             MISS → ┌──────────┐
                                    │ Database │
                                    └──────────┘
```

### Database Schema

```sql
CREATE TABLE url_mapping (
    id              BIGINT PRIMARY KEY,      -- Snowflake ID
    short_code      VARCHAR(7) UNIQUE,       -- Base62 encoded
    long_url        TEXT NOT NULL,
    user_id         BIGINT,
    created_at      TIMESTAMP DEFAULT NOW(),
    expires_at      TIMESTAMP,
    INDEX idx_short_code (short_code)
);
```

### API Design

```
POST /api/v1/data/shorten
  Body: { "long_url": "https://example.com/very/long/path" }
  Response: { "short_url": "https://tiny.url/dnhssr" }

GET /{short_code}
  Response: HTTP 301 (Permanent Redirect)
            Location: https://example.com/very/long/path

WHY 301 (Permanent) vs 302 (Temporary)?
  301: Browser caches the redirect → faster on subsequent visits
       BUT: analytics lose click data (browser doesn't hit server)
  302: Browser always hits server → accurate analytics
       BUT: slightly slower (always goes through redirect)

CHOICE: Use 302 for analytics-heavy use case (like bit.ly).
        Use 301 for performance-focused use case.
```

### Interview Q&As

**Q: "How do you handle hash collisions?"**

"Two approaches. First, with Snowflake IDs converted to Base62, collisions are impossible — each unique ID produces a unique Base62 string. Second, if using a hash function (MD5/SHA), I check the database before inserting. If the hash already exists, append a random suffix or increment the original ID and re-encode."

**Q: "What if two users shorten the same URL?"**

"Two options: (1) Dedup — store one record per unique long URL. If the same URL is shortened again, return the existing short code. This saves storage. (2) Allow duplicates — each user gets their own short code. This allows per-user analytics. The choice depends on whether analytics is important. Bit.ly allows duplicates because analytics is their core product."

---

> **Next:** Chapter 9-12 covers Web Crawler, Notification System, News Feed, and Chat System.
> See `05-alex-xu-vol1-scaling-systems.md`.
