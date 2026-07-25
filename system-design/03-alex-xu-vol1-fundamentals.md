# Alex Xu Vol 1 — System Design Interview Fundamentals (Chapters 1-3)

> **Source:** "System Design Interview — An Insider's Guide (2nd Edition)" by Alex Xu
> **Coverage:** Chapter 1 (Scaling), Chapter 2 (Estimation), Chapter 3 (Framework)
> **Purpose:** Master the foundational knowledge and interview framework before diving into specific problems.

---

## TABLE OF CONTENTS

1. [Chapter 1: Scale From Zero to Millions of Users](#chapter-1)
2. [Chapter 2: Back-of-the-Envelope Estimation](#chapter-2)
3. [Chapter 3: A Framework for System Design Interviews](#chapter-3)
4. [Master Cheat Sheet](#cheat-sheet)

---

## Chapter 1: Scale From Zero to Millions of Users

### The Scaling Journey

Xu presents scaling as an **iterative journey** — you don't start with a distributed system. You start with one server and add complexity only when needed.

```
SCALING MATURITY MODEL (Xu's Progression):

Level 1: Single Server
  Everything on one machine: web app, database, cache.
  Serves: ~1,000 users

Level 2: Web + Database Separation
  Split app server from database server.
  Scale each independently.
  Serves: ~10,000 users

Level 3: Load Balancer + Database Replication
  Add LB for failover. Master-slave DB replication.
  Serves: ~100,000 users

Level 4: Cache + CDN
  Cache DB results in Redis/Memcached.
  Serve static assets via CDN.
  Serves: ~500,000 users

Level 5: Stateless Web Tier + Multi-Datacenter
  Move session data to shared store (NoSQL).
  GeoDNS routes to nearest data center.
  Auto-scaling based on traffic.
  Serves: ~1,000,000 users

Level 6: Message Queue + Sharding + Microservices
  Decouple with async message queues (Kafka/RabbitMQ).
  Shard the database horizontally.
  Split into microservices.
  Serves: 10,000,000+ users
```

### Key Concept: Load Balancer

```
┌─────────┐          ┌──────────────┐         ┌──────────┐
│  Users  │─────────>│ Load Balancer│────────>│ Server 1 │
└─────────┘          │  (Public IP) │         └──────────┘
                     │              │         ┌──────────┐
                     │              │────────>│ Server 2 │
                     │              │         └──────────┘
                     └──────────────┘
                     Servers use PRIVATE IPs
                     (not reachable from internet)
```

**What it solves:**
1. **Failover:** If Server 1 dies, all traffic goes to Server 2
2. **Load distribution:** Traffic spread evenly across servers
3. **Horizontal scaling:** Add servers without downtime

**Key interview point:** Users connect to the LB's public IP. Servers communicate via private IPs. This adds security (servers aren't directly reachable from the internet).

### Key Concept: Database Replication (Master-Slave)

```
                    WRITES
                      │
                      ▼
              ┌──────────────┐
              │ Master DB    │  (only writes/updates/deletes)
              │              │
              └──────┬───────┘
                     │ replicates
           ┌─────────┼─────────┐
           ▼         ▼         ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │ Slave 1  │ │ Slave 2  │ │ Slave 3  │
     │ (reads)  │ │ (reads)  │ │ (reads)  │
     └──────────┘ └──────────┘ └──────────┘
           ▲
           │ READS
```

**Why master-slave?**
- Most applications are read-heavy (read:write ratio is often 10:1 or higher)
- Distributing reads across multiple slaves improves query throughput
- If master fails → promote a slave to master
- If slave fails → redirect reads to master or another slave

**Interview gotcha:** When promoting a slave to master, the slave might not have all the latest data (replication lag). Recovery scripts are needed to fill the gap.

### Key Concept: Cache

```
Read-Through Cache Flow:

  Request → Check Cache → HIT? → Return cached data
                 │
                 └─ MISS → Query Database → Store in Cache → Return
```

**Cache considerations (memorize these for interviews):**

| Consideration | Recommendation |
|--------------|----------------|
| When to cache | Read frequently, modify infrequently |
| Expiration policy | Not too short (causes reload storms), not too long (stale data) |
| Consistency | Cache + DB in sync — hard across multiple regions |
| Failure mitigation | Multiple cache servers (avoid SPOF), over-provision memory |
| Eviction policy | LRU (Least Recently Used) is most popular. LFU and FIFO also used |

### Key Concept: CDN (Content Delivery Network)

```
CDN Workflow:

User (Europe) ──> CDN Edge (Europe) ──> Cache HIT → Return image
                         │
                         └─ Cache MISS → Origin Server (US) → Fetch → Cache → Return
```

**CDN considerations:**
- **Cost:** You pay for data transfer in/out of CDN. Don't cache infrequently used assets.
- **Cache expiry:** Too long = stale content. Too short = repeated origin fetches.
- **CDN fallback:** If CDN goes down, clients should fallback to origin server directly.
- **Invalidation:** Use API-based invalidation or object versioning (`image.png?v=2`).

### Key Concept: Stateless Web Tier

```
STATEFUL (BAD for scaling):

  User A ──> Server 1 (has User A's session)
  User B ──> Server 2 (has User B's session)
  → Must use sticky sessions. Can't freely add/remove servers.

STATELESS (GOOD for scaling):

  User A ──> LB ──> Any Server ──> Shared Store (Redis/NoSQL)
                          │                 ↑
                          └─ reads/writes session data here
  → Any server can handle any user. Auto-scaling works.
```

**This is THE key concept for horizontal scaling.** If your web servers store session state locally, you can't scale horizontally. Move state to a shared store.

### Key Concept: Database Sharding

```
Sharding = splitting a large database into smaller pieces (shards)

  user_id % 4 → determines which shard holds the data

  Shard 0: user_id = 0, 4, 8, 12, ...
  Shard 1: user_id = 1, 5, 9, 13, ...
  Shard 2: user_id = 2, 6, 10, 14, ...
  Shard 3: user_id = 3, 7, 11, 15, ...
```

**Sharding challenges (Xu highlights these as critical):**

1. **Resharding:** When a shard gets too big or unevenly loaded, you need to re-distribute data. Consistent hashing (Chapter 5) helps minimize data movement.

2. **Celebrity/hotspot problem:** If Justin Bieber's data is on Shard 2, that shard gets hammered with read traffic. Solution: allocate a dedicated shard for high-traffic users.

3. **Join operations:** Once sharded, cross-shard JOINs are expensive/impossible. Solution: denormalize data (store redundant copies to avoid joins).

### Xu's Final Scaling Checklist

```
□ Keep web tier stateless
□ Build redundancy at every tier
□ Cache data as much as you can
□ Support multiple data centers
□ Host static assets in CDN
□ Scale your data tier by sharding
□ Split tiers into individual services (microservices)
□ Monitor your system and use automation tools
```

---

## Chapter 2: Back-of-the-Envelope Estimation

### Power of Two — Data Volume Units

```
┌──────────────────────┬──────────────┬─────────────────────┐
│ Unit                 │ Exact Value  │ Approximate         │
├──────────────────────┼──────────────┼─────────────────────┤
│ 1 Kilobyte (KB)      │ 2^10         │ 1,024 bytes         │
│ 1 Megabyte (MB)      │ 2^20         │ 1,024 KB (~1M)      │
│ 1 Gigabyte (GB)      │ 2^30         │ 1,024 MB (~1B)      │
│ 1 Terabyte (TB)      │ 2^40         │ 1,024 GB (~1K GB)   │
│ 1 Petabyte (PB)      │ 2^50         │ 1,024 TB            │
│ 1 Exabyte (EB)       │ 2^60         │ 1,024 PB            │
└──────────────────────┴──────────────┴─────────────────────┘
```

### Latency Numbers Every Programmer Should Know

```
┌────────────────────────────────────────────┬──────────────┐
│ Operation                                 │ Time         │
├────────────────────────────────────────────┼──────────────┤
│ L1 cache reference                        │ 0.5 ns       │
│ Branch mispredict                         │ 5 ns         │
│ L2 cache reference                        │ 7 ns         │
│ Mutex lock/unlock                         │ 25 ns        │
│ Main memory reference                     │ 100 ns       │
│ Compress 1KB with Zippy                   │ 3,000 ns     │
│ Send 1KB over 1 Gbps network              │ 10,000 ns    │
│ Read 4KB randomly from SSD                │ 150,000 ns   │
│ Read 1MB sequentially from memory         │ 250,000 ns   │
│ Round trip within data center             │ 500,000 ns   │
│ Read 1MB sequentially from SSD            │ 1,000,000 ns │
│ Disk seek                                 │ 10,000,000 ns│
│ Read 1MB sequentially from disk           │ 30,000,000 ns│
│ Send packet CA→Netherlands→CA             │ 150,000,000 ns│
└────────────────────────────────────────────┴──────────────┘

CONVERTED TO HUMAN-READABLE:
┌────────────────────────────────────────┬──────────┐
│ L1 cache                               │ 0.5 ns   │
│ L2 cache                               │ 7 ns     │
│ Main memory (RAM)                      │ 100 ns   │
│ SSD random read (4KB)                  │ 150 µs   │
│ Intra-datacenter round trip            │ 500 µs   │
│ SSD sequential read (1MB)              │ 1 ms     │
│ Disk seek                               │ 10 ms    │
│ Disk sequential read (1MB)             │ 30 ms    │
│ Cross-region (CA→Netherlands→CA)       │ 150 ms   │
└────────────────────────────────────────┴──────────┘

KEY INSIGHTS:
  • Memory is 100,000× faster than disk seek
  • SSD is ~70× faster than disk for random reads
  • Compress data before sending over network
  • Data center round trip: 500µs (keep calls within DC when possible)
```

### Availability Numbers

```
┌──────────────┬─────────────────────────────┐
│ Availability │ Allowable downtime per year │
├──────────────┼─────────────────────────────┤
│ 99%          │ 3.65 days                   │
│ 99.9%        │ 8.77 hours                  │
│ 99.99%       │ 52.60 minutes               │
│ 99.999%      │ 5.26 minutes                │
│ 99.9999%     │ 31.56 seconds               │
└──────────────┴─────────────────────────────┘

RULE: Each additional "9" costs ~10× more to achieve.
Going from 99.9% to 99.99% requires redundant everything.
```

### Example: Twitter Estimation

```
ASSUMPTIONS:
  • 300 million MAU (Monthly Active Users)
  • 50% use daily
  • 2 tweets per day per user
  • 10% of tweets contain media
  • Data stored for 5 years

QPS ESTIMATION:
  DAU = 300M × 50% = 150M
  Tweets QPS = 150M × 2 / 24 / 3600 = ~3,500
  Peak QPS = 2 × QPS = ~7,000

STORAGE ESTIMATION:
  Average tweet: tweet_id (64 bytes) + text (140 bytes) + media (1 MB)
  Media storage per day: 150M × 2 × 10% × 1 MB = 30 TB/day
  5-year storage: 30 TB × 365 × 5 = ~55 PB
```

### Xu's Estimation Tips

1. **Round and approximate:** Don't do `99,987 / 9.1`. Do `100,000 / 10`.
2. **Write down assumptions:** Referenced later in the design.
3. **Label units:** Write "5 MB", not just "5".
4. **Common estimation asks:** QPS, peak QPS, storage, cache, server count.

---

## Chapter 3: A Framework for System Design Interviews

### The 4-Step Process

```
┌──────────────────────────────────────────────────────────┐
│              XU'S 4-STEP SYSTEM DESIGN FRAMEWORK          │
│                                                          │
│  Step 1: UNDERSTAND THE PROBLEM (3-5 min)               │
│    • Ask clarifying questions                            │
│    • Don't jump to solutions                             │
│    • Define scope and requirements                       │
│                                                          │
│  Step 2: PROPOSE HIGH-LEVEL DESIGN (10-15 min)           │
│    • Draw initial blueprint (boxes + arrows)             │
│    • Get buy-in from interviewer                         │
│    • Back-of-envelope estimation                         │
│    • Walk through use cases                              │
│                                                          │
│  Step 3: DESIGN DEEP DIVE (10-25 min)                    │
│    • Identify and prioritize components                  │
│    • Focus on bottlenecks and interesting parts          │
│    • Design APIs and database schema                     │
│    • DON'T get lost in unnecessary details              │
│                                                          │
│  Step 4: WRAP UP (3-5 min)                               │
│    • Identify bottlenecks and single points of failure   │
│    • Discuss tradeoffs                                   │
│    • How to monitor and maintain                         │
│    • Future improvements and refinements                 │
│                                                          │
│  TOTAL: 45-50 minutes                                    │
└──────────────────────────────────────────────────────────┘
```

### Step 1: Questions to Ask

```
FUNCTIONAL REQUIREMENTS:
  • What specific features are we building?
  • Is this a mobile app, web app, or both?
  • What are the core use cases?
  • What is the expected read:write ratio?

NON-FUNCTIONAL REQUIREMENTS:
  • How many users does the product have?
  • How fast is the company scaling? (3 months, 6 months, 1 year)
  • What is the technology stack?
  • What existing services can we leverage?
  • What is the latency requirement?
  • What is the consistency requirement (strong vs eventual)?
```

### Red Flags Xu Warns About

```
🚫 OVER-ENGINEERING
   "The disease of many engineers — delighting in design purity
    and ignoring tradeoffs."

🚫 JUMPING TO SOLUTIONS
   "Answering without thorough understanding is a huge red flag."

🚫 GETTING LOST IN DETAILS
   "Talking about EdgeRank algorithm in detail takes precious time
    and does not prove your ability."

🚫 IGNORING TRADEOFFS
   Every design decision has pros and cons. Never present a design
   without saying "The tradeoff is..."
```

### What Interviewers Look For

```
✅ Ability to collaborate (treat interviewer as teammate)
✅ Working under pressure (don't freeze on hard questions)
✅ Resolving ambiguity constructively
✅ Asking good questions (the #1 signal of a senior engineer)
✅ Defending design choices with tradeoffs
✅ Communication clarity (think out loud)
```

---

## Cheat Sheet: Xu's Scaling Concepts At a Glance

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SCALING TOOLBOX                                   │
│                                                                     │
│  PROBLEM                    → SOLUTION                               │
│  ─────────                  → ────────                               │
│  Single server SPOF         → Load balancer + multiple servers      │
│  DB read bottleneck         → Master-slave replication              │
│  Slow DB queries            → Cache (Redis/Memcached)               │
│  Slow static asset delivery → CDN                                    │
│  Stateful web tier          → Move sessions to shared store         │
│  Geographic latency         → Multi-datacenter with GeoDNS          │
│  Tight coupling             → Message queue (async decoupling)      │
│  Large database             → Sharding (horizontal scaling)          │
│  Complex monolith           → Microservices                          │
│  Manual operations          → CI/CD, monitoring, automation          │
│                                                                     │
│  MEMORIZE: Statelessness + Caching + Replication + Sharding         │
│           These four unlock horizontal scaling.                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Interview Questions for Chapters 1-3

### Q1: "Walk me through how you'd scale a system from 1 to 1 million users."

```
"I'd follow an iterative approach:

Stage 1 (1K users): Single server — web app + database on one machine.

Stage 2 (10K users): Separate web server from database. This lets me scale
each independently and isolates DB load.

Stage 3 (100K users): Add a load balancer with multiple web servers behind
it for failover. Set up master-slave DB replication — reads go to slaves,
writes go to master.

Stage 4 (500K users): Add a cache layer (Redis) for frequently-read data.
Move static assets (images, CSS, JS) to a CDN.

Stage 5 (1M users): Make the web tier stateless by moving session data to
a shared store (Redis/NoSQL). This enables auto-scaling. Set up multi-DC
with GeoDNS for geographic latency reduction.

At every stage, I'd add monitoring, logging, and CI/CD automation."
```

### Q2: "What's the difference between vertical and horizontal scaling?"

```
"Vertical scaling (scale UP) means adding more CPU/RAM to a single server.
It's simple but has a hard hardware limit and creates a single point of
failure.

Horizontal scaling (scale OUT) means adding more servers. It's the
preferred approach for large-scale systems because there's no theoretical
limit — you can always add another server. However, it requires stateless
web tiers, load balancers, and distributed data stores.

In practice, both are used: you scale vertically until it's cost-effective,
then scale horizontally."
```

### Q3: "Why is stateless important for scaling?"

```
"Statelessness means no server stores client-specific data between requests.
Any server can handle any request from any user. This is critical because:

1. Auto-scaling works: You can add/remove servers freely without worrying
   about which user's data is on which server.
2. No sticky sessions needed: Load balancer can route to ANY server.
3. Failover is seamless: If a server dies, any other server takes over.

To achieve statelessness, you move session data to a shared store (Redis,
NoSQL, or a relational database). The web servers become pure compute —
they read state from the shared store, process the request, and write
updated state back."
```

### Q4: "How do you decide between SQL and NoSQL?"

```
"Default to SQL (PostgreSQL/MySQL) for most applications. It's mature,
ACID-compliant, and well understood.

Consider NoSQL when:
  • You need super-low latency on reads
  • Data is unstructured or schema is rapidly changing
  • You only need JSON serialization (no complex joins)
  • You need to store massive data volume (PB-scale)

The decision often comes down to whether you need JOINs and transactions
(SQL) vs raw key-value speed (NoSQL). In practice, many systems use both:
SQL for transactional data (users, orders) and NoSQL for high-volume
data (logs, sessions, analytics)."
```

### Q5: "Estimate the storage requirements for a photo-sharing app with 1M DAU."

```
"Assumptions:
  • 1M Daily Active Users
  • Each user uploads 2 photos per day
  • Average photo size: 1 MB (compressed JPEG)
  • Photos stored for 5 years
  • Thumbnails also stored: 0.1 MB each (2 thumbnails per photo)

Calculations:
  Daily uploads: 1M × 2 = 2M photos/day
  Daily storage: 2M × (1 MB + 2 × 0.1 MB) = 2M × 1.2 MB = 2.4 TB/day
  5-year storage: 2.4 TB × 365 × 5 = 4,380 TB ≈ 4.4 PB

With replication factor of 3 (for durability): 4.4 × 3 = 13.2 PB

CDN storage (for frequently-accessed photos): ~20% of total = ~1 PB"
```

### Q6: "What's the most important thing to do in a system design interview?"

```
"The #1 thing is to ask clarifying questions before designing. Xu explicitly
warns against 'Jimmy' — the student who answers too quickly. Jumping into
a solution without understanding requirements shows immaturity.

Good questions to ask:
  • What features are we building?
  • How many users? What's the scale?
  • What's the read:write ratio?
  • What's the consistency requirement?
  • What existing infrastructure can we leverage?

The interview simulates real-life collaboration. Engineers who ask the right
questions before designing are the ones who build the right system."
```

---

> **Next:** Chapter 4 covers Rate Limiters, Token Buckets, and distributed rate limiting.
> See `04-alex-xu-vol1-distributed-systems.md` for chapters 4-8.
