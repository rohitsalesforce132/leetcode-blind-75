# Sinha — Core Components of Distributed Systems (Chapters 5-8)

> **Source:** "System Design Guide for Professionals" by Dhirendra Sinha
> **Coverage:** Ch 5 (Databases & Storage), Ch 6 (Distributed Cache), Ch 7 (Pub/Sub & Queues), Ch 8 (API, Security, Metrics)

---

## TABLE OF CONTENTS

1. [Chapter 5: Databases and Storage](#chapter-5)
2. [Chapter 6: Distributed Cache](#chapter-6)
3. [Chapter 7: Pub/Sub and Distributed Queues](#chapter-7)
4. [Chapter 8: API, Security, and Metrics](#chapter-8)

---

## Chapter 5: Databases and Storage

### Database Taxonomy (Sinha Goes Much Deeper Than Alex Xu)

```
┌──────────────────────────────────────────────────────────────────────┐
│                   DATABASE TAXONOMY                                   │
│                                                                      │
│  RELATIONAL (SQL)                                                    │
│  ├── PostgreSQL, MySQL, Oracle, SQL Server                           │
│  ├── ACID transactions                                               │
│  ├── Strict schema                                                   │
│  ├── JOINs                                                           │
│  └── Best for: Complex queries, transactional data                   │
│                                                                      │
│  NoSQL                                                               │
│  ├── KEY-VALUE: Redis, DynamoDB, Riak                                │
│  │   └── Best for: Fast lookups, session storage                     │
│  ├── COLUMN-FAMILY: Cassandra, HBase                                 │
│  │   └── Best for: Time-series, write-heavy workloads                │
│  ├── DOCUMENT: MongoDB, CouchDB                                      │
│  │   └── Best for: Flexible schema, content management               │
│  └── GRAPH: Neo4j, Amazon Neptune                                    │
│      └── Best for: Relationships, social networks, fraud detection   │
│                                                                      │
│  TIME-SERIES: InfluxDB, TimescaleDB                                  │
│  SEARCH: Elasticsearch, Solr                                         │
└──────────────────────────────────────────────────────────────────────┘
```

### DynamoDB Deep Dive (Sinha Covers Internals)

```
DynamoDB Architecture (Amazon's key-value store):

PARTITIONING:
  Data is partitioned using the partition key.
  DynamoDB uses consistent hashing internally.
  
  Partition key → hash → node assignment
  Each partition handles up to 10 GB of data.

THROUGHPUT:
  Each partition has dedicated read/write capacity.
  Read Capacity Units (RCU): 1 RCU = 1 strongly consistent read/sec
                              OR 2 eventually consistent reads/sec
                              (for items up to 4KB)
  Write Capacity Units (WCU): 1 WCU = 1 write/sec (for items up to 1KB)

  Example: Table with 10,000 WCU and 20,000 RCU
  → Can sustain 10,000 writes/sec and 20,000 reads/sec

REPLICATION:
  Each partition is replicated across 3 Availability Zones.
  Uses Raft consensus for leader election within a replication group.

  Leader handles all writes → replicates to followers
  Followers can serve eventually consistent reads
  Strong reads go through the leader
```

### HBase Architecture (Column-Family Store)

```
HBase = Google's BigTable open-source implementation

DATA MODEL:
  Row Key → Column Family → Column Qualifier → Version (timestamp) → Value

  Example:
  Row Key: user123
    Column Family: contact
      Column: email, Version 3 (latest) → "john@email.com"
      Column: phone, Version 2 → "+1234567890"
    Column Family: profile
      Column: age, Version 1 → 30
      Column: city, Version 5 → "Mumbai"

STORAGE (LSM-Tree):
  Writes → WAL (Write-Ahead Log) → MemStore (in memory)
  When MemStore is full → Flush to HFile (on HDFS)
  HFiles are periodically compacted (merged)

  Reads: Check MemStore → Check Bloom Filter → Read HFile

ARCHITECTURE:
  ┌───────────┐     ┌───────────┐     ┌───────────┐
  │ HBase     │────>│ Region    │────>│ HFile     │
  │ Master    │     │ Server    │     │ (on HDFS) │
  │ (metadata │     │ (handles  │     └───────────┘
  │  mgmt)    │     │  reads/   │
  └───────────┘     │  writes)  │
                    └───────────┘
  ZooKeeper coordinates master election and region assignment
```

### Neo4j Graph Database

```
Sinha covers graph databases — Alex Xu doesn't.

NEO4J DATA MODEL:
  Nodes: Entities (Person, Product, City)
  Relationships: Connections between nodes (KNOWS, BOUGHT, LIVES_IN)
  Properties: Key-value pairs on nodes and relationships

  Example:
  (Person:John)-[:KNOWS {since: 2020}]->(Person:Alice)
  (Person:Alice)-[:BOUGHT {amount: $50}]->(Product:iPhone)

CYPHER QUERY:
  MATCH (p:Person)-[:KNOWS]->(friend:Person)
  WHERE p.name = "John"
  RETURN friend.name

WHEN TO USE GRAPH DATABASE:
  • Social networks (friend recommendations)
  • Fraud detection (pattern matching in transaction networks)
  • Network topology (telecom infrastructure)
  • Recommendation engines (product→user relationships)

INTERVIEW CONNECTION: "My GraphRAG project uses Neo4j to model
telecom network dependencies. 297 entities, 6,822 relationships."
```

---

## Chapter 6: Distributed Cache

### Cache Write Strategies (Sinha Deep Dive)

```
┌──────────────────────────────────────────────────────────────────────┐
│                   CACHE WRITE STRATEGIES                              │
│                                                                      │
│  WRITE-THROUGH:                                                      │
│    Write to cache AND database simultaneously (synchronously)        │
│    ┌──────┐  write  ┌──────┐  write  ┌──────────┐                  │
│    │ App  │────────>│Cache │────────>│ Database │                  │
│    └──────┘         └──────┘         └──────────┘                  │
│    Pros: Cache always consistent with DB                             │
│    Cons: Higher write latency (two writes)                          │
│                                                                      │
│  WRITE-AROUND (Write-Behind):                                        │
│    Write directly to database, skip cache                            │
│    ┌──────┐  write  ┌──────────┐                                    │
│    │ App  │────────>│ Database │                                    │
│    └──────┘         └──────────┘                                    │
│    Cache populated on first READ (lazy loading)                      │
│    Pros: Fast writes (no cache write needed)                         │
│    Cons: First read is slow (cache miss)                             │
│                                                                      │
│  WRITE-BACK (Write-Behind):                                          │
│    Write to cache first, async write to database later               │
│    ┌──────┐  write  ┌──────┐  async  ┌──────────┐                 │
│    │ App  │────────>│Cache │────────>│ Database │                 │
│    └──────┘         └──────┘         └──────────┘                 │
│    Pros: Very fast writes (only cache)                               │
│    Cons: Risk of data loss if cache crashes before DB write         │
│                                                                      │
│  CHOOSING A STRATEGY:                                                │
│    • Read-heavy → Write-Through (cache always populated)             │
│    • Write-heavy → Write-Around (don't pollute cache with writes)    │
│    • Ultra-low latency → Write-Back (but accept data loss risk)     │
└──────────────────────────────────────────────────────────────────────┘
```

### Cache Eviction Policies

```
LRU (Least Recently Used):
  Evict the item accessed least recently.
  Implementation: Doubly linked list + hash map → O(1) eviction
  Used by: Redis (approximate LRU), Memcached

LFU (Least Frequently Used):
  Evict the item with the fewest accesses.
  Better than LRU for items with long-term popularity.
  Used by: Redis (LFU mode available since 4.0)

FIFO (First In First Out):
  Evict the oldest item regardless of access pattern.
  Simplest to implement. Rarely the best choice.

TTL (Time-To-Live):
  Items expire after a set time.
  Can be combined with LRU/LFU.
  Used by: Almost all production caches (as a complementary policy)

ARC (Adaptive Replacement Cache):
  Dynamically balances between LRU and LFU.
  Adapts to workload patterns automatically.
  Used by: ZFS (file system)
```

### Redis vs Memcached (Sinha's Comparison)

```
┌──────────────────┬────────────────────┬────────────────────┐
│ Feature          │ Redis              │ Memcached          │
├──────────────────┼────────────────────┼────────────────────┤
│ Data structures  │ Strings, Lists,    │ Strings only       │
│                  │ Sets, Hashes,      │                    │
│                  │ Sorted Sets,       │                    │
│                  │ Streams, Bitmaps   │                    │
│ Persistence      │ Yes (RDB + AOF)    │ No (in-memory only)│
│ Replication      │ Master-slave       │ No native support  │
│ Clustering       │ Yes (Redis Cluster)│ Yes (client-side   │
│                  │                    │  sharding)         │
│ Max value size   │ 512 MB             │ 1 MB               │
│ Threading        │ Single-threaded    │ Multi-threaded     │
│ Pub/Sub          │ Yes                │ No                 │
│ Lua scripting    │ Yes                │ No                 │
│ Memory efficiency│ Good               │ Better (for simple │
│                  │                    │  key-value)        │
│ Speed            │ ~100K ops/sec      │ ~100K+ ops/sec     │
└──────────────────┴────────────────────┴────────────────────┘

WHEN TO USE WHICH:
  • Redis: When you need data structures, persistence, or pub/sub
  • Memcached: When you need simple key-value caching with max speed
```

---

## Chapter 7: Pub/Sub and Distributed Queues

### Kafka Architecture (Sinha's Deep Dive)

```
┌──────────────────────────────────────────────────────────────────────┐
│                       KAFKA ARCHITECTURE                              │
│                                                                      │
│  ┌──────────┐   ┌──────────────────────────────────────────┐        │
│  │ Producer │──>│              KAFKA CLUSTER               │        │
│  └──────────┘   │                                          │        │
│                 │  ┌─────────────┐  ┌─────────────┐       │        │
│                 │  │  Broker 1   │  │  Broker 2   │       │        │
│                 │  │             │  │             │       │        │
│                 │  │ Topic:      │  │ Topic:      │       │        │
│                 │  │  orders     │  │  payments   │       │        │
│                 │  │             │  │             │       │        │
│                 │  │ Partition 0 │  │ Partition 0 │       │        │
│                 │  │ [msg1,msg2] │  │ [msg1,msg2] │       │        │
│                 │  │             │  │             │       │        │
│                 │  │ Partition 1 │  │ Partition 1 │       │        │
│                 │  │ [msg3,msg4] │  │ [msg3,msg4] │       │        │
│                 │  └─────────────┘  └─────────────┘       │        │
│                 └──────────────────────────────────────────┘        │
│                          │                                           │
│                 ┌────────┴────────┐                                 │
│                 │  ZooKeeper      │  (coordinates brokers,          │
│                 │  / KRaft        │   leader election, membership)  │
│                 └─────────────────┘                                 │
│                                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                        │
│  │Consumer  │   │Consumer  │   │Consumer  │                        │
│  │Group A   │   │Group B   │   │Group C   │                        │
│  │(reads    │   │(reads    │   │(independent                              │
│  │ orders)  │   │ payments)│   │  consumer)                              │
│  └──────────┘   └──────────┘   └──────────┘                        │
└──────────────────────────────────────────────────────────────────────┘

KEY CONCEPTS:
  • Topic: A named stream of messages (e.g., "orders")
  • Partition: A topic is split into partitions for parallelism
  • Offset: Position of a message within a partition
  • Consumer Group: A set of consumers that share partitions
  • Broker: A Kafka server that stores messages
  • ZooKeeper/KRaft: Coordinates the cluster

PARTITIONING:
  Messages are distributed across partitions using a key:
  partition = hash(key) % num_partitions

  Messages with the SAME KEY always go to the SAME PARTITION
  → Guarantees ordering within a partition

RETENTION:
  Kafka retains messages for a configurable period (default: 7 days)
  → Consumers can replay messages if needed
  → This is fundamentally different from traditional queues (RabbitMQ)
    where messages are DELETED after consumption
```

### Kafka vs Traditional Queues (RabbitMQ)

```
┌──────────────────┬────────────────────────┬──────────────────────┐
│ Feature          │ Kafka                  │ RabbitMQ             │
├──────────────────┼────────────────────────┼──────────────────────┤
│ Model            │ Pub/Sub + log          │ Traditional queue    │
│ Message retention│ Days/weeks (retention) │ Deleted after ack    │
│ Replay           │ Yes (re-read from log) │ No                   │
│ Throughput       │ Millions/sec           │ ~100K/sec            │
│ Ordering         │ Per partition          │ Per queue            │
│ Consumer model   │ Pull-based             │ Push-based           │
│ Best for         │ Event streaming, log   │ Task queues, RPC     │
│                  │ aggregation, CDC       │ work distribution    │
└──────────────────┴────────────────────────┴──────────────────────┘
```

---

## Chapter 8: API, Security, and Metrics

### REST vs gRPC (Sinha's Deep Comparison)

```
┌──────────────────┬────────────────────────┬──────────────────────┐
│ Feature          │ REST                   │ gRPC                 │
├──────────────────┼────────────────────────┼──────────────────────┤
│ Protocol         │ HTTP/1.1 (usually)     │ HTTP/2               │
│ Format           │ JSON (text-based)      │ Protobuf (binary)    │
│ Speed            │ Slower (text parsing)  │ Faster (binary)      │
│ Streaming        │ No (request-response)  │ Yes (bi-directional) │
│ Browser support  │ Native                 │ Requires gRPC-Web    │
│ Schema           │ OpenAPI (optional)     │ Protobuf (required)  │
│ Code generation  │ Optional               │ Built-in             │
│ Best for         │ Public APIs,           │ Microservices,       │
│                  │ browser clients         │ internal service    │
│                  │                        │ communication        │
└──────────────────┴────────────────────────┴──────────────────────┘

INTERVIEW ANSWER: "I use REST for external/public APIs because
  browsers and mobile apps work with it natively. I use gRPC for
  internal microservice communication because it's faster (binary
  Protobuf), supports streaming, and has built-in code generation."
```

### Distributed Tracing (Observability — Key for FDE Interviews)

```
Sinha covers observability (logging, metrics, tracing) — critical for
production systems and a hot topic in interviews.

DISTRIBUTED TRACING FLOW:

  Client → Service A → Service B → Database
            │           │
            │ trace_id  │ trace_id (propagated)
            │ span_id_A │ span_id_B
            │           │
            ▼           ▼
  ┌──────────────────────────────────────────┐
  │           TRACE: abc123                   │
  │                                          │
  │  Span 1: Service A (12ms)                │
  │    ├── Span 2: Service B (8ms)           │
  │    │     └── Span 3: DB query (5ms)     │
  │    └── Span 4: Cache lookup (1ms)       │
  └──────────────────────────────────────────┘

  Each span records:
    • Service name
    • Operation name
    • Start time, duration
    • Tags (key-value metadata)
    • Parent span ID (creates the tree)

TOOLS:
  • Jaeger (open source, CNCF)
  • Zipkin (open source, Twitter)
  • OpenTelemetry (standard for instrumentation)
  • Datadog APM (commercial)

INTERVIEW CONNECTION: "My AgentTrace project implements distributed
 tracing for AI agents. Each agent step (LLM call, tool call) is a span.
 This is exactly the same pattern — just applied to agent execution."
```

### The Three Pillars of Observability

```
┌──────────────────────────────────────────────────────────────┐
│              THREE PILLARS OF OBSERVABILITY                   │
│                                                              │
│  1. LOGGING: Discrete events with context                   │
│     "User 12345 logged in from IP 10.0.0.1 at 14:32:01"    │
│     Tools: ELK (Elasticsearch, Logstash, Kibana),           │
│            Splunk, Loki                                     │
│                                                              │
│  2. METRICS: Numeric measurements over time                 │
│     "Request rate: 5000/sec, P99 latency: 250ms"           │
│     Tools: Prometheus, Grafana, CloudWatch                  │
│                                                              │
│  3. TRACING: Request flow across services                   │
│     "Request entered via API Gateway →                      │
│      Auth Service → Order Service → Database"               │
│     Tools: Jaeger, Zipkin, OpenTelemetry                    │
│                                                              │
│  GOLDEN RULE: All three are needed.                          │
│    Logs tell you WHAT happened.                             │
│    Metrics tell you HOW MUCH and HOW FAST.                  │
│    Traces tell you WHERE time was spent.                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Interview Q&As

### Q1: "How would you choose between SQL and NoSQL for a new application?"

"I default to SQL (PostgreSQL) for most applications because it's mature, ACID-compliant, and handles complex queries with JOINs. I switch to NoSQL when there's a clear need: DynamoDB for key-value workloads with predictable throughput, Cassandra for write-heavy time-series data, MongoDB for flexible-schema content, Neo4j for relationship-heavy queries like social networks. In practice, many systems use polyglot persistence — SQL for transactional data and NoSQL for specialized workloads."

### Q2: "Compare write-through, write-around, and write-back caching."

"Write-through writes to cache AND database synchronously — cache is always consistent but writes are slower. Write-around skips the cache on writes — fast writes but first read is a cache miss. Write-back writes to cache first and asynchronously flushes to the database — fastest writes but risk of data loss if cache crashes. I'd use write-through for financial data, write-around for write-heavy workloads with sporadic reads, and write-back only when I can tolerate potential data loss."

### Q3: "When would you use Kafka vs RabbitMQ?"

"Kafka for event streaming, log aggregation, and change data capture where you need message retention and replay. RabbitMQ for task queues and RPC where messages should be consumed and deleted. Kafka can handle millions of messages per second with persistence — it's a distributed log, not just a queue. RabbitMQ is simpler for point-to-point or fanout messaging with lower throughput needs."

### Q4: "How does distributed tracing work?"

"Each request gets a unique trace ID. As the request flows through services, each service creates a span — a timed unit of work with the trace ID, span ID, and parent span ID. Spans form a tree that shows the full request path. OpenTelemetry instruments code to automatically propagate trace context across service boundaries. The traces are sent to a backend like Jaeger for visualization. In my AgentTrace project, I apply this same pattern to AI agent execution."

### Q5: "Why gRPC over REST for internal microservices?"

"gRPC uses HTTP/2 with Protobuf binary encoding, which is faster than REST's JSON text parsing. gRPC supports bi-directional streaming, which is critical for real-time services. The Protobuf schema provides type safety and automatic code generation in multiple languages. For internal services where both producer and consumer are in the same network, gRPC's performance and type safety are significant advantages over REST."

---

> **Next:** System Design Practice (URL Shortener, Proximity, Twitter, Instagram, Google Docs, Netflix) → `09-sinha-system-design-practice.md`
