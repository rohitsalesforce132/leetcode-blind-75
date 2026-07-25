# Sinha System Design Guide — Chapters 9–16 Deep Dive

> Comprehensive study notes derived from **Sinha's System Design Guide** (Chapters 9–16).
> Covers: URL Shortener, Proximity Service, Twitter, Instagram, Google Docs (OT/collaboration),
> Netflix (transcoding/CDN/DRM), Interview Tips, and the System Design Cheat Sheet.
> Each chapter includes ASCII architecture diagrams, data models, APIs, estimations, and **5 Q&As**.

---

## Table of Contents

- [Chapter 9: URL Shortener](#chapter-9-url-shortener)
- [Chapter 10: Proximity Service](#chapter-10-proximity-service)
- [Chapter 11: Twitter](#chapter-11-twitter)
- [Chapter 12: Instagram](#chapter-12-instagram)
- [Chapter 13: Google Docs (Collaborative Editing / OT)](#chapter-13-google-docs)
- [Chapter 14: Netflix (Video Streaming)](#chapter-14-netflix)
- [Chapter 15: Interview Tips](#chapter-15-interview-tips)
- [Chapter 16: System Design Cheat Sheet](#chapter-16-system-design-cheat-sheet)

---

## Chapter 9: URL Shortener

### 9.1 Overview

A URL shortener converts long web addresses into short, manageable links. Though seemingly
simple, the design involves unique-ID generation at massive scale, collision avoidance,
high availability for reads, and low latency on both read and write paths.

**Real-world use cases:**
- Social media sharing (Twitter character limits)
- Affiliate / email marketing (click-through tracking)
- QR codes (shorter URLs → simpler QR patterns)
- Print media (memorable, typeable links)
- Mobile deep linking (app store redirects)
- Branded short links (bit.ly, t.co, rebrand.ly)

### 9.2 Functional Requirements

**Core:**
| # | Requirement |
|---|-------------|
| FR1 | Given a long URL, return a short URL |
| FR2 | Given a short URL, return the original long URL |
| FR3 | Short URLs must be unique, with a length cap |

**Extended / Good-to-have:**
- Validate incoming long URL
- Support custom aliases (e.g., `bit.ly/MyBrand`)
- URL expiry (6 months from last usage)
- Creator can update the destination long URL
- Delete a mapping
- Analytics & click tracking
- User account management

### 9.3 Non-Functional Requirements

| NFR | Detail |
|-----|--------|
| **Availability** | Highly available — link resolution must never fail |
| **Scalability** | 100M+ users, tolerate traffic spikes |
| **Latency** | Sub-50ms reads and writes |
| **Consistency** | Same short URL → same long URL for all users; same long URL → same short URL |
| **Durability** | Once created, the mapping is never lost |
| **Reliability** | Correct behavior under failures & spikes |

### 9.4 APIs

```
┌─────────────────────────────────────────────────────┐
│  POST /shorturl                                      │
│  Request:  { "longUrl": "https://example.com/..." }  │
│  Response: { "shortUrl": "https://s.co/aB3xY9k" }   │
├─────────────────────────────────────────────────────┤
│  GET /shorturls/{shortUrl}                           │
│  Response: { "longUrl": "https://example.com/..." }  │
│  (HTTP 301 redirect in practice)                     │
└─────────────────────────────────────────────────────┘
```

### 9.5 Scale Estimations

**Character set:** `[a-z, A-Z, 0-9]` = **62 characters**

**Assumptions:**
```
Users:               1 billion
Active creators:     10% = 100M
URLs per user/day:   1
Retention:           10 years

Total URLs stored:   100M × 365 × 10 = 365 billion
```

**Short URL length:**
```
62^6  = 56.8 billion  → too few for 365B
62^7  = 3.5 trillion  → sufficient ✅
→ Use 7 characters
```

**Storage:**
```
Per-record bytes:
  short_url   = 20
  long_url    = 1000
  created_at  = 10
  updated_at  = 10
  created_by  = 20
  ────────────────
  Total       ≈ 1060 → round to 1500 bytes

365B × 1500 B ≈ 500 TB (raw)
With replication factor 3 → 1.5 PB
```

**Throughput:**
```
Write RPS:  100M / 100,000 ≈ 1,000 RPS
Read RPS:   100× write     ≈ 100,000 RPS  (100:1 read/write ratio)
```

### 9.6 Core Challenge — Unique ID Generation

This is the heart of the problem. Sinha evaluates four approaches:

#### Option A: Random Generation + DB Check

```
generate_random_7chars() → check DB → if exists, retry → else store
```

**Problems:**
- Unpredictable retries → write latency spikes
- Concurrency collisions: two threads generate the same short URL for
  different long URLs → one overwrites the other (data corruption)
- Mitigation: `putIfAbsent` (not universally supported) or post-write
  verification via a read-back check (doubles every write)

**Verdict:** ❌ Not production-grade.

#### Option B: MD5 Hash (deterministic)

```
long_url → MD5 → 128-bit hash → take first 42 bits → base62 encode → 7 chars
```

**Pros:** Same long URL → same short URL (dedup, saves space).

**Problems:**
- 42 bits of 128 → much higher collision probability
- Using all 128 bits → 22+ characters (defeats the purpose)
- Birthday paradox: collisions become likely at scale

**Verdict:** ❌ Collision-prone.

#### Option C: Single Monotonic Counter

```
1 master host generates sequential IDs: 1, 2, 3, ...
```

**Problem:** Single point of failure (SPOF).

**Mitigation attempt:** `host_id(6b) + timestamp(32b) + counter(4b)`
- Only 64 hosts
- Only 16 IDs/ms → collisions if >16 requests/ms

**Verdict:** ❌ Limited scale, SPOF.

#### Option D: Distributed Range-Based Counters ✅

```
                     ┌──────────────┐
                     │ Range Server │  (ZooKeeper: HA, replicated)
                     │  3.5T total  │
                     │  split into  │
                     │  3.5M ranges │
                     │  of 1M each  │
                     └──────┬───────┘
                            │ assigns ranges
           ┌────────────────┼────────────────┐
           ▼                ▼                 ▼
    ┌─────────────┐  ┌─────────────┐   ┌─────────────┐
    │ Counter S1  │  │ Counter S2  │…  │ Counter S10 │
    │ [0 – 1M)    │  │ [1M – 2M)   │   │ [9M – 10M)  │
    │ increments  │  │ increments  │   │ increments  │
    │ locally     │  │ locally     │   │ locally     │
    └──────┬──────┘  └──────┬──────┘   └──────┬──────┘
           │                │                 │
           ▼                ▼                 ▼
      base62 encode → 7-char short URL → store in Redis
```

**How it works:**
1. Range Server (backed by ZooKeeper) divides the 3.5T key space into
   ranges of ~1M.
2. Each Counter Server requests and owns a range (e.g., `[0, 1M)`).
3. It increments locally — no coordination needed within the range.
4. When exhausted, it requests the next range.

**Failure handling:**
- Counter Server crashes → its unassigned range is discarded (lose ≤1M
  IDs — negligible out of 3.5T).
- Mitigation: periodically checkpoint the current counter to the Range
  Server (every Nth generation) → lose at most N IDs per crash.

**Base62 conversion example:**
```
Counter: 9,234,529,445

9234529445 ÷ 62 = 148907051  r 23  → 'x'
148907051  ÷ 62 = 2401748    r 39  → 'N'
2401748    ÷ 62 = 38702      r 4   → 'e'
38702      ÷ 62 = 624        r 14  → 'o'
624        ÷ 62 = 10         r 4   → 'e'
10         ÷ 62 = 0          r 10  → 'k'

Result: "keoeNx"  →  urlshortener.com/keoeNx
```

**Verdict:** ✅ Robust, horizontally scalable, no SPOF.

### 9.7 High-Level Architecture

```
                         ┌─────────────┐
                         │   Client    │
                         │  (Browser)  │
                         └──────┬──────┘
                                │
                    ┌───────────▼───────────┐
                    │      Load Balancer     │
                    └───┬───────────────┬───┘
              WRITE     │               │     READ
            ┌───────────▼──┐         ┌──▼────────────┐
            │  Counter     │         │  Read Server   │
            │  Servers     │         │  (stateless,   │
            │  (each has   │         │   horizontally │
            │   a range)   │         │   scaled)      │
            └──────┬───────┘         └──┬──────────┬──┘
                   │                    │          │
          ┌────────▼────────┐   ┌───────▼──┐  ┌────▼─────┐
          │  Range Server   │   │  Cache   │  │  Redis   │
          │  (ZooKeeper)    │   │  (LRU)   │  │ Cluster  │
          │  assigns ranges │   │          │  │          │
          └─────────────────┘   └──────────┘  └──────────┘
```

**Write Flow:**
1. Client calls `POST /shorturl` with the long URL.
2. LB routes to a Counter Server.
3. Counter Server increments its local counter.
4. Converts counter → 7-char base62 string.
5. Stores `{short_url → long_url}` in Redis.

**Read Flow:**
1. Client calls `GET /shorturls/{shortUrl}`.
2. LB routes to a Read Server.
3. Read Server checks cache → if hit, return long URL.
4. If miss, fetch from Redis → populate cache → return.

### 9.8 Database Choice

| Requirement | Choice |
|-------------|--------|
| Key-value mapping | **Redis** (in-memory, fast, durable via AOF/RDB) |
| Analytics | Append to a WAL / time-series DB (Cassandra) |

Redis is chosen because the data model is a pure key→value lookup and
Redis provides microsecond-level latency with built-in replication.

### 9.5 Requirements Verification

| Requirement | How Satisfied |
|-------------|---------------|
| FR1 (long→short) | Counter Server generates unique 7-char ID |
| FR2 (short→long) | Redis lookup, cache-accelerated |
| FR3 (unique, capped) | 7 chars, unique by design |
| Availability | No SPOF; all components horizontally scaled + replicated |
| Scalability | Add more Counter/Read servers behind LB |
| Latency | Writes: no DB lookup (pre-generate counters in memory); Reads: LRU cache |
| Consistency | One entry per short_url by design → strong consistency |
| Durability | Redis AOF + replication factor 3 |

### 9.10 Q&A — URL Shortener

**Q1: Why 7 characters and not 6?**
A: 62^6 ≈ 57B, but our 10-year requirement is 365B URLs. 62^7 ≈ 3.5T,
which provides ample headroom. Using fewer bits risks exhausting the
keyspace; using more wastes characters.

**Q2: What if the Range Server crashes?**
A: The Range Server is backed by ZooKeeper — a highly available,
replicated coordination service. ZooKeeper uses a quorum-based consensus
protocol (Zab) so if one node fails, others continue. Range assignments
are persisted, so recovery is automatic.

**Q3: Why not just use a database auto-increment column?**
A: A single auto-increment column is a SPOF and a write bottleneck. All
writes serialize through one sequence generator. The distributed range
approach allows each Counter Server to generate IDs independently within
its range, achieving linear write scalability.

**Q4: How do you handle custom aliases (e.g., `s.co/mybrand`)?**
A: Store custom aliases in a separate table with the short_url as the
custom string. On creation, check if the custom alias is already taken.
Reserve a namespace so auto-generated IDs never collide with custom
aliases (e.g., custom aliases can't be purely alphanumeric-7 in the
counter sequence, or use a flag column).

**Q5: Why Redis and not Cassandra or DynamoDB?**
A: The data access pattern is a pure point lookup (key → value), not
range queries or complex filtering. Redis provides the lowest latency for
this pattern (<1ms). Cassandra/DynamoDB would add 5–10ms. If cost is a
concern, you can tier: hot URLs in Redis, cold in Cassandra.

---

## Chapter 10: Proximity Service

### 10.1 Overview

Proximity services find nearby entities (restaurants, drivers, stores)
given a geographic location and radius. Used by Uber, Yelp, DoorDash,
Tinder, Google Maps, and Strava.

**Real-world use cases:**
- **Ride-sharing:** Match riders with nearby drivers, dynamic pricing
- **Local search:** Restaurant/shop recommendations by location
- **Food delivery:** Optimized routes, real-time order tracking
- **Dating apps:** Geolocation matching
- **Navigation:** Turn-by-turn directions, traffic alerts
- **Fitness:** Route tracking, activity analysis

### 10.2 Functional Requirements

**Core:**
| # | Requirement |
|---|-------------|
| FR1 | User can search nearby restaurants given their location (lat, long) |
| FR2 | User can select a restaurant and place an order |

### 10.3 Non-Functional Requirements

| NFR | Detail |
|-----|--------|
| Availability | Highly available (multiple instances per service) |
| Scalability | 100M users, tolerate spikes |
| Latency | Read latency < 200ms |
| Consistency | Eventual consistency acceptable (restaurants don't change often) |
| Reliability | Durable, fault-tolerant |

### 10.4 APIs

```http
GET /restaurants/search?lat=37.7749&long=122.4194&distance=5

Response:
[
  {
    "restaurantId": "78566",
    "name": "ABC_Italian",
    "location": "123 Castro St, San Francisco, CA 94056",
    "cuisine": "Italian",
    "rating": 4.9,
    "distance": "2 miles"
  },
  ...
]

POST /orders/place
Request:
{
  "userId": "12345",
  "restaurantId": "78566",
  "items": [
    { "itemId": "item1", "quantity": 4 },
    { "itemId": "item2", "quantity": 3 }
  ],
  "paymentMethod": "credit_card"
}
Response:
{
  "orderId": "6689092",
  "message": "Thanks for ordering!",
  "billAmount": "$75.92"
}
```

### 10.5 Scale Estimations

```
Users:               100M
DAU:                 10M (10%)
Ordering peak hours: 6 hours (lunch + dinner)

Order QPS:     10M / (6 × 60 × 60) ≈ 1,200 QPS
With spikes:   5× = 6,000 QPS
Search QPS:    5× ordering = 6,000 QPS
Restaurants:   1M on our platform (of ~10M worldwide)
```

### 10.6 Core Challenge — Finding Nearby Restaurants

#### Option A: Relational DB with Two-Dimensional Query ❌

```sql
SELECT restaurant_ids FROM restaurant_table
WHERE lat > user_lat - 5 AND lat < user_lat + 5
  AND long > user_long - 5 AND long < user_long + 5;
```

**Problem:** Full table scan. Indexes work in one dimension — even with
two indexes, the DB can only use one at a time, leaving a massive range
to scan.

#### Option B: Quadtree ✅

```
                    Root (entire world)
            ┌──────────┬──────────┐
            │     0    │     1    │
            ├──────────┼──────────┤
            │     2    │     3    │
            └──────────┴──────────┘
         Each quadrant recursively divided
         until it has < N restaurants (e.g., N=500)
```

**Quadtree properties:**
- **Leaf nodes:** contain a list of restaurant IDs
- **Non-leaf nodes:** contain min/max lat/long bounds
- Subdivision is **conditional**: only split if a quadrant has > N items
- Kept **in memory** for O(log N) search

**Search algorithm:**
```
findNearby(root, lat, long, radius D):
    if root is leaf:
        restaurants = root.restaurant_list
        return filter_by_distance(restaurants, lat, long, D)
    for each child in root.children:
        if (lat, long) within child.bounds:
            return findNearby(child, lat, long, D)
    # If results insufficient, go up one level and check siblings
```

**Pros:** Fast (in-memory), efficient (conditional subdivision).
**Cons:** Frequent updates → tree rebuild cost. Acceptable here since
restaurants open/close infrequently.

#### Option C: Geohashing ✅ (alternative)

```
World → divided into quadrants, labeled:
  top-left: 00   top-right: 01
  bottom-left: 10  bottom-right: 11

Recursively subdivided:
  0000, 0001, 0010, 0011, ...

At 16 levels: rectangles of 0.38mi × 0.19mi
Encoded in base32: [0-9, b-z] excluding a, i, l, o
```

**Example:** San Francisco (37.7749°N, 122.4194°W) → geohash `9q8yyk8yt`

**Storage:**
```
geohash      | restaurant_ids
─────────────┼─────────────────────────
9q8yyk       | {3, 7, 97, 89, 234, ...}
9q8yym       | {1, 4, 73, 91, 212, ...}
9q8yyn       | {9, 13, 92, 893, 422, ...}
```

**Query:**
```sql
SELECT restaurant_ids WHERE geohash LIKE '9q8yy%';
```

**Quadtree vs. Geohashing:**
| Aspect | Quadtree | Geohashing |
|--------|----------|------------|
| Subdivision | Conditional (only if > N items) | Fixed grid |
| Sparse areas | No wasted subdivisions | Unnecessary subdivisions |
| Speed | In-memory → very fast | DB-backed, prefix index |
| Updates | Tree rebuild needed | Simple row update |
| **Sinha's choice** | **✅ Preferred** | Acceptable |

### 10.7 High-Level Architecture

```
  ┌─────────┐
  │  User    │
  │ Device   │
  └────┬─────┘
       │
  ┌────▼──────────────┐
  │   Load Balancer    │
  └─┬──────┬──────┬───┘
    │      │      │
    ▼      ▼      ▼
┌───────┐ ┌──────────────┐ ┌──────────────┐
│ User  │ │ Restaurant   │ │ Order Mgmt   │
│ CRUD  │ │ Search Svc   │ │ Service      │
│ Svc   │ │              │ │              │
└───┬───┘ └──────┬───────┘ └──────┬───────┘
    │            │                │
    ▼            ▼                ▼
┌────────┐ ┌──────────┐   ┌─────────────┐
│Customer│ │ Quadtree │   │ Restaurant  │
│  DB    │ │ (in-mem) │   │     DB      │
└────────┘ └──────────┘   └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │  Payment    │
                          │  Service    │
                          └─────────────┘
```

**Read Flow (search):**
1. Client calls `GET /restaurants/search?lat=...&long=...`
2. LB routes to Restaurant Search Service.
3. Service traverses quadtree from root → leaf based on user coords.
4. Returns list of nearest restaurants within radius.

**Write Flow (order):**
1. Client calls `POST /orders/place`.
2. Order Mgmt Service fetches customer data + restaurant menu.
3. Processes payment via Payment Service.
4. Writes order to Order DB.

### 10.8 Q&A — Proximity Service

**Q1: Why prefer quadtree over geohashing for restaurant search?**
A: Quadtree only subdivides when a quadrant has more than N (e.g., 500)
restaurants, avoiding wasted subdivisions in sparse areas. Geohashing
divides uniformly regardless of restaurant density, creating many empty
or near-empty cells. Quadtree is also in-memory, giving faster lookups.
Since restaurants rarely change location, the tree-rebuild cost on update
is negligible.

**Q2: How do you handle edge cases where a user is near the boundary of a
quadtree leaf?**
A: After getting results from the leaf, if the result count is
insufficient (e.g., fewer than requested), traverse up to the parent node
and search its sibling quadrants. Apply a final Cartesian/distance filter
to eliminate results outside the actual radius.

**Q3: What if the quadtree server crashes?**
A: The quadtree is rebuilt from the restaurant database on startup
(synchronization). Multiple quadtree server replicas run behind the LB,
so failure of one doesn't affect availability. Updates (restaurant
open/close) are propagated to all replicas.

**Q4: How would you handle real-time driver location updates (Uber
scenario)?**
A: For high-frequency location updates (drivers moving), quadtree's
rebuild cost becomes problematic. In that case, geohashing or a
specialized solution like Google S2 cells would be better — they support
incremental updates without tree restructuring. You'd also use a
geo-indexed NoSQL store (e.g., Redis GEO, MongoDB 2dsphere).

**Q5: Why is eventual consistency acceptable here?**
A: Restaurant data (menu, hours, location) changes infrequently. If a
new restaurant appears in search results a few seconds after it registers,
no harm is done. Strong consistency would add latency (synchronous
replication) for no practical benefit.

---

## Chapter 11: Twitter

### 11.1 Overview

Twitter (now X) is a microblogging platform with short messages (tweets,
≤280 chars), follow graphs, timelines, search, and real-time delivery.
The core design challenges are timeline generation at massive fanout and
search indexing at scale.

### 11.2 Functional Requirements

| Area | Requirements |
|------|-------------|
| Auth | Register, login, session management |
| Tweeting | Post ≤280-char tweets with text, hashtags, mentions, media |
| Follow | Follow/unfollow; maintain follow graph |
| Timeline | Chronological feed of tweets from followed users; real-time updates |
| Search | Search tweets/users by keywords, hashtags, usernames |
| Engagement | Retweet, like |
| DMs | Private messaging between users |

### 11.3 Non-Functional Requirements

| NFR | Detail |
|-----|--------|
| Scalability | Horizontal; independent scaling of Tweet/Timeline/Search services |
| Availability | Minimal downtime, geo-redundancy, server + DB replication |
| Reliability | Data integrity, backups, eventual or strong consistency per subsystem |
| Latency | Real-time updates, fast timeline retrieval, caching + CDN |

### 11.4 Data Model

```
┌──────────────┐       ┌──────────────┐
│    User      │       │    Tweet     │
├──────────────┤       ├──────────────┤
│ user_id (PK) │◄──────│ tweet_id (PK)│
│ username     │       │ user_id (FK) │
│ email        │       │ content      │
│ password_hash│       │ media_url    │
│ profile_pic  │       │ timestamp    │
│ bio          │       │ retweet_cnt  │
│ location     │       │ like_cnt     │
│ created_at   │       └──────────────┘
└──────┬───────┘
       │
       ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Follow     │  │    Like      │  │   Retweet    │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ follower_id  │  │ user_id      │  │ tweet_id     │
│ followee_id  │  │ tweet_id     │  │ retweeted_by │
│ created_at   │  │ created_at   │  │ created_at   │
└──────────────┘  └──────────────┘  └──────────────┘
```

- **Follow:** composite PK (follower_id, followee_id)
- **Tweet:** partition key = `user_id`, clustering key = `timestamp`
  (for chronological retrieval of a user's tweets)

### 11.5 Scale Calculations

```
Assumptions:
  Users:              100M
  DAU:                20M
  Tweets/user/day:    5
  Avg tweet size:     200 bytes
  Avg media size:     1 MB
  % tweets w/ media:  20%
  Retention:          5 years
  Avg followers/user: 100

STORAGE:
  Tweet storage:  20M × 5 × 200B × 365 × 5 = 36.5 TB
  Media storage:  20M × 5 × 20% × 1MB × 365 × 5 = 365 PB
  User storage:   100M × 1MB = 100 TB
  ─────────────────────────────────────
  Total:          ≈ 365 PB (dominated by media)

BANDWIDTH:
  Tweet delivery: 20M × 5 × 100 followers × 200B = 2 TB/day
  Media delivery: 20M × 5 × 20% × 100 × 1MB   = 2 PB/day
  Total:          ≈ 2 PB/day

THROUGHPUT:
  Peak tweets/sec:    20M × 5 / 86400 ≈ 1,200
  Peak media/sec:     1,200 × 20%     ≈ 240
  Fanout ops/sec:     1,200 × 100     ≈ 120,000

CACHE:
  Daily tweet views:  20M × 100 = 2B views
  Cache size (80% hit): 2B × 80% × 200B ≈ 320 GB
```

### 11.6 High-Level Architecture

```
┌──────────┐
│  Clients  │  (Web, iOS, Android)
└─────┬─────┘
      │
┌─────▼──────────┐
│  Load Balancer  │
└─────┬──────────┘
      │
┌─────▼──────────┐
│  API Gateway    │  (auth, rate limiting, routing)
└──┬────┬────┬───┘
   │    │    │
   ▼    ▼    ▼
┌──────┐┌──────┐┌──────────┐┌──────────┐
│Tweet ││User  ││Timeline  ││Search    │
│Svc   ││Svc   ││Svc       ││Svc       │
└──┬───┘└──┬───┘└────┬─────┘└────┬─────┘
   │       │         │           │
   ▼       ▼         │           ▼
┌──────┐ ┌──────┐    │    ┌─────────────┐
│Tweet │ │User/ │    │    │Elasticsearch│
│DB    │ │Follow│    │    │ (inverted   │
│(Cass)│ │ DB   │    │    │  index)     │
└──┬───┘ └──────┘    │    └─────────────┘
   │                 │
   │     ┌───────────▼───────────┐
   │     │    Redis Cache        │
   │     │  (timeline per user:  │
   │     │   sorted set of       │
   │     │   tweet_ids)          │
   │     └───────────────────────┘
   │
┌──▼──────────┐    ┌───────────────┐
│ Object Store │    │ Apache Kafka  │
│ (S3: media)  │    │ (message      │
└──────────────┘    │  queue)       │
                    └───────┬───────┘
                            │
              publishes tweet_id + user_id
                            │
                    ┌───────▼───────┐
                    │ Timeline Svc   │
                    │ + Search Svc   │
                    │ (consumers)    │
                    └───────────────┘
```

### 11.7 Microservices Deep Dive

#### Tweet Service

```
POST   /tweets                    — create tweet
GET    /tweets/{tweetId}          — retrieve tweet
DELETE /tweets/{tweetId}          — delete tweet
GET    /users/{userId}/tweets     — user's tweets (paginated)
```

**Creation flow:**
1. Client sends `POST /tweets` with content + optional media.
2. Tweet Service validates (length, auth).
3. Uploads media to S3, gets media_url.
4. Generates `tweet_id`, stores in Cassandra (partition=`user_id`).
5. Publishes `{tweet_id, user_id}` to Kafka.
6. Returns tweet object.

**Caching strategies:**
- Time-based sliding window (cache last 24h of tweets)
- Popularity-based (cache tweets above engagement threshold)
- Hybrid (last 2h always + older popular)
- Predictive (ML model predicts viral tweets)
- User-based (cache recent tweets from high-follower accounts)

Eviction: LRU, TTL, LFU, size-based, priority-based.

#### User Service

```
POST   /users                     — register
GET    /users/{userId}            — profile
PUT    /users/{userId}            — update profile
POST   /users/{userId}/follow     — follow
DELETE /users/{userId}/follow     — unfollow
GET    /users/{userId}/followers  — list followers
GET    /users/{userId}/following  — list following
```

- **User table:** PostgreSQL, PK = `user_id`
- **Follow table:** composite PK (`follower_id`, `followee_id`)
- **Auth:** JWT token with user_id + expiration

#### Timeline Service (Fanout-on-Write)

```
GET /timeline/{userId}            — home timeline
GET /timeline/{userId}/mentions   — mentions timeline
```

**Fanout-on-write flow:**
```
New tweet created
       │
       ▼
   Kafka topic
       │
       ▼
Timeline Service consumes
       │
       ├─ Get follower list from User Service
       │
       └─ For each follower:
            append tweet_id to their timeline
            (Redis sorted set, scored by timestamp)
```

**Timeline retrieval:**
1. Client requests `GET /timeline/{userId}`.
2. Timeline Service fetches user's timeline from Redis (sorted set of
   tweet_ids).
3. Fetches full tweet objects from Tweet Service (or tweet cache).
4. Returns sorted list.

**Push-based real-time:** WebSocket connections push new tweets to active
clients instantly.

#### Search Service

```
GET /search/tweets?q={query}&limit={limit}&offset={offset}
GET /search/users?q={query}&limit={limit}&offset={offset}
```

- Uses **Elasticsearch** (inverted index: terms → tweet_ids).
- New tweets indexed via Kafka consumer.
- Relevance scoring: TF-IDF + field-level boosting (hashtags, mentions).

### 11.8 Timeline Generation — Push vs. Pull

| Strategy | Description | Pros | Cons |
|----------|-------------|------|------|
| **Fanout-on-write (Push)** | On tweet creation, push to all followers' timeline caches | Fast reads (O(1) cache lookup) | Celebrity problem: 100M followers → 100M writes |
| **Fanout-on-read (Pull)** | On timeline request, fetch recent tweets from all followees | No write amplification | Slow reads (N queries for N followees) |
| **Hybrid** | Push for normal users; pull for celebrities (>100K followers) | Best of both worlds | Complexity |

### 11.9 Q&A — Twitter

**Q1: How do you handle the "celebrity problem" (a user with 100M
followers)?**
A: Use a hybrid approach. For users with very high follower counts
(celebrities), don't fanout on write — instead, fanout on read: when a
user loads their timeline, merge pre-computed timeline tweets with recent
tweets from celebrities they follow. This avoids 100M write operations
per celebrity tweet while keeping read latency low.

**Q2: Why use Cassandra for tweets instead of PostgreSQL?**
A: Tweets require extremely high write throughput (1,200+/sec) and
horizontal scalability. Cassandra is designed for write-heavy workloads
with linear scalability. The partition key (`user_id`) + clustering key
(`timestamp`) pattern naturally supports "get a user's tweets in
chronological order" without secondary indexes.

**Q3: How does the Search Service index tweets in real-time?**
A: Tweet Service publishes to Kafka on creation. Search Service consumes
messages from Kafka, extracts text/hashtags/mentions, and indexes them in
Elasticsearch. Kafka decouples the indexing from the write path — if
Elasticsearch is slow or down, messages buffer in Kafka without blocking
tweet creation.

**Q4: What happens if the Redis cache storing timelines fails?**
A: Redis should be configured with replication (primary + replicas) and
persistence (AOF). If the primary fails, a replica is promoted. If the
entire cache is lost, timelines can be reconstructed: Timeline Service
fetches recent tweets from all followed users (fanout-on-read fallback)
and repopulates the cache.

**Q5: How do you ensure tweets appear in the correct chronological order
in timelines?**
A: Each tweet has a timestamp. In Redis, timelines are stored as sorted
sets with the tweet timestamp as the score. This guarantees O(log N)
insertion and natural chronological ordering on retrieval. For globally
unique ordering, use a Snowflake-style ID (timestamp + machine ID +
sequence).

---

## Chapter 12: Instagram

### 12.1 Overview

Instagram is a photo-sharing platform with news feed, likes, comments,
hashtags, direct messaging, and search. The key challenges are media
storage/delivery at scale and news feed generation.

### 12.2 Functional Requirements

| Area | Requirements |
|------|-------------|
| Auth | Registration, login, session management |
| Photo upload | Upload from devices, JPEG/PNG support, filters, captions, tags |
| News feed | Personalized stream of photos from followed users; infinite scroll |
| Interactions | Like, comment, @mention |
| DMs | Private messaging (photos + text) |
| Search | Users, photos, hashtags |
| Notifications | Real-time push for followers, likes, comments, DMs |

### 12.3 Non-Functional Requirements

| NFR | Detail |
|-----|--------|
| Scalability | Horizontal; independent scaling of Photo Upload / News Feed services |
| Performance | Minimal latency for uploads, feed loading; async processing |
| Availability | Redundancy, fault tolerance, backups, disaster recovery |
| Reliability | Data integrity, graceful error handling |
| Usability | Search, filters, recommendations for engagement |

### 12.4 Data Model

```
┌──────────────┐       ┌──────────────┐
│    User      │       │    Photo     │
├──────────────┤       ├──────────────┤
│ user_id (PK) │◄──────│ photo_id (PK)│
│ username     │       │ user_id (FK) │
│ email        │       │ caption      │
│ password_hash│       │ image_url    │
│ profile_pic  │       │ location     │
│ bio          │       │ tags         │
│ website      │       │ created_at   │
└──────┬───────┘       └──────┬───────┘
       │                      │
       ▼                      ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Follow     │  │   Comment    │  │    Like      │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ follower_id  │  │ comment_id   │  │ user_id      │
│ followee_id  │  │ photo_id(FK) │  │ photo_id     │
│ created_at   │  │ user_id (FK) │  │ created_at   │
└──────────────┘  │ text         │  └──────────────┘
                  │ created_at   │
                  └──────────────┘

┌──────────────┐       ┌──────────────────┐
│   Hashtag    │       │  PhotoHashtag    │
├──────────────┤       ├──────────────────┤
│ hashtag_id   │◄──────│ photo_id         │
│ name         │       │ hashtag_id       │
└──────────────┘       └──────────────────┘
                       (many-to-many junction)
```

### 12.5 Scale Calculations

```
Assumptions:
  Users:              100M
  DAU:                10M
  Photos/user/day:    2
  Avg photo size:     5 MB
  Retention:          5 years
  Avg followers/user: 500
  Avg likes/photo:    100
  Avg comments/photo: 10

STORAGE:
  Photo storage:  10M × 2 × 5MB × 365 × 5 = 182.5 PB
  User data:      100M × 1MB = 100 GB
  Metadata:       10M × 2 × 1KB × 365 × 5 = 36.5 TB
  ─────────────────────────────────────
  Total:          ≈ 182.5 PB

BANDWIDTH:
  Uploads:   10M × 2 × 5MB = 100 TB/day
  Delivery:  10M × 500 × 2 × 5MB = 50 PB/day
  Total:     ≈ 50 PB/day

THROUGHPUT:
  Peak uploads/sec:   10M × 2 / 86400 ≈ 230
  Likes/sec:          230 × 100       ≈ 23,000
  Comments/sec:       230 × 10        ≈ 2,300
```

### 12.6 High-Level Architecture

```
┌──────────┐
│  Clients  │
└─────┬─────┘
      │
┌─────▼──────────┐
│  Load Balancer  │
└─────┬──────────┘
      │
┌─────▼──────────┐
│  API Gateway    │
└──┬───┬────┬────┘
   │   │    │
   ▼   ▼    ▼
┌──────┐┌──────────────┐┌──────────┐┌────────────┐┌──────────┐
│Photo ││ News Feed    ││User Svc  ││Interaction ││Direct Msg│
│Upload││ Service      ││          ││ Service    ││ Service  │
│Svc   ││              ││          ││            ││          │
└──┬───┘└──────┬───────┘└────┬─────┘└─────┬──────┘└────┬─────┘
   │           │             │            │             │
   ▼           ▼             ▼            ▼             ▼
┌──────┐ ┌─────────┐  ┌──────────┐ ┌──────────┐ ┌──────────┐
│  S3  │ │  Redis  │  │PostgreSQL│ │ NoSQL    │ │ NoSQL/   │
│(obj  │ │ (cache: │  │ (users,  │ │ (Cassandra│ │ Kafka    │
│ store│ │  feed)  │  │  follows)│ │ for high  │ │          │
│ for  │ │         │  │          │ │  writes)  │ │          │
│photo)│ └─────────┘  └──────────┘ └──────────┘ └──────────┘
└──┬───┘
   │
   ├─── CDN (CloudFront) ──► serves photos from edge locations
   │
┌──▼──────────┐
│ Kafka       │──► Background Workers
│ (async:     │    (compress, resize, thumbnail)
│  processing)│
└─────────────┘
```

### 12.7 Microservices Deep Dive

#### Photo Upload Service

```
POST /photos
  Request: photo file, user_id, caption, location
  Response: { photo_id, url }
```

**Upload flow:**
1. Client sends photo + metadata.
2. API Gateway routes to Photo Upload Service.
3. Service validates, generates `photo_id`, stores metadata in DB.
4. Uploads original to S3.
5. Sends message to Kafka for async processing.
6. Returns photo details immediately (fast response).

**Async processing (background workers):**
```
Kafka message → Worker:
  1. Compress photo (reduce size)
  2. Generate multiple resolutions (for different devices)
  3. Create thumbnail
  4. Store processed files in S3
  5. Update DB with processed file URLs
```

**Photo retrieval:**
1. `GET /photos/{photoId}` → fetch metadata from DB.
2. If not in CDN, fetch from S3.
3. Return photo URL (client fetches from CDN).

#### News Feed Service

```
GET /newsfeed/{userId}
  Params: pagination token, limit
  Response: list of photo objects
```

**Feed generation:**
1. Retrieve user's followee list from Follow table.
2. For each followee, fetch recent photos from DB.
3. **Rank** photos: chronological, engagement-based, or hybrid (timestamp
   + affinity + engagement).
4. **Paginate:** cursor-based (last photo_id or timestamp).
5. **Deduplicate:** maintain a set of photo_ids already in the feed.
6. **Cache** the generated feed in Redis.

**Real-time updates:**
- **WebSocket / long polling:** push new photos to active clients.
- **Notification service:** send push notifications for important updates.

**Feed synchronization (multi-device):**
- Timestamp-based: client sends last-viewed timestamp, server returns
  photos added since then.
- Incremental updates: client sends last photo_id, server returns only
  new/updated items.

#### User Service

```
POST   /users                         — register
POST   /users/login                   — login
GET    /users/{userId}                — profile
PUT    /users/{userId}                — update profile
POST   /users/{userId}/follow         — follow
DELETE /users/{userId}/follow         — unfollow
```

- Passwords hashed with **bcrypt**.
- Auth via **JWT** with expiration.
- User profiles cached in Redis (especially popular users).

### 12.8 Feed Generation — Ranking Approaches

| Approach | How it works | When to use |
|----------|-------------|-------------|
| Chronological | Sort by timestamp | Simple, expected behavior |
| Engagement-based | Score by likes + comments + recency | Maximize engagement |
| Hybrid | Weighted: recency + affinity + engagement | Instagram's actual approach |
| ML-based | Trained model predicts user interest | Advanced, personalized |

### 12.9 Q&A — Instagram

**Q1: Why store photos in S3 rather than a database?**
A: Photos are large binary objects (5MB avg). Relational databases are
optimized for structured data, not blobs. S3 provides virtually unlimited
scalability, 11 nines of durability, and is significantly cheaper per TB
than database storage. The DB stores only the photo URL reference.

**Q2: How do you prevent duplicate photos from appearing in the news
feed?**
A: The News Feed Service maintains a deduplication set (a Redis set of
photo_ids already in the user's feed). Before adding a photo, it checks
if the photo_id exists in the set. If it does, the photo is skipped.

**Q3: Why use a CDN for photo delivery?**
A: Instagram delivers ~50 PB/day of photos. Serving all of these from a
single origin would create enormous bandwidth costs and latency. A CDN
caches photos at edge locations geographically close to users, reducing
latency by 50–80% and reducing origin load. Only cache misses hit the
origin S3.

**Q4: How does photo processing work asynchronously?**
A: When a photo is uploaded, the service immediately stores the original
in S3 and returns a response. A Kafka message is published with the
photo_id and processing instructions. Background workers consume these
messages, compress/resize/thumbnail the photo, and store the processed
versions. This ensures the upload API returns instantly (sub-second)
while heavy processing happens in the background.

**Q5: How would you implement the Explore/Discover tab?**
A: Use a recommendation system that combines: (1) content-based
filtering (photos similar to what the user likes), (2) collaborative
filtering (photos liked by similar users), and (3) trending/popular
photos. Pre-compute recommendations offline (batch ML job) and cache them
in Redis. The Explore API returns cached recommendations with real-time
trending overlays.

---

## Chapter 13: Google Docs

### 13.1 Overview

Google Docs is a collaborative document editing platform enabling
real-time multi-user editing, version history, comments, suggestions,
sharing, and access control. The core technical challenge is **Operational
Transformation (OT)** — resolving concurrent edits to maintain consistency.

### 13.2 Functional Requirements

| Area | Requirements |
|------|-------------|
| Auth | Registration, login, session management |
| Document CRUD | Create, read, update, delete documents |
| Real-time collaboration | Multiple users edit simultaneously; changes sync in real-time |
| Presence awareness | See other collaborators' cursors and online status |
| Sharing | Share via links; access levels (view, comment, edit) |
| Version history | Auto-save revisions; view/restore previous versions |
| Comments & suggestions | Add comments; suggest edits without modifying doc |
| Search & organization | Search by title/content; organize into folders |

### 13.3 Non-Functional Requirements

| NFR | Detail |
|-----|--------|
| Scalability | Horizontal; independent scaling of Document/Collaboration services |
| Availability | Minimal downtime, geo-redundancy |
| Latency | Real-time collaboration with minimal delay |
| Consistency | Strong consistency across replicas; conflict resolution for concurrent edits |

### 13.4 Data Model

```
┌──────────────┐       ┌──────────────┐
│    User      │       │  Document    │
├──────────────┤       ├──────────────┤
│ user_id (PK) │◄──────│ doc_id (PK)  │
│ username     │       │ owner_id(FK) │
│ email        │       │ title        │
│ password_hash│       │ content_url  │
│ created_at   │       │ version      │
│ last_login   │       │ created_at   │
└──────┬───────┘       │ updated_at   │
       │               └──────┬───────┘
       │                      │
       ▼                      ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
│CollaboratorPerms │  │  Revision    │  │   Comment    │
├──────────────────┤  ├──────────────┤  ├──────────────┤
│ user_id (FK)     │  │ revision_id  │  │ comment_id   │
│ doc_id (FK)      │  │ doc_id (FK)  │  │ doc_id (FK)  │
│ permission_level │  │ user_id (FK) │  │ user_id (FK) │
│ granted_at       │  │ content      │  │ content      │
│  (view/comment/  │  │ timestamp    │  │ created_at   │
│   edit/owner)    │  │ version_num  │  └──────────────┘
└──────────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
│  Suggestion  │  │     Folder       │  │FolderDocument│
├──────────────┤  ├──────────────────┤  ├──────────────┤
│ suggestion_id│  │ folder_id (PK)   │  │ folder_id    │
│ doc_id (FK)  │  │ user_id (FK)     │  │ doc_id       │
│ user_id (FK) │  │ name             │  └──────────────┘
│ content      │  │ created_at       │  (many-to-many)
│ status       │  └──────────────────┘
│  (pending/   │
│   accepted/  │
│   rejected)  │
│ created_at   │
└──────────────┘
```

### 13.5 Scale Calculations

```
Assumptions:
  Users:                  10M
  Documents/user:         100
  Avg document size:      50 KB
  Revisions/document:     10
  Collaborators/document: 5
  Comments/document:      20

STORAGE:
  Documents:   10M × 100 × 50KB = 50 TB
  Revisions:   1B × 10 × 50KB   = 500 TB
  Comments:    1B × 20 × 1KB    = 20 TB
  Permissions: 1B × 5 × 1KB     = 5 TB
  ─────────────────────────────
  Total:       ≈ 575 TB

BANDWIDTH:
  Uploads:       10M × 1 × 50KB/day     = 500 GB/day
  Downloads:     10M × 10 × 50KB/day    = 5 TB/day
  Collaboration: 10M × 10 × 5 × 10KB/day = 5 TB/day
  ─────────────────────────────────────
  Total:         ≈ 10.5 TB/day

THROUGHPUT:
  Peak renders/sec:         10M × 10 / 86400 ≈ 1,200
  Peak collaboration updates/sec:
    5M concurrent × 1/min / 60 ≈ 83,000 updates/sec
```

### 13.6 High-Level Architecture

```
┌──────────┐
│  Clients  │  (Browser, Mobile — WebSocket connections)
└─────┬─────┘
      │
┌─────▼──────────┐
│  Load Balancer  │
└─────┬──────────┘
      │
┌─────▼──────────┐
│  API Gateway    │  (auth, routing, rate limiting)
└──┬──┬───┬───┬──┘
   │  │   │   │
   ▼  ▼   ▼   ▼
┌──────┐┌──────────────┐┌──────────┐┌──────────────┐┌──────────┐
│Doc   ││Collaboration ││Revision  ││Access Control││Notification│
│Svc   ││Service       ││Service   ││Service       ││Service   │
│      ││(OT engine,   ││          ││(auth, perms) ││          │
│      ││ WebSocket)   ││          ││              ││          │
└──┬───┘└──────┬───────┘└────┬─────┘└──────┬───────┘└──────────┘
   │           │             │             │
   ▼           ▼             ▼             ▼
┌──────┐ ┌─────────┐  ┌──────────┐  ┌──────────┐
│ S3 / │ │  Redis  │  │PostgreSQL│  │PostgreSQL│
│Cloud │ │(doc     │  │(revisions│  │(users,   │
│Store │ │ state,  │  │  history)│  │ perms,   │
│(content)│presence)│  │          │  │ tokens)  │
└──────┘ └─────────┘  └──────────┘  └──────────┘
                   │
                   │  collaboration events via
                   ▼
              ┌─────────┐
              │ Kafka   │──► broadcast to WebSocket clients
              └─────────┘
```

### 13.7 Operational Transformation (OT) — The Core Algorithm

OT is the technique that enables conflict-free concurrent editing. The
goal: regardless of the order in which operations arrive at the server,
all clients converge to the same final document state.

**Basic principle:**
```
If two operations Op1 and Op2 are concurrent (both based on the same
document state), transform one against the other so they can be applied
in any order and produce the same result.

  T(Op1, Op2) = Op1'   (Op1 transformed by Op2)
  Apply(Op2); Apply(Op1')  ==  Apply(Op1); Apply(Op2')
```

**Example — concurrent insert:**
```
Document state: "Hello"
  User A inserts "X" at position 5 → "HelloX"
  User B inserts "Y" at position 5 → "HelloY"

These are concurrent. Without OT:
  Server receives A then B: "HelloXY"  ← but B expected position 5!

With OT:
  Server transforms B's op against A's:
    T(Insert("Y", 5), Insert("X", 5)) = Insert("Y", 6)
  Result: "HelloXY" ✓ (consistent for all clients)
```

**Server-side OT flow:**
```
                     ┌─────────────────┐
   User A ──────────►│                 │
   sends Op1         │  Collaboration  │     ┌───────────────┐
                     │  Service        │────►│ Transform     │
   User B ──────────►│  (maintains     │     │ Op against    │
   sends Op2         │   server state  │     │ operation     │
   (concurrent)      │   + history)    │     │ history       │
                     └─────────────────┘     └───────┬───────┘
                                                     │
                            ┌────────────────────────┘
                            ▼
                    ┌───────────────┐
                    │ Apply to      │
                    │ server state  │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ Broadcast     │
                    │ transformed   │──► All connected clients
                    │ ops via       │    (WebSocket)
                    │ WebSocket     │
                    └───────────────┘
```

**Collaboration flow (step-by-step):**
1. User joins session → `POST /collaborate/{docId}`.
2. Collaboration Service checks access permissions.
3. Returns initial document state + session details.
4. Client opens WebSocket connection.
5. As user edits, client sends collaboration events (insert, delete,
   format) via WebSocket.
6. Server applies OT to resolve conflicts.
7. Transformed events broadcast to all clients.
8. Clients update local state.

### 13.8 Presence Management

```
Presence Map (in Redis):
  doc_id → { user_id: { status, cursor_pos, last_active } }

  Example:
  "doc_123" → {
    "user_1": { status: "online", cursor: 42, color: "blue" },
    "user_2": { status: "idle",   cursor: 17, color: "green" }
  }
```

- Clients send presence updates via `POST /presence/{docId}`.
- Server periodically checks for inactive clients → marks offline.
- Presence changes broadcast to other collaborators.

### 13.9 Offline Support

```
Browser Cache (IndexedDB / LocalStorage)
     │
     │ stores local edits
     │
     ▼
  Network restored?
     │
     ├─ Yes → sync local edits with server (conflict resolution via OT)
     └─ No  → continue offline; sync when reconnected
```

**Benefits:**
- Faster UI (immediate local reflection)
- Offline editing
- Network resilience (no lost work)
- Reduced server load (batched sync)

### 13.10 Q&A — Google Docs

**Q1: What is Operational Transformation and why is it needed?**
A: OT is a conflict resolution algorithm for concurrent document editing.
When two users edit the same document simultaneously, their operations
may conflict (e.g., both insert at the same position). OT transforms each
operation based on previously applied operations so that all clients
converge to the same state regardless of operation arrival order. Without
OT, concurrent edits would cause data loss or inconsistency.

**Q2: Why use WebSocket instead of HTTP for collaboration?**
A: Collaboration requires bidirectional, low-latency communication — the
server must push changes from other users instantly. HTTP is
request-response (client must poll), adding latency. WebSocket provides a
persistent, full-duplex connection ideal for real-time collaboration. SSE
is an alternative for server-to-client only, but collaboration needs
client-to-server too.

**Q3: How do you handle a client that goes offline and comes back with
stale edits?**
A: Each operation carries a revision number (the document state it was
based on). When the client reconnects, the server compares the client's
revision with the current server revision. If the client is behind, the
server transforms the client's operations against all operations that
have been applied since the client's revision. This is called "catch-up
transformation" and ensures the client's edits are applied correctly.

**Q4: How is version history stored efficiently?**
A: Rather than storing full document copies for each revision, store
**deltas** (diffs) between versions. The Revision Service computes diffs
using algorithms like Myers' diff. To reconstruct version N, apply the
delta chain from the last full snapshot to N. Periodically create full
snapshots to bound reconstruction time. This reduces storage from O(N ×
doc_size) to O(N × delta_size).

**Q5: How does the Access Control Service enforce permissions at scale?**
A: Permissions are cached in Redis (keyed by `doc_id + user_id`). When a
user attempts an operation, the Collaboration Service checks the cache
first (sub-millisecond). Cache misses fall through to PostgreSQL. Access
tokens (JWT) contain the user's role and are verified on every request.
Permission changes (revocation) invalidate the cache entry.

---

## Chapter 14: Netflix

### 14.1 Overview

Netflix is a video streaming platform serving personalized content to
millions of users worldwide. Key challenges include massive video
storage, transcoding into multiple formats/bitrates, CDN-based content
delivery, adaptive bitrate streaming, DRM, and ML-powered
recommendations.

### 14.2 Functional Requirements

| Area | Requirements |
|------|-------------|
| Auth | Registration, login, multi-device sessions |
| Content browsing | Browse catalog by genre/category; search by title/actor/director |
| Video playback | Seamless streaming with minimal buffering; play/pause/seek/resume |
| Profiles | Multiple profiles per account; personalized watch history |
| Recommendations | Personalized suggestions based on history + similar users |
| Watchlist & history | Save titles; sync across devices; resume playback |
| Offline viewing | Download titles; secure storage; expiration per licensing |

### 14.3 Non-Functional Requirements

| NFR | Detail |
|-----|--------|
| Scalability | Handle millions of concurrent users; horizontal scaling |
| Availability | Minimal downtime; redundancy, failover, disaster recovery |
| Content delivery | CDN for global distribution; adaptive bitrate streaming |
| Streaming quality | Minimize buffering; support multiple formats/codecs |

### 14.4 Data Model

```
┌──────────────┐       ┌──────────────┐
│    User      │       │   Profile    │
├──────────────┤       ├──────────────┤
│ user_id (PK) │◄──────│ profile_id   │
│ email        │  1:M  │ user_id (FK) │
│ password     │       │ name         │
│ subscription │       │ avatar       │
│ created_at   │       │ preferences  │
└──────────────┘       │ parental_ctrl│
                       └──────┬───────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │WatchHistory  │ │  Watchlist   │ │   Rating     │
    ├──────────────┤ ├──────────────┤ ├──────────────┤
    │ history_id   │ │ watchlist_id │ │ rating_id    │
    │ profile_id   │ │ profile_id   │ │ profile_id   │
    │ content_ref  │ │ content_ref  │ │ content_ref  │
    │ progress     │ │ added_at     │ │ score        │
    │ watched_at   │ └──────────────┘ │ rated_at     │
    └──────────────┘                  └──────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Movie      │  │   TVShow     │  │  Episode     │
├──────────────┤  ├──────────────┤  ├──────────────┤
│ movie_id(PK) │  │ show_id (PK) │  │ episode_id   │
│ title        │  │ title        │  │ show_id (FK) │
│ description  │  │ description  │  │ season_num   │
│ duration     │  │ genre        │  │ episode_num  │
│ genre        │  │ release_year │  │ title        │
│ release_year │  │ rating       │  │ duration     │
│ rating       │  └──────┬───────┘  └──────┬───────┘
└──────┬───────┘         │ 1:M            │
       │                 └────────────────┘
       │                          │
       ▼                          ▼
    ┌─────────────────────────────────┐
    │      ContentMetadata            │
    ├─────────────────────────────────┤
    │ metadata_id (PK)                │
    │ content_ref (movie/show/episode)│
    │ video_quality (HD, 4K, SD)      │
    │ file_size                       │
    │ codec (H.264, H.265, VP9)       │
    │ bitrate                         │
    │ language/audio_track            │
    │ file_url (in CDN/storage)       │
    └─────────────────────────────────┘
```

### 14.5 Scale Calculations

```
Assumptions:
  Users:                50M
  DAU:                  10M
  Videos watched/user/day: 3
  Avg video duration:   1.5 hours
  Avg video file size:  3 GB (HD)

CATALOG:
  Movies:        10,000
  TV shows:      5,000 (avg 30 episodes each)
  Episodes:      5,000 × 30 = 150,000
  Total files:   160,000

STORAGE:
  Video storage:     160,000 × 3 GB = 480 PB
  User data:         50M × 1KB = 50 GB
  Profile data:      50M × 5 × 1KB = 250 GB
  Watch history:     50M × 5 × 1MB = 250 TB
  Content metadata:  160,000 × 10KB = 1.6 GB
  ─────────────────────────────────────
  Total:             ≈ 480 PB

BANDWIDTH:
  Daily streaming:    10M × 3 × 3GB = 90 PB/day
  Peak concurrent:    1M users
  Peak bandwidth:     1M × 3GB / 1.5h = 2 TB/s

PROCESSING:
  New videos/day:     100
  Encoding/video:     1.5h × 5 bitrates = 7.5 hours
  Daily encoding:     100 × 7.5 = 750 hours
  Recommendation req: 10M × 10 = 100M/day
```

### 14.6 High-Level Architecture

```
┌──────────────────────────────────────────────────┐
│              Client Applications                  │
│  (Web, iOS, Android, Smart TV, Game Console)     │
└──────────────────────┬───────────────────────────┘
                       │
               ┌───────▼───────┐
               │  API Gateway   │ (auth, routing, rate limiting)
               └───┬──┬──┬──┬──┘
                   │  │  │  │
    ┌──────────────┘  │  │  └───────────────┐
    │                 │  │                  │
    ▼                 ▼  ▼                  ▼
┌────────┐  ┌──────────┐┌──────────┐┌──────────────┐
│Video   │  │User Svc  ││Recommend ││Search Svc    │
│Service │  │          ││Svc       ││              │
└───┬────┘  └────┬─────┘└────┬─────┘└──────┬───────┘
    │            │           │             │
    ▼            ▼           ▼             ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌─────────────┐
│Distrib │  │Postgres│  │ML Model│  │Elasticsearch│
│Storage │  │ (users)│  │Repo    │  │ (metadata)  │
│(S3/HDFS│  └────────┘  └────────┘  └─────────────┘
│for video│
│ files) │  ┌──────────────────────────────┐
└───┬────┘  │   Billing & Subscription    │
    │       │   Service                    │
    │       └──────────────────────────────┘
    │
    │  transcoding pipeline
    ▼
┌────────────────┐    ┌───────────┐
│ Encoding       │◄──│ Kafka     │
│ Workers        │   │ (async    │
│ (MP4, HLS,     │   │  jobs)    │
│  DASH, multi-  │   └───────────┘
│  bitrate)      │
└───────┬────────┘
        │ encoded segments
        ▼
┌───────────────────────────────────────────┐
│                  CDN                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │ Edge SF │ │Edge NYC │ │Edge LON │ ...  │
│  └────┬────┘ └────┬────┘ └────┬────┘      │
│       │           │           │            │
│       └───────────┴───────────┘            │
│                   │                        │
│          ┌────────▼────────┐               │
│          │  Origin Server  │               │
│          │  (master copies)│               │
│          └─────────────────┘               │
│                                            │
│  + Request Router (DNS LB → nearest edge)  │
│  + Adaptive Bitrate Streaming              │
│  + DRM Service (PlayReady / Widevine)      │
└───────────────────────────────────────────┘
```

### 14.7 Video Service Deep Dive

```
POST /videos              — upload new video
GET  /videos/{videoId}    — get metadata
GET  /videos/{videoId}/stream?quality=HD&offset=300
                          — stream video chunk/segment
```

**Video upload & storage:**
1. Video Service receives file + metadata.
2. Stores raw video in distributed storage (S3 / HDFS).
3. Stores metadata in DB (PostgreSQL / Cassandra) with reference to file
   location.

**Video encoding & transcoding:**
```
Raw video upload
      │
      ▼
  Kafka message (encoding job)
      │
      ▼
Encoding Workers:
  1. Transcode to multiple formats: MP4, HLS, DASH
  2. Multiple bitrates: 240p, 480p, 720p, 1080p, 4K
  3. Segment into small chunks (2-10 seconds each)
  4. Generate manifest files (HLS playlist / DASH MPD)
  5. Store encoded segments in S3
  6. Update metadata with locations
      │
      ▼
  Notify CDN Manager → propagate to edge servers
```

**Video streaming (adaptive bitrate):**
```
1. Client requests video stream
2. Video Service returns manifest file (HLS .m3u8 or DASH .mpd)
3. Client requests first segment at initial quality
4. Client monitors network conditions:
   - If bandwidth high → request higher quality segments
   - If bandwidth low  → request lower quality segments
5. Edge server serves segments (cache hit) or fetches from origin (miss)
6. Seamless quality transitions during playback
```

### 14.8 CDN Architecture

```
User in San Francisco requests "Stranger Things"
                    │
                    ▼
          ┌─────────────────┐
          │  DNS Load       │
          │  Balancer       │
          │  (geo-routes    │
          │   to nearest    │
          │   CDN entry)    │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Request Router │
          │  (considers:    │
          │   - user loc    │
          │   - server load │
          │   - latency     │
          │   - health)     │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │  Edge Server    │
          │  (SF)           │
          │                 │
          │  Cache hit?     │
          │  ┌─Yes→ serve   │
          │  └─No → fetch    │
          │        from origin│
          │        → cache    │
          │        → serve    │
          └─────────────────┘
```

**Content propagation:**
1. New video uploaded → transcoded into segments.
2. CDN Manager notified.
3. CDN Manager initiates propagation to edge servers.
4. Each edge server requests and caches segments from origin.
5. Popular content proactively pushed to all edges.

### 14.9 DRM (Digital Rights Management)

```
┌──────────┐         ┌──────────────┐         ┌──────────┐
│  Client   │────────►│  CDN / Edge  │────────►│  DRM     │
│ requests  │         │  Server      │         │  Service │
│ playback  │         │ (encrypted   │         │          │
│           │◄────────│  segments)   │◄────────│          │
│           │         └──────────────┘         └──────────┘
│           │
│  requests │
│  license  │──────────────────────────────────►│  DRM     │
│           │◄──────────────────────────────────│  Service │
│  receives │   (license key if authorized)     │  validates│
│  license  │                                   │  subscription│
│           │                                   └──────────┘
│  decrypts │
│  & plays  │
└──────────┘
```

**DRM systems:** Microsoft PlayReady, Google Widevine, Apple FairPlay.

- Video content is **encrypted** before storage on CDN.
- Only authorized users with valid DRM licenses can decrypt and play.
- Licenses are time-limited and device-bound.
- Complies with regional restrictions and licensing agreements.

### 14.10 Recommendation Service

```
GET /recommendations/{userId}   — get personalized recommendations
POST /events                    — record user event (watch, rate, search)
```

**Recommendation generation flow:**
```
1. Client requests recommendations
2. Recommendation Manager checks cache:
   ├─ Hit  → return cached recs
   └─ Miss → generate new:
       a. Fetch user behavior data (watch history, ratings)
       b. Fetch video metadata
       c. Load ML model from Model Repository
       d. Apply model → generate ranked recommendations
       e. Cache results
3. Return recommendations
```

**Model training pipeline:**
```
User behavior DB → Preprocess → Feature extraction
→ Train/Validate models → Deploy best model → Model Repository
```

### 14.11 Q&A — Netflix

**Q1: Why transcode videos into multiple bitrates and formats?**
A: Users watch Netflix on diverse devices (phones, TVs, browsers) with
varying network conditions (WiFi, cellular, slow broadband). Transcoding
into multiple bitrates (240p–4K) and formats (HLS, DASH) enables adaptive
bitrate streaming — the client dynamically switches quality based on
current bandwidth, ensuring smooth playback without buffering. Different
formats are needed because different devices support different codecs and
streaming protocols.

**Q2: How does the CDN decide which edge server to route a user to?**
A: The DNS Load Balancer first directs the user to the nearest CDN entry
point based on geography. Then the Request Router considers multiple
factors: user location, server availability, current network latency,
server load, and health status. It selects the optimal edge server that
minimizes latency while avoiding overloaded or unhealthy servers. This
ensures fast, reliable streaming.

**Q3: How does adaptive bitrate streaming work in practice?**
A: The video is segmented into small chunks (2–10 seconds). Each chunk is
available in multiple bitrates. The client player maintains a buffer and
monitors download speed. If chunks download faster than playback rate and
bandwidth is high, the client requests the next chunk at a higher
bitrate. If downloads are slow or bandwidth drops, it requests a lower
bitrate to prevent buffer underruns. The manifest file (HLS/DASH) tells
the client which bitrates and segments are available.

**Q4: How does DRM prevent piracy?**
A: Video content is encrypted before being placed on CDN edge servers.
Even if someone intercepts the encrypted segments, they cannot play them
without a decryption key. The DRM Service issues licenses only to
authenticated, authorized users with active subscriptions. Licenses are
device-bound and time-limited. DRM systems like Widevine and PlayReady
also include hardware-level protection (e.g., Secure Video Path) to
prevent screen recording.

**Q5: How does the recommendation system handle cold-start (new users)?**
A: For new users with no watch history, the system uses: (1) popular/trending
content globally, (2) demographic-based recommendations (age, location,
registration preferences), (3) explicit onboarding questions (genre
selection during signup). As the user watches content, collaborative
filtering and content-based models kick in. The system continuously
learns and adapts — the more data, the better the recommendations.

---

## Chapter 15: Interview Tips

### 15.1 Overview

System design interviews test your ability to architect scalable,
efficient, and robust systems. They often determine your level (e.g.,
L vs. L+1) and compensation. This chapter covers preparation strategies
and in-interview techniques.

### 15.2 Preparation Tips

#### Master the Fundamentals

| Topic | Key Concepts |
|-------|-------------|
| **Scalability** | Horizontal vs. vertical scaling, load balancing, distributed systems |
| **Databases** | SQL vs. NoSQL, indexing, sharding, replication, when to use which |
| **Caching** | Strategies (write-through, write-back, cache-aside), eviction (LRU, LFU, TTL), Redis/Memcached |
| **Consistency** | CAP theorem, PACELC, strong vs. eventual consistency, trade-offs |

#### Study Design Patterns

| Pattern | When to use |
|---------|------------|
| Microservices | Independent scaling, domain separation |
| Event-driven | Async processing, decoupling via Kafka |
| CQRS | Separate read/write models for high-throughput systems |
| Saga | Distributed transactions across microservices |
| Circuit Breaker | Prevent cascading failures in distributed systems |

#### Practice Methods

- **Mock interviews:** Pramp, Interviewing.io, Exponent — simulate real
  interviews with peers or professional interviewers.
- **Design challenges:** LeetCode, HackerRank, Grokking the System Design
  Interview.
- **Case studies:** Analyze real architectures (Twitter, Uber, Netflix
  engineering blogs).

#### Resources

- **Books:** *Designing Data-Intensive Applications* (Kleppmann),
  *The Art of Scalability* (Abbott & Fisher)
- **Courses:** Grokking the System Design Interview (Educative),
  Coursera, Udemy
- **Blogs:** Netflix TechBlog, Uber Engineering, LinkedIn Engineering
- **YouTube:** Gaurav Sen, Tushar Roy, Tech Dummies

#### Communication Skills

- Practice verbalizing your thought process out loud.
- Learn to draw architecture diagrams and sequence diagrams.
- Write and speak simultaneously during interviews.

### 15.3 In-Interview Strategy

#### Step 1: Understand the Problem (3-5 min)

```
Ask clarifying questions:
  - What is the scale? (users, RPS, data volume)
  - What are the core features?
  - Are there specific latency/availability requirements?
  - Is this read-heavy or write-heavy?

Identify:
  - Functional requirements (what the system must DO)
  - Non-functional requirements (how the system must PERFORM)
```

**Tip:** Don't spend too long brainstorming features. Be focused and get
clarification from the interviewer.

#### Step 2: Write Non-Functional Requirements

Don't just say "highly available" — be specific:
- ❌ "The system should be highly available"
- ✅ "99.99% availability for the payment service; 99.9% for analytics"

Don't just say "highly consistent" — talk about specific sub-use cases:
- ✅ "Strong consistency for order creation; eventual consistency for
  product catalog updates"

#### Step 3: List APIs (5 min)

```
REST APIs for client-facing operations
Internal function/method signatures for service-to-service

Example (URL Shortener):
  POST /shorturl         → create short URL
  GET  /shorturls/{id}   → resolve to long URL
```

#### Step 4: Do Estimations (5 min)

```
Make estimates PURPOSEFUL — they should influence design choices.
Use round numbers (≈ powers of 10) for easy mental math.

86,400 sec/day ≈ 100,000 sec/day (for quick estimates)
```

#### Step 5: Draw High-Level Block Diagram (5-7 min)

```
Draw the major components:
  Client → LB → API Gateway → Services → Databases/Cache/Storage

This helps identify:
  - Single points of failure
  - Bottlenecks
  - Core challenges to address
```

#### Step 6: Address Core Challenges (10-15 min)

```
For each bottleneck:
  1. Brainstorm 2-3 solution options
  2. Discuss pros/cons of each
  3. Make a trade-off decision with justification
  4. Listen to interviewer hints — they're clues!
```

#### Step 7: Final Architecture + Verification (5 min)

```
1. Draw the final refined architecture
2. Walk through the flows (write + read)
3. Verify ALL functional requirements are met
4. Verify ALL non-functional requirements are met
```

### 15.4 Communication Checklist

| Do | Don't |
|----|-------|
| Structure your presentation logically | Jump into details without context |
| Explain trade-offs with reasoning | Pick a technology without justification |
| Listen to interviewer hints | Ignore steering signals |
| Use diagrams while talking | Only talk without visual aids |
| Summarize at the end | Leave the interview hanging |
| Be ready for follow-up questions | Assume one answer covers everything |
| Mention reliability, observability, debuggability | Forget operational concerns |
| Leverage past experience | Be purely theoretical |

### 15.5 Key Insight

> "Presenting your solution clearly is as important as the solution
> itself. I've seen candidates with brilliant designs fail because they
> couldn't articulate their ideas. And I've seen candidates with simpler
> designs excel because they communicated their thought process and
> trade-offs with clarity."

**Communication can be the difference between L and L+1 leveling.**

### 15.6 Common Pitfalls

```
❌ Jumping into solution without understanding requirements
❌ Spending too long on estimations without purpose
❌ Not drawing diagrams
❌ Ignoring interviewer hints
❌ Being too vague on NFRs ("highly available")
❌ Not discussing trade-offs
❌ Forgetting to verify requirements at the end
❌ Over-engineering early (start simple, then refine)
```

---

## Chapter 16: System Design Cheat Sheet

### 16.1 Interview Structure (9 Steps)

```
1.  Ask and clarify the problem
2.  List functional requirements
3.  List non-functional requirements
4.  Write down the APIs
5.  Do high-level estimates and calculations
6.  Draw initial high-level design diagram
7.  Identify core challenges → brainstorm options → trade-offs
8.  Final high-level architecture diagram + flows
9.  Verify all functional and non-functional requirements
```

### 16.2 Data Store Selection Guide

| Use Case | Recommended Data Store |
|----------|----------------------|
| Structured data, ACID, not too many joins | **Relational DB** (PostgreSQL, MySQL) — shard for scale |
| Unstructured, sparse, document variety | **Document DB** (MongoDB, Couchbase) |
| Massive scale, ever-increasing, wide rows, few columns queried | **Columnar** (HBase = consistency; Cassandra = availability, tunable) |
| Fast key-value lookups | **Redis / Memcached** |
| Full-text search | **Elasticsearch / Solr / Lucene** |
| Fast writes (append-only) | **WAL** (Write-Ahead Log) |
| Fast reads | **Cache + Replicas + In-Memory + CDN** |
| Blob storage (video, images) | **S3 + CDN** |
| Complex graph relationships | **Graph DB** (Neo4j) |
| Hot data | **In-memory / SSD** |
| Cold data | **Disk / Amazon Glacier** |
| Similarity search (AI/ML, embeddings) | **Vector DB** (Pinecone, Milvus, Weaviate) |
| Time-series metrics | **Time-series DB** (OpenTSDB, InfluxDB) |
| Proximity / nearby entity search | **Geo-spatial index** (Quadtree, Geohash) |

### 16.3 Data Structure Selection Guide

| Use Case | Data Structure |
|----------|---------------|
| Membership test, space-efficient, tolerates false positives (cache dedup, spam filter) | **Bloom Filter** |
| Frequency estimation in data streams (heavy hitters, trending, network traffic) | **Count-Min Sketch** |
| Cardinality estimation (unique users, unique IPs, ad reach) | **HyperLogLog** |
| Data integrity verification (Git commits, P2P file sharing, software updates) | **Merkle Tree** |

### 16.4 Component Selection Guide

| Component | Purpose | Example Use Cases |
|-----------|---------|-------------------|
| **Load Balancer** | Distribute traffic across servers | Web apps, DB read replicas |
| **Proxy** | Intermediary between device and internet (privacy, security, filtering) | Anonymity, content filtering |
| **Reverse Proxy** | Middleman between internet and web app (protection, caching) | E-commerce traffic, CDN caching, microservice routing |
| **Rate Limiter** | Prevent overload, ensure fair access | API protection, login attempt limits, e-commerce fraud prevention |
| **Circuit Breaker** | Prevent cascading failures | Microservice isolation, external API protection |
| **API Gateway** | Single entry point for microservices | Routing, auth, rate limiting, monitoring |
| **Message Queue** | Decoupled async communication | Order processing, task queues, feed updates |
| **CDN** | Geographically distributed content delivery | Websites, streaming, social media |

### 16.5 Protocol Selection Guide

| Feature | HTTP | SSE | WebSockets |
|---------|------|-----|------------|
| **Communication** | Request-response | Unidirectional (server→client) | Bidirectional |
| **Connection** | Short-lived | Long-lived | Long-lived |
| **Data format** | Text (HTML, JSON) | Text (event-stream) | Text + binary |
| **Latency** | High | Low | Very low |
| **Scalability** | High (stateless) | Moderate | Moderate (careful management) |
| **Auto-reconnect** | No | Yes | Application-managed |
| **Overhead** | High (repeated handshakes) | Low | Low |
| **Browser support** | Universal | Modern browsers | Modern browsers |

**Protocol → Use Case mapping:**

| Use Case | Protocol | Why |
|----------|----------|-----|
| Static content, REST APIs, form submissions, file transfers | **HTTP** | Simple, stateless, widely supported |
| Real-time notifications, live feeds, monitoring dashboards | **SSE** | Simple, auto-reconnect, server→client |
| Simple chat/messaging | **SSE** | Unidirectional updates sufficient |
| Online gaming, real-time chat, collaborative tools, financial apps, IoT | **WebSockets** | Low-latency, bidirectional |

### 16.6 Core Challenge → Solution Map

| Core Challenge | Potential Solutions |
|----------------|-------------------|
| **High write throughput** | WAL, Sharding, NoSQL databases |
| **Data consistency** | Distributed transactions (2PC), Eventual consistency, Conflict resolution |
| **Low-latency requirements** | In-memory DBs (Redis), Caching (Memcached), Edge computing |
| **Scalability** | Horizontal scaling, Load balancing, Microservices |
| **Fault tolerance** | Replication, Failover mechanisms, Circuit breakers |
| **Data partitioning** | Hash partitioning, Range partitioning, Consistent hashing |
| **Search performance** | Inverted index, Elasticsearch, Caching |
| **Spiky traffic** | Autoscaling, Load smoothing (queuing/rate limiting), CDNs |
| **Distributed locking** | DLMs, ZooKeeper, Redis |

### 16.7 Quick Reference: Common Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM DESIGN PATTERNS                     │
├──────────────────┬──────────────────────────────────────────┤
│ Fanout-on-Write  │ Pre-compute feeds on write (Twitter,     │
│                  │ Instagram timelines)                     │
├──────────────────┼──────────────────────────────────────────┤
│ Fanout-on-Read   │ Compute feeds on read (lazy evaluation)  │
├──────────────────┼──────────────────────────────────────────┤
│ Hybrid Fanout    │ Push for normal users, pull for celebs   │
├──────────────────┼──────────────────────────────────────────┤
│ CQRS             │ Separate read/write models               │
├──────────────────┼──────────────────────────────────────────┤
│ Event Sourcing   │ Store events as source of truth          │
├──────────────────┼──────────────────────────────────────────┤
│ Saga Pattern     │ Distributed transactions via compensating│
│                  │ events                                  │
├──────────────────┼──────────────────────────────────────────┤
│ Circuit Breaker  │ Fail fast, don't cascade failures        │
├──────────────────┼──────────────────────────────────────────┤
│ Bulkhead         │ Isolate resources to prevent total       │
│                  │ failure                                 │
├──────────────────┼──────────────────────────────────────────┤
│ Backpressure     │ Slow down producers when consumers      │
│                  │ can't keep up                            │
├──────────────────┼──────────────────────────────────────────┤
│ Consistent       │ Minimize data movement when adding/      │
│ Hashing          │ removing nodes                           │
├──────────────────┼──────────────────────────────────────────┤
│ Operational      │ Transform concurrent ops for conflict-  │
│ Transformation   │ free collaborative editing               │
├──────────────────┼──────────────────────────────────────────┤
│ Adaptive Bitrate │ Dynamically switch video quality based  │
│ Streaming        │ on network conditions                    │
├──────────────────┼──────────────────────────────────────────┤
│ Write-Ahead Log  │ Durability via append-only log before    │
│ (WAL)            │ applying to data structure               │
└──────────────────┴──────────────────────────────────────────┘
```

### 16.8 Quick Reference: Number Cheatsheet

```
Time:
  1 minute  = 60 seconds
  1 hour    = 3,600 seconds
  1 day     = 86,400 seconds  (≈ 100,000 for estimates)
  1 year    = 365 days ≈ 31.5M seconds

Storage:
  1 KB  = 10^3 bytes
  1 MB  = 10^6 bytes
  1 GB  = 10^9 bytes
  1 TB  = 10^12 bytes
  1 PB  = 10^15 bytes

Bandwidth:
  1 Gbps = 125 MB/s
  10 Gbps = 1.25 GB/s

Key math:
  62^6  = 56.8 billion
  62^7  = 3.5 trillion
  2^10  = 1,024  (≈ 10^3)
  2^20  = 1,048,576  (≈ 10^6)
  2^30  = 1,073,741,824  (≈ 10^9)

Availability:
  99.9%   = 8.76 hours downtime/year
  99.99%  = 52.6 minutes downtime/year
  99.999% = 5.26 minutes downtime/year

Typical latency:
  Memory access:        ~100 ns
  SSD read:             ~100 μs
  LAN round trip:       ~0.5 ms
  DB query (indexed):   ~1-10 ms
  Disk seek:            ~10 ms
  Cross-DC round trip:  ~30-100 ms
```

### 16.9 Final Interview Checklist

```
□ Understood the problem and asked clarifying questions
□ Listed 3-5 core functional requirements
□ Listed specific (not vague) non-functional requirements
□ Wrote down key APIs
□ Did purposeful estimations (influenced design)
□ Drew initial high-level block diagram
□ Identified core challenges/bottlenecks
□ Brainstormed multiple options with trade-offs
□ Drew final refined architecture
□ Walked through write and read flows
□ Verified ALL functional requirements
□ Verified ALL non-functional requirements
□ Discussed reliability/observability/debuggability
□ Summarized the design
□ Was collaborative and listened to hints
□ Used diagrams while explaining
□ Explained trade-offs with reasoning
```

---

## Cross-Chapter Comparison

### Architecture Patterns Across Systems

| System | Primary DB | Cache | Message Queue | Key Challenge |
|--------|-----------|-------|---------------|---------------|
| URL Shortener | Redis (KV) | LRU Cache | — | Unique ID generation |
| Proximity | PostgreSQL + Quadtree | — | — | 2D spatial search |
| Twitter | Cassandra | Redis (timelines) | Kafka | Timeline fanout at scale |
| Instagram | PostgreSQL + S3 | Redis (feed) | Kafka | Media storage + feed ranking |
| Google Docs | PostgreSQL + S3 | Redis (doc state) | Kafka | OT for concurrent editing |
| Netflix | PostgreSQL + S3 | Redis (recs) | Kafka | Video transcoding + CDN + DRM |

### Read/Write Ratios

| System | Read:Write Ratio | Primary Bottleneck |
|--------|-----------------|-------------------|
| URL Shortener | 100:1 | Write (unique ID gen) |
| Proximity | 1000:1 | Read (spatial search) |
| Twitter | 1000:1 (timeline reads) | Write (fanout) |
| Instagram | 100:1 (feed reads) | Write (media processing) |
| Google Docs | 1:1 (collaboration) | Latency (real-time sync) |
| Netflix | 1000:1 (streaming) | Bandwidth (video delivery) |

### Common Building Blocks

All six systems use some combination of:

```
┌────────────────────────────────────────────────────────────────┐
│                     UNIVERSAL BUILDING BLOCKS                    │
├────────────────┬───────────────────────────────────────────────┤
│ Load Balancer  │ Every system — distribute traffic              │
│ API Gateway    │ Every system — routing, auth, rate limiting   │
│ Cache (Redis)  │ Every system — reduce DB load, low latency    │
│ Message Queue  │ Twitter, Instagram, Google Docs, Netflix      │
│                │ — async processing, decoupling                 │
│ Object Storage │ Twitter (media), Instagram (photos),          │
│ (S3)           │ Google Docs (content), Netflix (video)        │
│ CDN            │ Instagram (photos), Netflix (video)           │
│ Search Engine  │ Twitter (Elasticsearch), Netflix (ES)         │
│ (Elasticsearch)│                                               │
└────────────────┴───────────────────────────────────────────────┘
```

---

## Appendix: Key Formulas

### Base62 Encoding

```python
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def encode(num):
    if num == 0:
        return CHARS[0]
    result = []
    while num > 0:
        result.append(CHARS[num % 62])
        num //= 62
    return ''.join(reversed(result))

def decode(s):
    num = 0
    for c in s:
        num = num * 62 + CHARS.index(c)
    return num
```

### Geohash Encoding (simplified)

```python
BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"

def encode_geohash(lat, lon, precision=12):
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    even = True
    while len(geohash) < precision:
        if even:
            mid = (lon_range[0] + lon_range[1]) / 2
            if lon >= mid:
                ch |= bits[bit]
                lon_range[0] = mid
            else:
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat >= mid:
                ch |= bits[bit]
                lat_range[0] = mid
            else:
                lat_range[1] = mid
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash.append(BASE32[ch])
            bit = 0
            ch = 0
    return ''.join(geohash)
```

### Snowflake ID (Twitter-style)

```
  1 bit    |  41 bits timestamp  | 10 bits machine | 12 bits sequence
  (unused) |  (ms since epoch)   |    ID           |    number

  Total: 64 bits → fits in a bigint
  Can generate 4096 IDs per ms per machine
  41 bits → ~69 years of timestamps
  10 bits → 1024 machines
```

---

> **End of Sinha System Design Guide — Chapters 9–16 Deep Dive**
>
> This document covers URL Shortener, Proximity Service, Twitter, Instagram,
> Google Docs (OT/collaboration), Netflix (transcoding/CDN/DRM), Interview
> Tips, and the System Design Cheat Sheet. Each chapter includes architecture
> diagrams, data models, APIs, estimations, and 5 interview Q&As.
