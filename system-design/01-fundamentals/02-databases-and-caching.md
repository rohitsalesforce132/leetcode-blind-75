# Databases & Caching: The Engine Room of Every System

> **The goal of this guide:** Understand relational vs NoSQL databases, ACID
> properties, indexes, sharding, replication, caching strategies, and the CAP
> theorem — enough to design a database layer confidently in any interview.

---

## Table of Contents

1. [Relational (SQL) vs NoSQL](#1-relational-sql-vs-nosql)
2. [ACID Properties](#2-acid-properties)
3. [Indexes: Making Queries Fast](#3-indexes-making-queries-fast)
4. [Partitioning & Sharding](#4-partitioning--sharding)
5. [Replication: Read Replicas & Write Master](#5-replication-read-replicas--write-master)
6. [Caching Fundamentals](#6-caching-fundamentals)
7. [Cache Patterns: Cache-Aside, Write-Through](#7-cache-patterns-cache-aside-write-through)
8. [Cache Eviction Policies](#8-cache-eviction-policies)
9. [The CAP Theorem](#9-the-cap-theorem)
10. [Interview Q&A](#10-interview-qa)

---

## 1. Relational (SQL) vs NoSQL

### Real-World Analogy: Filing Cabinet vs Spreadsheets 🗄️📊

- **Relational (SQL):** Like a **filing cabinet** with strict rules. Every document
  has a defined folder, tab, and position. You can't put a document in the wrong
  place. Structured, predictable, but rigid.
- **NoSQL:** Like a **spreadsheet where anyone can add any column**. Flexible,
  ad-hoc, great for messy evolving data — but less predictable.

### Relational Databases (SQL)

Data is stored in **tables** with rows and columns. Tables have **relationships**
(foreign keys). You query with SQL.

```
   ┌─────────── USERS TABLE ───────────┐
   │ id │ name    │ email          │ age│
   │────┼─────────┼────────────────┼────│
   │ 1  │ Alice   │ alice@mail.com │ 30 │
   │ 2  │ Bob     │ bob@mail.com   │ 25 │
   └────┴─────────┴────────────────┴────┘
            │
            │ foreign key
            ▼
   ┌─────────── ORDERS TABLE ──────────┐
   │ id │ user_id │ product  │ amount  │
   │────┼─────────┼──────────┼─────────│
   │ 101│ 1       │ Laptop   │ $999    │
   │ 102│ 1       │ Mouse    │ $25     │
   │ 103│ 2       │ Keyboard │ $75     │
   └────┴─────────┴──────────┴─────────┘
```

**Examples:** PostgreSQL, MySQL, Oracle, SQL Server, SQLite

### NoSQL Databases

NoSQL comes in several flavors:

| Type         | Description                          | Examples               | Analogy                    |
|--------------|--------------------------------------|------------------------|----------------------------|
| **Key-Value**| Just a key → value lookup            | Redis, DynamoDB, Riak  | Dictionary / phone book    |
| **Document** | Flexible JSON-like documents         | MongoDB, CouchDB       | Binder of loose papers     |
| **Column-Family** | Data grouped by column families | Cassandra, HBase       | Ledgers grouped by topic   |
| **Graph**    | Nodes and edges (relationships)      | Neo4j, ArangoDB        | Social network map         |

```
   DOCUMENT STORE (MongoDB):

   ┌─────────────────────── USER DOCUMENT ───────────────────────┐
   │ {                                                            │
   │   "_id": "abc123",                                           │
   │   "name": "Alice",                                           │
   │   "email": "alice@mail.com",                                 │
   │   "orders": [           ← nested data, no separate table!   │
   │     { "product": "Laptop", "amount": 999 },                  │
   │     { "product": "Mouse", "amount": 25 }                     │
   │   ]                                                          │
   │ }                                                            │
   └──────────────────────────────────────────────────────────────┘
```

### When to Use Which?

| Use SQL when...                           | Use NoSQL when...                        |
|-------------------------------------------|------------------------------------------|
| Data has a **rigid, known structure**     | Data is **unstructured or evolving**     |
| You need **ACID transactions**            | You need **massive horizontal scaling**  |
| Relationships are central (joins)         | Schema changes frequently                |
| Financial systems, ERP, inventory         | Content, IoT, real-time analytics, logs  |

---

## 2. ACID Properties

### Real-World Analogy: Bank Transfer 🏦

You transfer $100 from Alice to Bob. This involves **two steps**: deduct from Alice,
add to Bob. What if the system crashes between the two steps? Alice lost $100, Bob
got nothing. **Disaster.** ACID prevents this.

```
   STEP 1: Deduct $100 from Alice   ✅
   ─── CRASH! 💥 ───
   STEP 2: Add $100 to Bob          ❌ (never happened)

   Result: $100 vanished into thin air! 💸
```

### The Four ACID Properties

| Property         | Meaning                                                | Analogy                          |
|------------------|--------------------------------------------------------|----------------------------------|
| **A**tomicity    | All operations succeed or **all fail** — no partial state | Bank transfer: both or neither   |
| **C**onsistency  | Database always moves from one valid state to another  | Can't overdraw below $0          |
| **I**solation    | Concurrent transactions don't interfere with each other| Two tellers don't double-spend   |
| **D**urability   | Once committed, data survives crashes/power loss       | Written in permanent ink         |

### Atomicity in Action

```
   TRANSACTION: Transfer $100 from Alice to Bob

   BEGIN TRANSACTION;
     UPDATE accounts SET balance = balance - 100 WHERE name = 'Alice';
     UPDATE accounts SET balance = balance + 100 WHERE name = 'Bob';
   COMMIT;

   If either UPDATE fails ──> ROLLBACK (undo everything)
   If both succeed ────────> COMMIT (make it permanent)
```

> ⚠️ NoSQL databases often sacrifice ACID for **scalability and performance**. You
> get "eventual consistency" instead. This is a core tradeoff.

---

## 3. Indexes: Making Queries Fast

### Real-World Analogy: Library Book Catalog 📚

Imagine finding a book in a library **without a catalog**. You'd walk aisle by aisle,
reading every spine — incredibly slow (a **full table scan**).

Now imagine the library has an **alphabetical card catalog** by title. You look up
the title, see it says "Shelf 4, Row 2," and go straight there. That's an **index**.

### Without vs With an Index

```
   WITHOUT INDEX (Full Table Scan):
   Query: SELECT * FROM users WHERE email = 'bob@mail.com';

   Scan every row ───> row 1 (Alice) ❌ ───> row 2 (Bob) ✅
   Time: O(n) — slow for millions of rows

   WITH INDEX on email:
   Query: SELECT * FROM users WHERE email = 'bob@mail.com';

   Index lookup ───> "bob@mail.com" → row #2 ───> jump directly!
   Time: O(log n) — fast even for billions of rows
```

### How an Index Works (B-Tree)

```
   B-TREE INDEX on "email":

                    [kate@]                    ← root node
                   /        \
          [alice@, bob@]   [mary@, zoe@]       ← internal nodes
           /      |    \      /    |     \
       (leaf: row 1)(row 2) ... (row 5)(row N)  ← leaf nodes → actual data
   ```

   Each level narrows the search. To find "bob@", you go left at the root, find
   the middle leaf, done. No need to scan everything.

### Tradeoffs of Indexes

| Pros ✅                              | Cons ❌                                    |
|--------------------------------------|--------------------------------------------|
| Reads are dramatically faster        | **Slower writes** (index must be updated)  |
| Essential for large tables           | Consumes extra **storage space**           |
| Enables fast sorting (ORDER BY)      | Too many indexes = write performance drops |

> 💡 **Rule of thumb:** Index columns used frequently in WHERE, JOIN, and ORDER BY
> clauses. Don't index every column — each index slows down writes.

---

## 4. Partitioning & Sharding

### Real-World Analogy: Big Library, Too Many Books 📚📚📚

When a single library building can't hold all the books, you split the collection
across **multiple branches**. Each branch holds a portion. Readers go to the right
branch based on what they need.

### What Is Sharding?

**Sharding** is horizontal partitioning: splitting a large table's rows across
**multiple database servers**. Each server (shard) holds a subset of the data.

```
   ONE BIG DATABASE (becoming too large):
   ┌──────────────────────────────────────┐
   │          USERS TABLE (1 billion rows)│
   │  Can't fit on one machine!           │
   └──────────────────────────────────────┘

   SHARD BY USER ID (range-based):
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │  Shard 1     │  │  Shard 2     │  │  Shard 3     │
   │  ID: 1–333M  │  │  ID: 334M–666M│  │  ID: 667M–1B │
   │  🖥️          │  │  🖥️          │  │  🖥️          │
   └──────────────┘  └──────────────┘  └──────────────┘
```

### Sharding Strategies

| Strategy            | How rows are assigned                           | Good for                 |
|---------------------|-------------------------------------------------|--------------------------|
| **Range-based**     | Shard 1: IDs 1–1000, Shard 2: 1001–2000         | Time-series, sequential IDs |
| **Hash-based**      | `hash(id) % num_shards` → even distribution      | General purpose          |
| **Geographic**      | US users → US shard, EU users → EU shard         | Geo-locality             |
| **Directory-based** | A lookup service maps each key to its shard      | Flexibility              |

### The Challenges of Sharding

- **Cross-shard queries** are hard (e.g., "find all users globally")
- **Joins across shards** are expensive or impossible
- **Rebalancing** when a shard gets too big is painful
- **Hot shards** — if one shard gets disproportionate traffic (e.g., Justin Bieber's
  shard in a Twitter-like system)

```
   HOT SHARD PROBLEM:
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Shard 1  │  │ Shard 2  │  │ Shard 3  │
   │ Normal   │  │ 🔥 HOT!  │  │ Normal   │
   │ traffic  │  │ Celebrity│  │ traffic  │
   └──────────┘  └──────────┘  └──────────┘
                  ↑ overloaded while others are idle
```

---

## 5. Replication: Read Replicas & Write Master

### Real-World Analogy: Blueprints in a Library 🏛️

A library has one **original manuscript** (the master). They make **copies** for
other branches (replicas). Anyone can read a copy, but only the curator can modify
the original.

### Master-Replica Architecture

In most production systems, reads vastly outnumber writes. We optimize for this:

```
                    ┌─────────────────────┐
   WRITE requests ─>│   PRIMARY (MASTER)  │
   (INSERT, UPDATE) │   Handles ALL writes│
                    └──────────┬──────────┘
                               │ replicates changes
                    ┌──────────▼──────────┐
                    │   Replica 1         │
   READ requests ─> │   (read-only copy)  │
                    └─────────────────────┘
                    ┌─────────────────────┐
   READ requests ─> │   Replica 2         │
                    │   (read-only copy)  │
                    └─────────────────────┘
```

### Why This Helps

- **Read scaling:** Spread reads across many replicas
- **Reliability:** If master dies, a replica can be promoted
- **Geographic locality:** Place replicas near users in different regions
- **Analytics:** Run heavy queries on a replica, not the master

### Synchronous vs Asynchronous Replication

```
   SYNCHRONOUS (strong consistency):
   Master writes ──> waits for ALL replicas to confirm ──> commit
   ✅ Always consistent     ❌ Slow (slowest replica determines speed)

   ASYNCHRONOUS (eventual consistency):
   Master writes ──> commits immediately ──> replicas catch up later
   ✅ Fast                   ❌ Replicas may lag (stale reads)
```

> Most systems use **async replication** for performance. Accept that replicas may
> lag by milliseconds to seconds.

---

## 5b. Databases Summary Table

| Database     | Type      | Best For                          | ACID?    | Scale   |
|--------------|-----------|-----------------------------------|----------|---------|
| PostgreSQL   | SQL       | Complex queries, transactions     | ✅ Full  | Vertical|
| MySQL        | SQL       | General-purpose web apps          | ✅ Full  | Vertical|
| MongoDB      | Document  | Flexible schemas                  | Partial  | Horizontal|
| Cassandra    | Column    | Massive write throughput          | ❌       | Horizontal|
| Redis        | Key-Value | Caching, real-time leaderboards   | ❌       | Horizontal|
| Neo4j        | Graph     | Social networks, recommendations  | ✅ Full  | Vertical|

---

## 6. Caching Fundamentals

### Real-World Analogy: Your Desk vs the Filing Cabinet 🖥️

Your **desk** (cache) holds the few documents you use daily. The **filing cabinet**
(database) has everything but takes longer to access. You check the desk first — if
the document is there, great (fast). If not, go to the cabinet (slow) and put a copy
on your desk for next time.

### Why Cache?

Databases are **slow** (milliseconds). Memory (RAM) is **fast** (microseconds). A
cache stores frequently accessed data in RAM so you don't hit the DB every time.

```
   WITHOUT CACHE:
   Request ──> Database (10ms per query) ──> Response
   1000 req/s × 10ms = DB is overwhelmed

   WITH CACHE:
   Request ──> Cache? ──(HIT, 0.1ms)──> Response      ← 95% of requests
                    └──(MISS)──> Database (10ms) ──> cache it ──> Response
   Only 5% hit the DB. DB is happy. Users are happy.
```

### Cache Hit vs Cache Miss

```
   CACHE HIT:  Data IS in cache     ──> serve instantly (fast)
   CACHE MISS: Data NOT in cache    ──> fetch from DB, store in cache (slow once)
   CACHE HIT RATIO = Hits / (Hits + Misses)
   Target: 90%+ hit ratio for good performance
```

### Popular Caching Tools

| Tool       | Type      | Strengths                              |
|------------|-----------|----------------------------------------|
| **Redis**  | Key-Value | Rich data structures, persistence, pub/sub|
| **Memcached** | Key-Value | Dead simple, very fast, distributed   |

---

## 7. Cache Patterns: Cache-Aside, Write-Through

### Cache-Aside (Lazy Loading)

The application **manages the cache**. It checks the cache first, and only fetches
from the DB on a miss.

```
   1. App receives request for user_id=42
   2. App checks cache: cache.get("user:42")
      ├── HIT  ──> return cached data ✅
      └── MISS ──> query DB, then cache.set("user:42", data), return data
```

**Pros:** Only caches what's actually requested. DB isn't flooded on startup.
**Cons:** Data can become **stale** (DB changed but cache still has old value).

### Write-Through

Every write goes to **both** the cache and the database simultaneously.

```
   1. App writes data
   2. cache.set("user:42", data)  ← update cache
   3. db.update(user_42, data)    ← update database
   4. Cache and DB are always in sync ✅
```

**Pros:** Cache is always fresh — no stale reads.
**Cons:** Writes are slower (two writes instead of one). Data that's rarely read
still gets cached (wasted space).

### Write-Behind (Write-Back)

Writes go to the cache **first**, then asynchronously to the DB after a delay.

```
   1. App writes ──> cache.set()  (instant, fast)
   2. ... time passes ...
   3. Cache flushes ──> db.update()  (async, batched)
```

**Pros:** Extremely fast writes.
**Cons:** If cache crashes before flushing, data is lost. Risky.

### Cache Invalidation: The Hardest Problem

```
   "There are only two hard things in Computer Science:
    cache invalidation and naming things." — Phil Karlton
```

Strategies:
- **TTL (Time-To-Live):** Cache entry expires after N seconds. Simple.
- **Event-driven:** When DB updates, explicitly delete/update the cache entry.
- **Versioned:** Include a version number; old versions are invalid.

---

## 8. Cache Eviction Policies

### Real-World Analogy: A Full Desk 🪑

Your desk only holds 10 documents. When you need to add an 11th, you must **remove**
one. Which one? Your **eviction policy** decides.

```
   CACHE IS FULL — what do we evict?

   ┌────┬────┬────┬────┬────┐
   │ A  │ B  │ C  │ D  │ E  │   ← 5 slots, all occupied
   └────┴────┴────┴────┴────┘
   Need to add F? Must evict one of A–E.
```

### Common Eviction Policies

| Policy       | What it evicts                                 | Analogy                          |
|--------------|------------------------------------------------|----------------------------------|
| **LRU**      | Least Recently Used item                       | Throw out the doc you haven't touched in weeks |
| **LFU**      | Least Frequently Used item                     | Throw out the doc you rarely read|
| **FIFO**     | First-In, First-Out (oldest by insertion)      | Throw out the oldest doc         |
| **Random**   | Random item                                     | Flip a coin                      |

### LRU (Least Recently Used) — The Most Common

```
   LRU QUEUE (most recent ──> least recent):

   Time 0: [A]                       Add A
   Time 1: [A, B]                    Add B
   Time 2: [A, B, C]                 Add C (cache full: 3 slots)
   Time 3: [B, C, A*]                Access A → A moves to front (recently used)
   Time 4: [C, A, D]                 Add D → evict B (least recently used)

   B was evicted because it was accessed longest ago.
```

> 💡 Redis uses an approximation of LRU. Memcached uses a lazy LRU.

---

## 9. The CAP Theorem

### Real-World Analogy: A Chain with Three Branches 🏦

A bank has three branches connected by phone lines. If the phone line between two
branches goes down, they face a choice:
- Keep serving customers at both branches (but they might disagree on balances) —
  **Availability**
- Stop serving to avoid inconsistency — **Consistency**

You **cannot have both** when the network fails. That's CAP.

### The Three Properties

| Property          | Meaning                                           |
|-------------------|---------------------------------------------------|
| **C**onsistency   | Every read returns the latest write or an error   |
| **A**vailability  | Every request gets a response (not necessarily latest) |
| **P**artition Tolerance | The system continues despite network partitions |
```

You can guarantee at most **two of the three**:

```
                        ┌───────────────────────┐
                        │     CAP THEOREM       │
                        └───────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
       ┌──────▼──────┐       ┌──────▼──────┐       ┌──────▼──────┐
       │     CA      │       │     CP      │       │     AP      │
       │ (RDBMS)     │       │ (HBase,     │       │ (Cassandra, │
       │ Consistency │       │  MongoDB)   │       │  DynamoDB)  │
       │ + Avail.    │       │ Con. + Part.│       │ Avail+Part. │
       │ NO Partitions│       │ May block  │       │ May be stale│
       └─────────────┘       └─────────────┘       └─────────────┘
```

### What Each Choice Means

| Choice | Meaning                                            | Examples                |
|--------|----------------------------------------------------|-------------------------|
| **CP** | Reject requests if data can't be kept consistent  | HBase, MongoDB (default)|
| **AP** | Always respond, even if data might be stale        | Cassandra, DynamoDB     |
| **CA** | Single-node systems (no partition tolerance)       | Traditional RDBMS       |

> ⚠️ In distributed systems, **P is non-negotiable** — networks *will* fail. So the
> real choice is **CP vs AP**: do you block (CP) or serve stale data (AP) during a
> network partition?

---

## 10. Interview Q&A

### Q: SQL vs NoSQL — how do you choose?

Use **SQL** when data is structured and relationships matter, you need ACID
transactions, and complex queries/joins are common (banking, ERP, e-commerce
inventory). Use **NoSQL** when data is semi-structured or rapidly evolving, you need
massive horizontal scalability, or the access patterns are key-based lookups
(content management, IoT, real-time analytics, logs).

### Q: What does ACID stand for, and why does it matter?

**A**tomicity (all-or-nothing transactions), **C**onsistency (always valid state),
**I**solation (concurrent transactions don't interfere), **D**urability (committed
data survives crashes). ACID matters because without it, partial failures corrupt
data — e.g., a bank transfer that deducts but never credits.

### Q: Explain indexes. Why are they a tradeoff?

An index is a data structure (usually a B-Tree) that lets the database find rows
without scanning the entire table. They make **reads much faster** but **slow down
writes** (the index must be updated) and consume extra space. Index frequently
queried columns; avoid indexing everything.

### Q: What is sharding, and when would you use it?

Sharding splits a large table's rows across multiple database servers so no single
machine is overwhelmed. Use it when a single database can't handle the data volume
or write load. Challenges include cross-shard joins, hot shards, and rebalancing.

### Q: Explain the master-replica pattern.

One **primary/master** node handles all writes. **Replicas** are read-only copies
that receive updates from the master via replication. This scales reads, provides
redundancy (a replica can be promoted if the master dies), and enables geographic
locality. Most systems use **async replication**, so replicas may lag slightly.

### Q: What's the difference between cache-aside and write-through?

**Cache-aside** checks the cache first and only loads from the DB on a miss — simple,
but data can go stale. **Write-through** writes to both cache and DB simultaneously —
cache is always fresh, but writes are slower. Choose cache-aside for read-heavy
workloads; write-through when you can't tolerate stale reads.

### Q: What is the CAP theorem?

In a distributed system, you can guarantee at most two of: **Consistency** (all nodes
see the same data), **Availability** (every request gets a response), and **Partition
Tolerance** (system works despite network failures). Since networks can fail (P is
unavoidable), the real choice is **CP** (block during partitions to stay consistent)
vs **AP** (serve possibly stale data to stay available).

### Q: What is eventual consistency?

A consistency model where, if no new updates occur, all replicas **eventually**
converge to the same value. Reads may return stale data temporarily, but the system
becomes consistent over time. Common in AP systems like Cassandra and DynamoDB.

### Q: How do you handle cache invalidation?

Strategies include **TTL** (entries expire after a set time), **event-driven
invalidation** (explicitly delete the cache entry when the underlying data changes),
and **versioning**. Cache invalidation is notoriously hard because of race conditions
between cache and database updates.

### Q: Walk me through designing the database layer for a URL shortener.

1. Use a **relational DB** (PostgreSQL) with columns: short_code, original_url,
   created_at, user_id. (Structured data, simple queries.)
2. Add an **index on short_code** for fast lookups.
3. Add a **read replica** for high read volume (short link clicks are read-heavy).
4. **Shard** by short_code hash if the dataset grows beyond one machine.
5. Add a **Redis cache** for the hottest short links (cache-aside with TTL).
6. If global, use **geo-replicated** read replicas near users.

---

## Quick Reference Cheat Sheet

```
┌─────────────────────────┬───────────────────────────────────────────────┐
│ Concept                 │ One-liner                                     │
├─────────────────────────┼───────────────────────────────────────────────┤
│ SQL vs NoSQL            │ Structured+ACID vs flexible+scalable          │
│ ACID                    │ Atomicity, Consistency, Isolation, Durability│
│ Index                   │ B-Tree for fast lookups (faster reads)       │
│ Sharding                │ Split table rows across multiple DB servers  │
│ Master-Replica          │ 1 writer + N readers                         │
│ Cache-Aside             │ Check cache first, load DB on miss           │
│ Write-Through           │ Write to cache + DB simultaneously           │
│ LRU Eviction            │ Remove least recently used when full         │
│ CAP Theorem             │ Pick 2 of 3: Consistency, Availability, P    │
│ Eventual Consistency    │ Replicas converge over time (may be stale)   │
└─────────────────────────┴───────────────────────────────────────────────┘
```

---

**Previous:** [01 — Scaling Basics](01-scaling-basics.md)
**Next:** [03 — Microservices & APIs →](03-microservices-and-apis.md)
