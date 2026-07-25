# Designing ML Systems — Foundations (Ch 1-3)

> **Source:** "Designing Machine Learning Systems" by Chip Huyen
> **Coverage:** Ch 1 (Overview), Ch 2 (ML Systems Design), Ch 3 (Data Engineering)

---

## Chapter 1: Overview of ML Systems

### When to Use ML

```
Huyen's criteria for when ML is the RIGHT tool:

USE ML WHEN:
  ✓ The problem is complex enough that rules don't scale
  ✓ You have data with patterns the model can learn
  ✓ The environment changes (ML adapts, rules don't)
  ✓ It's cost-effective (ROI justifies the infrastructure)

DON'T USE ML WHEN:
  ✗ The problem is simple enough for rules/heuristics
  ✗ You don't have enough data
  ✗ The cost of being wrong is catastrophic (use rules)
  ✗ The problem requires explainability (use interpretable models)
  ✗ The ROI doesn't justify the infrastructure cost
```

### ML in Research vs Production

```
┌──────────────────────┬─────────────────────┬─────────────────────┐
│ Aspect               │ Research            │ Production           │
├──────────────────────┼─────────────────────┼─────────────────────┤
│ Goal                 │ Best possible metric│ Trade-off metrics   │
│                      │ (accuracy, F1)      │ with latency/cost   │
│ Data                 │ Static, clean,      │ Dynamic, messy,     │
│                      │ well-labeled        │ shifting            │
│ Fairness             │ Nice to have        │ Required by law     │
│ Interpretability     │ Optional            │ Often required      │
│ Constraints          │ Few (compute, time) │ Many (latency,      │
│                      │                     │ cost, privacy)      │
│ Requirements         │ Static              │ Evolving            │
│ Infrastructure       │ One experiment      │ 24/7 serving,       │
│                      │                     │ monitoring, CI/CD   │
│ Failures             │ Restart experiment  │ Incident, SLA breach│
│ Team                 │ Individual          │ Cross-functional    │
└──────────────────────┴─────────────────────┴─────────────────────┘
```

---

## Chapter 2: Introduction to ML Systems Design

### Requirements for ML Systems

```
Huyen identifies 4 requirements (inspired by traditional software):

1. RELIABILITY
   System continues to perform correctly even when things go wrong.
   For ML: model predictions must remain accurate despite data shifts.

2. SCALABILITY
   System handles increased load gracefully.
   For ML: serve predictions to 10x users without 10x latency.

3. MAINTAINABILITY
   Different teams can collaborate on the system.
   For ML: data scientists, ML engineers, and DevOps can all contribute.

4. ADAPTABILITY (ML-SPECIFIC)
   System adapts to changing data distributions.
   For ML: continual learning, automated retraining.
   THIS IS UNIQUE TO ML — traditional software doesn't need it.
```

### The Iterative Process

```
Huyen's iterative ML development cycle:

  ┌──────────────────────────────────────────────────┐
  │                                                  │
  │    1. Frame the problem                          │
  │         ↓                                        │
  │    2. Data engineering                           │
  │         ↓                                        │
  │    3. Feature engineering                        │
  │         ↓                                        │
  │    4. Model development                          │
  │         ↓                                        │
  │    5. Deployment                                 │
  │         ↓                                        │
  │    6. Monitoring & continual learning            │
  │         ↓                                        │
  │    (Feedback → back to step 1)                   │
  │                                                  │
  └──────────────────────────────────────────────────┘

  KEY: Each iteration adds ONE improvement.
  Don't try to build the perfect system upfront.
  Start simple, measure, iterate.
```

### Framing ML Problems

```
TYPES OF ML TASKS:
  1. Binary Classification: spam/not spam
  2. Multiclass Classification: cat/dog/bird
  3. Regression: predict house price
  4. Clustering: group similar customers
  5. Ranking: search results order
  6. Generation: text, images, code
  7. Recommendation: suggest products
  8. Anomaly Detection: fraud detection

OBJECTIVE FUNCTION CHOICE:
  Classification → Cross-entropy loss
  Regression     → MSE (mean squared error)
  Ranking        → NDCG (normalized discounted cumulative gain)
  Generation     → Negative log-likelihood

HUYEN'S ADVICE:
  "Framing the problem correctly is 80% of the work.
   The wrong objective function leads to the wrong model."
```

---

## Chapter 3: Data Engineering Fundamentals

### Data Sources

```
FOUR MAIN DATA SOURCES:
  1. User data: clicks, searches, purchases, interactions
  2. Enterprise data: CRM, ERP, inventory, billing
  3. Synthetic data: generated for augmentation, privacy
  4. Third-party data: weather, economic indicators, demographics

DATA FORMAT TRADEOFFS:
  ┌──────────────┬─────────────┬─────────────┬──────────────┐
  │ Format       │ Read Speed  │ Write Speed │ Size         │
  ├──────────────┼─────────────┼─────────────┼──────────────┤
  │ JSON         │ Slow (text) │ Fast        │ Large        │
  │ CSV          │ Slow        │ Fast        │ Medium       │
  │ Parquet      │ Fast (col)  │ Medium      │ Small (comp) │
  │ Avro         │ Medium (row)│ Fast        │ Medium       │
  │ Pickle       │ Fast (bin)  │ Fast        │ Medium       │
  └──────────────┴─────────────┴─────────────┴──────────────┘

  Row-major (Avro, CSV): Good for write-heavy, transactional
  Column-major (Parquet, ORC): Good for read-heavy, analytical
```

### Data Models

```
RELATIONAL MODEL (SQL):
  Strict schema, ACID, JOINs
  Best for: Transactional data (orders, users, accounts)

NOSQL MODELS:
  Document (MongoDB): Flexible schema, JSON-like
  Key-Value (DynamoDB): Fast lookups, simple structure
  Wide-Column (Cassandra): Time-series, write-heavy
  Graph (Neo4j): Relationships, social networks

STRUCTURED vs UNSTRUCTURED:
  Structured: Tables, fixed schema, SQL (transactions, billing)
  Semi-structured: JSON, flexible schema (logs, events)
  Unstructured: Text, images, audio, video (needs feature extraction)
```

### Data Flow Modes

```
THREE WAYS DATA FLOWS THROUGH SYSTEMS:

1. DATA THROUGH DATABASES
   Producer writes to DB → Consumer reads from DB
   Pros: Simple, persistent
   Cons: Polling (consumer must check for changes)

2. DATA THROUGH SERVICES (REST/gRPC)
   Producer → API call → Consumer
   Pros: Real-time, request-response
   Cons: Tightly coupled, service must be up

3. DATA THROUGH REAL-TIME TRANSPORT
   Producer → Message queue (Kafka) → Consumer
   Pros: Decoupled, scalable, async
   Cons: Infrastructure complexity

BATCH vs STREAM PROCESSING:
  Batch: Process all data at once (nightly ETL)
    → High throughput, high latency (hours)
  Stream: Process each event as it arrives
    → Low latency (<1s), lower throughput per event
  Lambda: Both batch + stream (batch for accuracy, stream for speed)
  Kappa: Stream only (simpler, use replay for batch)
```

---

## Interview Q&As

### Q1: "What are the 4 requirements for ML systems?"

"Reliability — the system continues to work correctly even when things go wrong. Scalability — it handles increased load gracefully. Maintainability — different teams can collaborate. Adaptability — the system adapts to changing data distributions. The fourth requirement, adaptability, is unique to ML systems and doesn't exist in traditional software. This is because ML models degrade over time as data distributions shift."

### Q2: "How is ML in production different from ML in research?"

"Research optimizes for the best metric (accuracy, F1) on a static, clean dataset. Production optimizes for a trade-off between metrics, latency, and cost on dynamic, messy data. In research, failures mean restarting an experiment. In production, failures mean SLA breaches and lost revenue. Research is done by individuals; production requires cross-functional teams (data scientists, ML engineers, DevOps)."

### Q3: "Row-major vs column-major data formats — when would you use each?"

"Row-major (Avro, CSV) is better for write-heavy, transactional workloads because inserting a row is a single append. Column-major (Parquet, ORC) is better for read-heavy, analytical workloads because you can read just the columns you need without scanning entire rows. For ML data pipelines, I'd use Parquet for storing training data (read-heavy, columnar queries for feature selection) and Avro for streaming events (write-heavy, row-level)."

### Q4: "What is the difference between batch and stream processing?"

"Batch processing processes all data at once, typically on a schedule (nightly). It has high throughput but high latency (hours). Stream processing processes each event as it arrives, with sub-second latency but lower throughput per event. For ML, batch is used for model training (process millions of rows), and stream is used for real-time inference and monitoring (detect anomalies immediately). The Lambda architecture uses both: batch for accuracy, stream for speed."

### Q5: "When is ML NOT the right solution?"

"ML is not the right tool when the problem is simple enough for rules (if-then-else), when you don't have enough data, when the cost of being wrong is catastrophic (use deterministic rules instead), when explainability is required and ML is a black box, or when the ROI doesn't justify the infrastructure cost. Huyen's principle: start with the simplest solution that works, and only add ML complexity when rules don't scale."
