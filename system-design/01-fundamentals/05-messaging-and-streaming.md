# Messaging & Streaming — Async Communication Patterns

> **Analogy:** Imagine a post office. You drop a letter in a mailbox. You don't wait for the mail carrier to deliver it right now. You trust the system to deliver it eventually. That's async messaging.

---

## Why Async Communication?

**Synchronous (HTTP):** Service A calls Service B and **waits** for a response.
```
Service A ──"give me data"──> Service B
Service A <──"here's data"─── Service B
     ↑ BLOCKED the entire time ↑
```

**Problem:** If Service B is slow or down, Service A is stuck. One slow service cascades and takes down the entire system.

**Asynchronous (Message Queue):** Service A drops a message in a queue and **immediately moves on**. Service B picks it up when ready.
```
Service A ──"process this"──> [QUEUE] ──"process this"──> Service B
     ↓ immediately free                          ↑ picks up when ready
```

**Benefits:**
- **Decoupling:** Services don't need to know about each other
- **Resilience:** If B is down, messages wait in the queue. No data loss.
- **Scaling:** Add more workers (B instances) to drain the queue faster
- **Load leveling:** Smooth out traffic spikes (queue absorbs the burst)

---

## Message Queues vs Streaming

| Feature | Message Queue (RabbitMQ, SQS) | Streaming (Kafka, Kinesis) |
|---------|-------------------------------|---------------------------|
| Analogy | Mailbox (consume → delete) | Conveyor belt (replay) |
| Message lifecycle | Consumed once → deleted | Retained for N days |
| Replay | No (gone after read) | Yes (rewind to offset) |
| Throughput | Medium (10K-100K/sec) | Very high (millions/sec) |
| Use case | Task dispatch, job queue | Event sourcing, analytics, real-time |
| Ordering | Per-consumer | Per-partition |

### When to Use Queue vs Stream

```
Use a QUEUE when:
  - "Process this order" (do the work, then done)
  - "Send this email" (fire and forget)
  - "Resize this image" (background job)

Use STREAMING when:
  - "User clicked X" (analytics, dashboards)
  - "Temperature sensor reading" (real-time monitoring)
  - "All financial transactions" (audit trail, event sourcing)
  - Multiple consumers need the same event independently
```

---

## Message Queue Architecture

```
                    ┌──────────────┐
  Producer ───────> │   EXCHANGE    │ (routes messages)
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    QUEUE      │ (buffer, FIFO)
                    │  [msg][msg][] │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Worker 1     Worker 2     Worker 3
         (processes messages concurrently)
```

**Producer:** Creates and sends messages.
**Queue:** Buffered storage (first-in-first-out).
**Consumer/Worker:** Reads and processes messages.
**Exchange (RabbitMQ):** Routes messages to queues based on rules.

---

## Delivery Semantics

| Semantic | Guarantee | Risk | Use Case |
|----------|-----------|------|----------|
| At-most-once | Message delivered 0 or 1 times | May lose messages | Metrics, logs (loss OK) |
| At-least-once | Message delivered 1+ times | May duplicate | Orders, payments (must process) |
| Exactly-once | Message delivered exactly 1 time | Hard to achieve | Financial transactions |

### How to Handle Duplicates (Idempotency)

"At-least-once" is the default for most systems. To prevent duplicate processing, make consumers **idempotent** — processing the same message twice has the same effect as once.

```python
# Idempotent consumer pattern
def process_message(msg):
    if already_processed(msg.id):
        return  # Skip — already done

    do_work(msg)

    mark_processed(msg.id)  # Record in DB
```

Use a unique message ID + a "processed" table/flag in the database.

---

## Pub/Sub (Publish-Subscribe) Pattern

```
                    ┌──────────────┐
  Publisher ──────> │    TOPIC      │
                    └──┬───┬───┬───┘
                       │   │   │
                       ▼   ▼   ▼
                    Sub A Sub B Sub C
                    (each gets a copy)
```

**One message → multiple independent consumers.**

Example: "User signed up" event →
- Email service sends welcome email
- Analytics service tracks signup
- Recommendation service initializes profile
- CRM creates contact

Each subscriber acts independently. If one fails, others are unaffected.

---

## Dead Letter Queue (DLQ)

What happens to messages that fail repeatedly? They go to the **Dead Letter Queue**.

```
[Main Queue] → Worker tries 3 times → FAILS → [Dead Letter Queue]
                                                    ↓
                                              Manual investigation / alerts
```

- After N failed delivery attempts, move to DLQ
- Alerts ops team for investigation
- Prevents poison-pill messages from blocking the queue

---

## Real-World Example: Order Processing Pipeline

```
User clicks "Buy"
    │
    ▼
Order Service ──"order:created"──> [Kafka Topic]
                                      │
                    ┌─────────────────┼──────────────────┐
                    ▼                 ▼                   ▼
              Payment Service   Inventory Service   Email Service
              (charges card)    (reserves items)    (sends confirm)
                    │
                    ▼
              "payment:success" ──> [Kafka Topic]
                                      │
                    ┌─────────────────┘
                    ▼
              Shipping Service (starts packing)
```

Each service produces and consumes events. No direct HTTP calls. Fully decoupled.

---

## Technology Choices

| Tool | Type | Best For | Cloud Equivalent |
|------|------|----------|-----------------|
| RabbitMQ | Queue | Complex routing, task dispatch | Amazon MQ |
| Amazon SQS | Queue | Simple, managed task queue | (is the cloud version) |
| Apache Kafka | Streaming | High-throughput event streaming | MSK / Confluent |
| Redis Streams | Streaming | Lightweight streaming | ElastiCache |
| Google Pub/Sub | Pub/Sub | GCP event-driven | (native GCP) |

---

## Interview Q&A

**Q: Why use async messaging instead of just calling an API?**
A: Three reasons: (1) Decoupling — the caller doesn't need to know who handles the work. (2) Resilience — if the worker is down, messages buffer in the queue. (3) Load leveling — smooths traffic spikes by absorbing bursts.

**Q: Kafka vs RabbitMQ — how do you choose?**
A: Kafka for high-throughput streaming where you need replay and multiple consumers (analytics, event sourcing). RabbitMQ for point-to-point task dispatch with complex routing rules. Kafka = conveyor belt. RabbitMQ = smart mailbox.

**Q: How do you ensure exactly-once processing?**
A: True exactly-once is very hard. The practical approach is at-least-once + idempotent consumers. Use a unique message ID and track processed IDs in a database. If you see the same ID again, skip it.

**Q: What happens if the consumer crashes mid-processing?**
A: Use acknowledgment. The consumer only ACKs the message after successful processing. If it crashes before ACKing, the broker redelivers the message. This guarantees at-least-once delivery.

**Q: How do you handle message ordering at scale?**
A: Use partitioning. Messages with the same key (e.g., user_id) go to the same partition, which is processed by a single consumer in order. Different keys can be processed in parallel across partitions.
