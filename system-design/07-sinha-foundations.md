# Sinha — Foundations of System Design (Chapters 1-4)

> **Source:** "System Design Guide for Professionals" by Dhirendra Sinha (Packt, 2024)
> **Coverage:** Ch 1 (Basics), Ch 2 (Distributed Attributes), Ch 3 (Theorems & Data Structures), Ch 4 (DNS/LB/Gateways)
> **Why this matters:** This book goes FAR deeper than Alex Xu on consensus algorithms (Paxos, Raft, BFT, FLP), probabilistic data structures (Bloom filters, Count-min sketch, HyperLogLog), and distributed system attributes (PACELC theorem).

---

## TABLE OF CONTENTS

1. [Chapter 1: Basics of System Design](#chapter-1)
2. [Chapter 2: Distributed System Attributes](#chapter-2)
3. [Chapter 3: Theorems and Data Structures (THE DEEPEST CHAPTER)](#chapter-3)
4. [Chapter 4: DNS, Load Balancers, and Gateways](#chapter-4)
5. [Sinha vs Alex Xu Comparison](#comparison)

---

## Chapter 1: Basics of System Design

### What Sinha Adds Beyond Alex Xu

Alex Xu's Chapter 1 is "how to scale from 1 to millions." Sinha's Chapter 1 is **"what IS system design?"** — a more foundational, conceptual introduction.

### Types of System Design

```
┌──────────────────────────────────────────────────────────────┐
│              TWO TYPES OF SYSTEM DESIGN                       │
│                                                              │
│  HIGH-LEVEL DESIGN (HLD)          LOW-LEVEL DESIGN (LLD)     │
│  ──────────────────────           ──────────────────          │
│  • System architecture            • Algorithms                │
│  • Component decomposition        • Data structures           │
│  • Data flow                      • API contracts             │
│  • Scalability strategy           • Code optimization         │
│  • Fault tolerance plan           • Class diagrams            │
│  • Technology selection           • Sequence diagrams         │
│  • Deployment topology            • Error handling            │
│                                                              │
│  "What components do we need?"    "How does each component    │
│  "How do they connect?"            work internally?"          │
│                                                              │
│  Interview focus: HLD (45 min)    Interview focus: LLD        │
│  (most system design rounds)      (some companies do both)    │
└──────────────────────────────────────────────────────────────┘
```

### Sinha's Key Insight: System Design is About Tradeoffs

```
"Every design decision involves a tradeoff. There is no perfect design.
 There are only designs that are better for specific requirements."

Sinha emphasizes this more than Alex Xu. His framework:
  1. Understand the PROBLEM (requirements)
  2. Identify the CONSTRAINTS (scale, latency, budget, team size)
  3. Evaluate OPTIONS (at least 2-3 alternatives)
  4. Choose based on TRADEOFFS
  5. Document WHY you chose what you chose
```

---

## Chapter 2: Distributed System Attributes

### Sinha's 8 Attributes (vs Alex Xu's Implicit Treatment)

Alex Xu covers availability and scalability but doesn't formalize them. Sinha explicitly defines **8 core attributes** that every distributed system must balance:

```
┌──────────────────────────────────────────────────────────────────────┐
│              THE 8 ATTRIBUTES OF DISTRIBUTED SYSTEMS                  │
│                                                                      │
│  1. CONSISTENCY      2. AVAILABILITY     3. PARTITION TOLERANCE     │
│  4. LATENCY          5. DURABILITY       6. RELIABILITY             │
│  7. FAULT TOLERANCE  8. SCALABILITY                                  │
│                                                                      │
│  THE HARDEST PART: These attributes CONFLICT with each other.        │
│  You cannot maximize all 8 simultaneously.                           │
│                                                                      │
│  EXAMPLE CONFLICTS:                                                  │
│  • Consistency vs Latency (strong consistency = higher latency)     │
│  • Availability vs Consistency (can't have both during partition)   │
│  • Durability vs Latency (sync replication = slower writes)         │
│  • Scalability vs Consistency (more nodes = harder to agree)        │
└──────────────────────────────────────────────────────────────────────┘
```

### Consistency Models Explained

```
STRONG CONSISTENCY:
  After a write completes, ALL subsequent reads see the new value.
  Implementation: Synchronous replication (write to ALL replicas before ack)
  Latency: HIGH (must wait for all replicas)
  Use case: Financial transactions, inventory management

  Timeline:
  T0: Client writes X=5 → replicated to Node A, B, C → ACK
  T1: Client reads X → guaranteed to see 5 from ANY node

EVENTUAL CONSISTENCY:
  After a write completes, reads MAY see stale data temporarily.
  Implementation: Asynchronous replication (write to one, replicate later)
  Latency: LOW (ack immediately)
  Use case: Social media feeds, shopping carts, DNS

  Timeline:
  T0: Client writes X=5 → written to Node A → ACK immediately
  T1: Client reads X from Node B → sees OLD value (4) ← STALE!
  T2: Replication catches up → Node B now has 5
  T3: Client reads X from Node B → sees 5 ← CONSISTENT
```

### The Hotel Booking Example (Sinha's Signature Analogy)

```
Sinha uses a HOTEL BOOKING example throughout the chapter to illustrate
all 8 attributes:

CONSISTENCY: Two people can't book the same room simultaneously.
  → Requires strong consistency for booking.
  → Eventual consistency is fine for "viewing available rooms."

AVAILABILITY: The booking system must be up 24/7.
  → Redundant servers across data centers.

PARTITION TOLERANCE: If the network between data centers fails,
  the system must still work.

LATENCY: Booking must complete in <2 seconds.

DURABILITY: A confirmed booking must NEVER be lost, even if all
  servers crash simultaneously.

RELIABILITY: The system consistently performs correctly over time.

FAULT TOLERANCE: If one server crashes mid-booking, the transaction
  rolls back gracefully.

SCALABILITY: Handle 1000 bookings/sec during peak season (holidays).
```

---

## Chapter 3: Theorems and Data Structures (THE DEEPEST CHAPTER)

> **This is the chapter that makes Sinha's book unique.** Alex Xu doesn't cover Paxos, Raft, BFT, FLP, PACELC, Bloom filters, Count-min sketch, or HyperLogLog. Sinha goes deep on all of them.

### 3.1 CAP Theorem (Review + Deeper Treatment)

```
CAP: Consistency, Availability, Partition tolerance — pick 2.

Sinha adds NUANCE that Alex Xu doesn't:

"The CAP theorem doesn't imply an all-or-nothing sacrifice of properties
 in every situation. Instead, it highlights the inherent trade-offs that
 distributed systems face."

REALITY: Most systems are NOT purely CP or AP. They TUNE the tradeoff:

  DynamoDB: Tunable consistency per request
    • Strong read: reads from quorum → CP behavior
    • Eventual read: reads from one node → AP behavior

  Cassandra: Tunable consistency per query
    • ConsistencyLevel.ALL → CP (reads from all replicas)
    • ConsistencyLevel.ONE → AP (reads from nearest replica)

This "tunability" is a KEY interview signal of senior understanding.
```

### 3.2 PACELC Theorem (NOT in Alex Xu — Sinha Exclusive)

```
PACELC extends CAP by adding the "else" case:

  IF Partition (P): choose Availability (A) or Consistency (C)
  ELSE (E): choose Latency (L) or Consistency (C)

In other words:
  During a network partition → CAP applies (A vs C)
  During normal operation (no partition) → Latency vs Consistency

         ┌─────────────────────────────────────┐
         │         PACELC THEOREM               │
         │                                     │
         │    Partition?                       │
         │     ├── YES → A vs C (like CAP)    │
         │     └── NO  → L vs C               │
         │                                     │
         │    PA/EL: Prefer low latency        │
         │           (Cassandra, DynamoDB)     │
         │                                     │
         │    PC/EC: Prefer consistency        │
         │           (BigTable, HBase, Spanner)│
         │                                     │
         │    PA/EC: Prefer availability when │
         │           partitioned, consistency  │
         │           when not (MongoDB)        │
         └─────────────────────────────────────┘

INTERVIEW GOLD: "I think about consistency tradeoffs not just during
partitions but also during normal operations. PACELC captures this —
even without a partition, there's a latency-consistency tradeoff.
Cassandra is PA/EL: it prefers availability during partitions and low
latency otherwise. HBase is PC/EC: it prefers consistency always."
```

### 3.3 Paxos Algorithm (NOT in Alex Xu)

```
Paxos: Achieve consensus in a distributed system with crash failures.

SCENARIO: 5 nodes need to agree on a value (e.g., "the new leader is Node 3").
  Some nodes may crash. Network may delay messages.
  How do they reach agreement?

ROLES:
  Proposers: Suggest values ("I propose value X")
  Acceptors: Vote on proposals ("I accept/reject X")
  Learners:  Learn the agreed-upon value

TWO-PHASE PROTOCOL:

  Phase 1 — PREPARE:
    Proposer → "I want to propose with number N"
    → Sends to all acceptors
    Acceptors → "I promise not to accept any proposal < N"
    → If acceptor already accepted a higher proposal, tells proposer

  Phase 2 — ACCEPT:
    If proposer gets majority (quorum) of promises:
    Proposer → "Accept value X with number N"
    → Sends to all acceptors
    Acceptors → Accept (if they haven't promised a higher number)
    → If majority accept → VALUE IS CHOSEN

    Learners are notified: "The agreed value is X"

    ┌──────────┐  Prepare(N)   ┌──────────┐
    │Proposer  │──────────────>│Acceptor 1│
    │          │<──────────────│ Promise  │
    │          │  Prepare(N)   └──────────┘
    │          │──────────────>┌──────────┐
    │          │<──────────────│Acceptor 2│
    │          │  Promise      └──────────┘
    │          │               ┌──────────┐
    │          │  Accept(X,N) >│Acceptor 3│
    │          │<──────────────│ Accepted │
    └──────────┘               └──────────┘
                                    │
                              ┌─────▼────┐
                              │ Learners │ → Value X is chosen
                              └──────────┘

KEY INSIGHT: Paxos guarantees SAFETY (never choose wrong value)
but does NOT guarantee LIVENESS (might not terminate).

VARIANTS:
  • Multi-Paxos: Optimizes for continuous consensus (skip prepare phase)
  • Fast Paxos: Reduces message rounds
  • Simple Paxos: Combines prepare + accept into one round

USED BY: Google Spanner, Apache ZooKeeper, Microsoft Azure Cosmos DB
```

### 3.4 Raft Algorithm (NOT in Alex Xu)

```
Raft: Same problem as Paxos, but SIMPLER to understand.

"Raft was designed for understandability. Paxos is notoriously difficult
 to implement correctly. Raft achieves the same guarantees with a clearer
 mental model."

THREE SUBPROBLEMS:
  1. Leader Election
  2. Log Replication
  3. Safety

NODE STATES:
  ┌─────────────────────────────────────────┐
  │              RAFT NODE STATES            │
  │                                         │
  │   ┌────────┐    timeout    ┌──────────┐│
  │   │Follower│──────────────>│Candidate ││
  │   │        │               │          ││
  │   │        │<──────────────│          ││
  │   │        │  discovers    │          ││
  │   │        │  new leader   │          ││
  │   └────────┘               └────┬─────┘│
  │        ▲                       │       │
  │        │   receives majority   │       │
  │        │   of votes            │       │
  │        │                       ▼       │
  │   ┌────────┐              ┌────────┐  │
  │   │ Leader │<─────────────│Candidate│  │
  │   │        │  wins election│        │  │
  │   └────────┘              └────────┘  │
  └─────────────────────────────────────────┘

LEADER ELECTION:
  1. Initially all nodes are Followers
  2. If a follower doesn't hear from the leader within a random timeout,
     it becomes a Candidate
  3. Candidate sends RequestVote to all nodes
  4. If majority vote YES → Candidate becomes Leader
  5. Leader sends heartbeat (AppendEntries) to maintain authority

LOG REPLICATION:
  1. Client sends command to Leader
  2. Leader appends command to its log
  3. Leader sends AppendEntries to all Followers
  4. Followers append to their logs, reply ACK
  5. When majority ACK → Leader commits the entry
  6. Leader notifies Followers to commit
  7. State machines apply the committed entry

    Client   Leader    Follower1   Follower2   Follower3
      │         │          │           │           │
      │──cmd──>│          │           │           │
      │         │──log───>│           │           │
      │         │──log──────────────>│           │
      │         │──log──────────────────────────>│
      │         │<──ACK───│           │           │
      │         │<────────────────ACK│           │
      │         │ (majority reached — COMMIT)    │
      │<──OK───│          │           │           │
      │         │──commit>│           │           │
      │         │──commit────────────>│           │
      │         │──commit────────────────────────>│

USED BY: etcd (core of Kubernetes), Consul, CockroachDB, TiDB

PAXOS vs RAFT COMPARISON:
  ┌─────────────┬──────────────────┬──────────────────┐
  │ Aspect      │ Paxos            │ Raft             │
  ├─────────────┼──────────────────┼──────────────────┤
  │ Leader      │ No designated    │ Strong leader    │
  │ Complexity  │ Very complex     │ Simpler          │
  │ Understand. │ Hard to reason   │ Easy to reason   │
  │ Log         │ Not specified    │ Defined log      │
  │ Membership  │ Complex          │ Defined process  │
  │ Used by     │ Spanner, ZK      │ etcd, Consul     │
  └─────────────┴──────────────────┴──────────────────┘
```

### 3.5 Byzantine Generals Problem & BFT (NOT in Alex Xu)

```
SCENARIO: A group of generals surround an enemy city. They must agree
on a common plan (attack or retreat). But some generals are TRAITORS
who spread false information.

  → Traitors can send conflicting messages to different generals
  → Loyal generals can't tell who is a traitor
  → Communication is only via messengers (no broadcast)

REQUIREMENT: Loyal generals must reach consensus despite traitors.

SOLUTION CONSTRAINT: BFT requires less than 1/3 traitors:
  If n = total nodes, f = faulty nodes, then n ≥ 3f + 1

  Example: For 1 traitor → need at least 4 nodes
           For 3 traitors → need at least 10 nodes

BYZANTINE FAULT TOLERANCE (BFT):
  The property of a system that can reach consensus despite Byzantine
  (arbitrary/malicious) faults, not just crash faults.

PBFT (Practical Byzantine Fault Tolerance):
  Used in blockchain (Hyperledger Fabric, and variants in Ethereum)

INTERVIEW APPLICATION: "When would you need BFT?"
  • Blockchain / cryptocurrency → YES (nodes may be malicious)
  • Financial systems → Maybe (nodes crash, but usually not malicious)
  • Web applications → NO (crash fault tolerance is sufficient)
```

### 3.6 FLP Impossibility Theorem (NOT in Alex Xu)

```
FLP (Fischer, Lynch, Paterson, 1985):

"In a fully ASYNCHRONOUS distributed system, it is impossible to
 deterministically solve consensus even with ONE process failure."

THE FLP TRIANGLE:
  ┌────────────────────────────────────────┐
  │         FLP IMPOSSIBILITY               │
  │                                        │
  │  You can achieve at most TWO of:       │
  │                                        │
  │  1. FAULT TOLERANCE                    │
  │     (system works despite failures)    │
  │                                        │
  │  2. AGREEMENT                          │
  │     (all correct processes agree)      │
  │                                        │
  │  3. TERMINATION                        │
  │     (algorithm eventually finishes)    │
  │                                        │
  │  But NOT all three simultaneously      │
  │  in a fully asynchronous system.       │
  └────────────────────────────────────────┘

WHY IT MATTERS: This is why Paxos/Raft use randomness and timeouts —
they "cheat" FLP by assuming partial synchrony (bounded delays).

WORKAROUNDS:
  • Assume partial synchrony (messages eventually arrive within bounds)
  • Use randomness (random timeouts in leader election)
  • Failure detectors (heartbeat-based, with timeouts)
```

### 3.7 Bloom Filters (Covered Briefly by Alex Xu, Deep Dive Here)

```
BLOOM FILTER: A space-efficient probabilistic data structure for
testing set membership.

  "Is element X in the set?"
  → Possibly yes (false positive possible)
  → Definitely no (no false negatives)

HOW IT WORKS:
  1. Start with a bit array of m bits, all set to 0
  2. Use k independent hash functions

  ADD element:
    For each hash function h_i:
      Calculate h_i(element) % m → position in bit array
      Set that position to 1

  CHECK element:
    For each hash function h_i:
      Calculate h_i(element) % m
      If ANY position is 0 → DEFINITELY NOT in set
      If ALL positions are 1 → POSSIBLY in set (could be false positive)

  Example (3 hash functions, bit array of size 10):
    ADD "apple":
      h1("apple") % 10 = 3 → set bit 3
      h2("apple") % 10 = 7 → set bit 7
      h3("apple") % 10 = 1 → set bit 1

    Bit array: [1, 0, 0, 1, 0, 0, 0, 1, 0, 0]

    CHECK "apple":
      h1→3 (set), h2→7 (set), h3→1 (set) → "Possibly yes"

    CHECK "banana":
      h1("banana") % 10 = 5 → bit 5 is 0 → "Definitely no"

SPACE EFFICIENCY:
  1 million URLs, 1% false positive rate → 1.2 MB (vs 50 MB for a hash set)
  1 million URLs, 0.1% false positive rate → 1.8 MB

USED BY:
  • Cassandra (SSTable lookups — avoid disk reads for non-existent keys)
  • Chrome (malicious URL checking)
  • Bitcoin (SPV clients — lightweight transaction verification)
  • Akamai (CDN cache — avoid caching items seen once)
```

### 3.8 Count-Min Sketch (NOT in Alex Xu)

```
COUNT-MIN SKETCH: A probabilistic data structure for counting
frequency of events in a data stream using SUBLINEAR space.

USE CASE: "How many times has user X made API requests in the last hour?"
  → Exact counting: need a hash map of all users → O(n) space
  → Count-Min Sketch: O(log n) space, slightly overestimates

HOW IT WORKS:
  1. Create d rows, each with w counters (all initialized to 0)
  2. Each row has a different hash function

  ADD 1 to count of element X:
    For each row i:
      Calculate h_i(X) % w → column
      Increment counters[i][column] by 1

  GET estimated count of X:
    For each row i:
      Calculate h_i(X) % w → column
      Read counters[i][column]
    Return MINIMUM of all rows

    ┌─────┬─────┬─────┬─────┬─────┐
    │  3  │  7  │  1  │  0  │  5  │  ← hash function 1
    ├─────┼─────┼─────┼─────┼─────┤
    │  2  │  7  │  4  │  1  │  3  │  ← hash function 2
    ├─────┼─────┼─────┼─────┼─────┤
    │  7  │  0  │  2  │  6  │  1  │  ← hash function 3
    └─────┴─────┴─────┴─────┴─────┘

    Query "X": h1→col1(7), h2→col1(7), h3→col0(7) → min(7,7,7) = 7

WHY MINIMUM? Because hash collisions can only INFLATE counts
(the counter includes both the target element AND colliding elements).
The minimum across multiple hash functions has the least inflation.

USED BY:
  • Stream processing (Apache Spark's countMinSketch)
  • Network traffic analysis (flow size estimation)
  • Trending topics (approximate frequency counting)
```

### 3.9 HyperLogLog (NOT in Alex Xu)

```
HYPERLOGLOG: A probabilistic data structure for counting UNIQUE
elements (cardinality) in a data stream using VERY LITTLE memory.

USE CASE: "How many UNIQUE users visited our site today?"
  → Exact count: store all user IDs in a set → O(n) space
  → HyperLogLog: ~12 KB for any cardinality up to ~10^9

HOW IT WORKS (Simplified):
  1. Hash each element to a binary string
  2. Count the number of LEADING ZEROS in the hash
  3. The MAXIMUM number of leading zeros gives an estimate of cardinality

  INTUITION: If you flip coins and get at most k heads in a row,
  you probably flipped about 2^k coins. Same idea with hash leading zeros.

ACCURACY:
  • Standard error: ~0.81% with 12 KB of memory
  • Can count 1 billion unique elements with ~12 KB

  Comparison:
  ┌──────────────────┬───────────────────┬───────────────────┐
  │ Method           │ Space for 1B IDs  │ Accuracy          │
  ├──────────────────┼───────────────────┼───────────────────┤
  │ Hash Set         │ ~40 GB            │ Exact             │
  │ HyperLogLog      │ ~12 KB            │ ±0.81% error      │
  └──────────────────┴───────────────────┴───────────────────┘

  That's a 3,333,333× space reduction for <1% error!

USED BY:
  • Redis (PFCOUNT command — HyperLogLog built-in)
  • Google (BigQuery COUNT(DISTINCT) uses HyperLogLog internally)
  • Twitter (approximate unique user counting)
  • Reddit (unique visitor counting)
```

---

## Chapter 4: DNS, Load Balancers, and Application Gateways

### What Sinha Adds vs Alex Xu

Alex Xu mentions load balancers briefly. Sinha goes deep on **DNS querying, GSLB, LB algorithms, OSI-layer load balancing, and application gateways**.

### DNS Querying (Deep Dive)

```
DNS RESOLUTION PROCESS:

  User types: www.example.com
       │
       ▼
  ┌──────────┐
  │ Browser  │  checks local cache → MISS
  │ Cache    │
  └────┬─────┘
       │
       ▼
  ┌──────────────┐
  │ OS Resolver  │  checks OS cache → MISS
  │ (stub)       │
  └────┬─────────┘
       │
       ▼
  ┌──────────────┐     ┌────────────────────┐
  │ Recursive    │────>│ Root DNS Server    │
  │ Resolver     │<────│ "Try .com TLD"     │
  │ (ISP/Cloud)  │     └────────────────────┘
  └────┬─────────┘
       │
       ▼
  ┌──────────────┐     ┌────────────────────┐
  │ Resolver     │────>│ .com TLD Server    │
  │              │<────│ "Try example.com   │
  │              │     │  nameserver"       │
  └────┬─────────┘     └────────────────────┘
       │
       ▼
  ┌──────────────┐     ┌────────────────────┐
  │ Resolver     │────>│ example.com        │
  │              │     │ Authoritative NS   │
  │              │<────│ "www → 93.184.216.34" │
  └──────────────┘     └────────────────────┘

TOTAL: 3 round trips (root → TLD → authoritative)
```

### Load Balancer Algorithms

```
Sinha covers 7 LB algorithms (Alex Xu covers ~3):

1. ROUND ROBIN: Cycle through servers in order. Simple, even distribution.
   Server 1 → Server 2 → Server 3 → Server 1 → ...

2. WEIGHTED ROUND ROBIN: Same but with weights for different-capacity servers.
   Server 1 (weight 3) → Server 2 (weight 1) → Server 1 → Server 1 → Server 2

3. LEAST CONNECTIONS: Send to server with fewest active connections.
   Best for long-lived connections (WebSocket, streaming).

4. IP HASH: hash(client_ip) → determines server.
   Ensures same client always goes to same server (sticky sessions).

5. LEAST RESPONSE TIME: Send to server with lowest avg response time.
   Combines connection count with response time.

6. RESOURCE-BASED: Check server CPU/memory, send to least loaded.
   Requires agent on each server.

7. RANDOM: Pick a random server. Simple, surprisingly effective at scale.
```

### Load Balancing at Different OSI Layers

```
┌──────────────────────────────────────────────────────────────┐
│           LOAD BALANCING AT EACH OSI LAYER                   │
│                                                              │
│  LAYER 4 (Transport — TCP/UDP):                              │
│    • Load balances based on IP + port                        │
│    • Very fast (doesn't inspect packet content)             │
│    • Examples: HAProxy (L4 mode), AWS NLB                   │
│    • Use when: you need raw speed, no routing logic          │
│                                                              │
│  LAYER 7 (Application — HTTP/HTTPS):                         │
│    • Load balances based on URL, headers, cookies            │
│    • Can route /api/* to one service, /images/* to another   │
│    • Examples: Nginx, AWS ALB, HAProxy (L7 mode)            │
│    • Use when: you need content-based routing                │
│                                                              │
│  GLOBAL SERVER LOAD BALANCING (GSLB):                        │
│    • DNS-based routing to nearest data center                │
│    • Uses GeoDNS to route EU users → EU DC, US → US DC      │
│    • Examples: Route 53, Cloudflare, F5 GTM                 │
└──────────────────────────────────────────────────────────────┘
```

### Application Gateways

```
An Application Gateway is a SPECIALIZED Layer 7 load balancer that
provides additional features:

  • SSL Termination (decrypt HTTPS, forward as HTTP)
  • Web Application Firewall (WAF) — block SQL injection, XSS
  • Session affinity (sticky sessions based on cookies)
  • URL-based routing (/api/v1/* → Service A)
  • Rate limiting (per-IP, per-user)
  • Request rewriting (modify headers, URLs)

AWS Application Load Balancer (ALB) is the most common cloud example.
```

---

## Sinha vs Alex Xu Comparison

```
┌────────────────────────────┬──────────────────┬──────────────────┐
│ Topic                      │ Alex Xu Vol 1    │ Sinha            │
├────────────────────────────┼──────────────────┼──────────────────┤
│ Scaling basics             │ ✓ Deep           │ ✓ Good           │
│ CAP theorem                │ Brief            │ ✓ Deep           │
│ PACELC theorem             │ ✗ Not covered    │ ✓ Deep ⭐        │
│ Paxos                      │ ✗ Not covered    │ ✓ Deep ⭐        │
│ Raft                       │ ✗ Not covered    │ ✓ Deep ⭐        │
│ Byzantine fault tolerance  │ ✗ Not covered    │ ✓ Deep ⭐        │
│ FLP impossibility          │ ✗ Not covered    │ ✓ Deep ⭐        │
│ Consistent hashing         │ ✓ Good           │ ✓ Good           │
│ Bloom filters              │ ✗ Not covered    │ ✓ Deep ⭐        │
│ Count-min sketch           │ ✗ Not covered    │ ✓ Deep ⭐        │
│ HyperLogLog                │ ✗ Not covered    │ ✓ Deep ⭐        │
│ DNS                        │ Mentioned        │ ✓ Deep           │
│ Load balancers             │ Brief            │ ✓ Deep (7 algos) │
│ App gateways               │ ✗ Not covered    │ ✓ Covered        │
│ Interview framework        │ ✓ 4-step         ✓ Tips + checklist │
│ System design problems     │ 15 problems      │ 6 problems       │
│ Estimation                 │ ✓ Good           │ ✓ Good           │
│ Docker/K8s                 │ ✗ Not covered    │ ✓ Mentioned      │
│ Difficulty                 │ Beginner-Med     │ Intermediate-Adv │
└────────────────────────────┴──────────────────┴──────────────────┘

VERDICT:
  • Read Alex Xu FIRST for interview pattern recognition and practice
  • Read Sinha SECOND for deep theoretical understanding
  • Together they give you the most complete system design preparation
```

---

## Interview Q&As

### Q1: "Explain the PACELC theorem."

"PACELC extends CAP. CAP says during a partition, you choose availability or consistency. PACELC adds: even WITHOUT a partition, you choose between latency and consistency. So a system like Cassandra is PA/EL — during partitions it chooses availability, and during normal operation it prefers low latency. HBase is PC/EC — it always prefers consistency. This is important because most interviewees only know CAP, but real-world systems are designed with PACELC tradeoffs in mind."

### Q2: "What's the difference between Paxos and Raft?"

"Both solve distributed consensus, but Raft was designed specifically for understandability. Paxos doesn't have a designated leader — any proposer can initiate consensus. Raft has a strong leader — all client requests go through the leader, who manages log replication. Raft decomposes the problem into three clear subproblems: leader election, log replication, and safety. Paxos is more general but notoriously difficult to implement correctly. In practice, most modern systems (etcd, Consul, CockroachDB) use Raft because it's easier to reason about."

### Q3: "When would you need Byzantine fault tolerance?"

"BFT is needed when nodes can behave MALICIOUSLY, not just crash. Blockchain systems need BFT because participants may be adversaries trying to double-spend. Traditional distributed databases don't need BFT — they use crash fault tolerance (Paxos/Raft), which assumes nodes either work correctly or stop entirely. BFT requires n ≥ 3f + 1 nodes (to tolerate f Byzantine faults), while CFT only needs n ≥ 2f + 1. The extra nodes make BFT more expensive, so it's only used when malicious behavior is a real threat."

### Q4: "How would you use a Bloom filter in a distributed system?"

"I'd use it as a fast membership test to avoid expensive lookups. For example, in Cassandra, before reading an SSTable (disk file), the system checks a Bloom filter to see if the key might be in that file. If the Bloom filter says 'no,' the disk read is skipped entirely — saving I/O. If it says 'yes,' the disk is read (might be a false positive). Bloom filters are space-efficient: 1 million keys with 1% false positive rate needs only 1.2 MB, versus 50 MB for a hash set."

### Q5: "How does HyperLogLog achieve such extreme space efficiency?"

"HyperLogLog exploits the statistical properties of hash functions. When you hash elements, the number of leading zeros in the hash follows a geometric distribution. If the maximum leading zeros observed is k, the estimated cardinality is approximately 2^k. By using multiple hash functions (or partitioning the hash space into buckets), HyperLogLog achieves ~0.81% error with only 12 KB of memory, regardless of whether you're counting 1 thousand or 1 billion unique elements. That's a 3-million-to-1 space reduction versus a hash set."

---

> **Next:** Core Components (Databases, Cache, Pub/Sub, APIs) → `08-sinha-core-components.md`
