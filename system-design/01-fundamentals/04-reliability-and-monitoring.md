# Reliability & Monitoring: Keeping Systems Alive

> **The goal of this guide:** Understand how to protect systems from failure and
> overload (rate limiting, circuit breakers), monitor their health (metrics, logs,
> traces), define reliability targets (SLI/SLO/SLA), and recover from disasters.

---

## Table of Contents

1. [Rate Limiting](#1-rate-limiting)
2. [Circuit Breakers](#2-circuit-breakers)
3. [Health Checks & Heartbeats](#3-health-checks--heartbeats)
4. [The Three Pillars of Observability](#4-the-three-pillars-of-observability)
5. [SLI, SLO, SLA](#5-sli-slo-sla)
6. [Failover & Disaster Recovery](#6-failover--disaster-recovery)
7. [Interview Q&A](#7-interview-qa)

---

## 1. Rate Limiting

### Real-World Analogy: Hospital Emergency Room Triage 🏥

An ER has **limited beds and doctors**. If 500 patients arrive at once, the hospital
can't treat them all simultaneously. Triage nurses **control the flow**: critical
patients first, others may need to wait. Without this control, the ER would be
overwhelmed and **no one** would get care.

Rate limiting does the same for APIs: **control the flow of requests** to protect
the system from being overwhelmed.

### What Is Rate Limiting?

Rate limiting restricts the number of requests a client (or all clients) can make in
a given time window. It protects the system from:

- **Abuse/misuse** — bots, scrapers, DDoS attacks
- **Accidental overload** — a bug in a client causing request floods
- **Fairness** — one noisy client shouldn't starve others
- **Cost control** — each request costs money (compute, third-party APIs)

### Common Rate Limiting Algorithms

#### Token Bucket

```
   TOKEN BUCKET (capacity: 10 tokens, refill: 1 token/second):

   ┌───────────────────────────┐
   │  Bucket: [🌕🌕🌕🌕🌕🌕🌕] │  ← 7 tokens available
   └───────────────────────────┘

   Request arrives ──> consume 1 token ──> serve request (6 tokens left)
   Request arrives ──> consume 1 token ──> serve request (5 tokens left)
   ...
   Request arrives ──> 0 tokens! ──> REJECT (429 Too Many Requests)
   Wait 1 second ──> bucket refills 1 token ──> requests can resume

   ✅ Allows BURSTS (up to bucket capacity), then averages out over time
```

#### Leaky Bucket

```
   LEAKY BUCKET:

   Requests pour in ──> ┌───────────────┐ ──> Steady output (1 req/sec)
   (bursty)            │ [req][req]    │      (smoothed, never bursts)
   ──────────────────> │ [req][req]    │ ──────────────────────────>
                       │ [req]         │
                       └───────┬───────┘
                               │ leaks at constant rate
                               ▼

   ✅ Produces SMOOTH, steady output rate (no bursts allowed)
```

#### Fixed Window vs Sliding Window

```
   FIXED WINDOW (count per time block):
   ┌────────────┐┌────────────┐┌────────────┐
   │ 0–1 sec    ││ 1–2 sec    ││ 2–3 sec    │
   │ 5 reqs ✅  ││ 5 reqs ✅  ││ 5 reqs ✅  │
   └────────────┘└────────────┘└────────────┘
   Problem: A burst at the boundary (2.9s–3.1s) can send 10 reqs in 0.2s!

   SLIDING WINDOW (count in a rolling window):
   At time 2.5s: count requests from 1.5s to 2.5s (last 1 second)
   More accurate, no boundary bursts.
```

| Algorithm      | Allows Bursts? | Smooth Output? | Complexity |
|----------------|----------------|----------------|------------|
| Token Bucket   | ✅ Yes         | No             | Medium     |
| Leaky Bucket   | ❌ No          | ✅ Yes         | Medium     |
| Fixed Window   | Partial        | No             | Low        |
| Sliding Window | Configurable   | Better         | Higher     |

### Where to Rate Limit

```
   ┌──────┐    ┌──────────┐    ┌─────────────┐    ┌──────────┐
   │Client│ ─> │  CDN /   │ ─> │ API Gateway │ ─> │ Service  │
   └──────┘    │ Edge     │    │ (per-user)  │    │ (per-tenant)│
               └──────────┘    └─────────────┘    └──────────┘
               Layer 1:         Layer 2:            Layer 3:
               Global DDoS      Per-user limits     Per-tenant limits
```

> 💡 **Typical limits:** Anonymous: 100 req/hour. Free tier: 1,000 req/hour. Paid:
> 10,000 req/hour.

---

## 2. Circuit Breakers

### Real-World Analogy: Electrical Circuit Breaker ⚡

Your home has circuit breakers. If there's a **power surge** or short circuit, the
breaker **trips** and cuts power to that circuit — preventing a fire. You don't keep
pushing electricity through a faulty line. You fix the problem, then reset the
breaker.

In software, a circuit breaker stops your service from **repeatedly calling a failing
downstream service**, which would waste resources and cascade the failure.

### The Problem: Cascading Failures

```
   WITHOUT CIRCUIT BREAKER:

   Service A ──> Service B (is DOWN)
   Service A waits... 5s timeout... retry... 5s timeout... retry...
   Service A's threads are ALL stuck waiting for B.
   Service A runs out of resources ──> Service A ALSO crashes.
   Now Service C (which calls A) also fails ──> EVERYTHING DIES. 💀
```

### How a Circuit Breaker Works

The circuit breaker has **three states**:

```
                        ┌──────────────────────────────────────┐
                        │                                      │
                        ▼                                      │
              ┌─────────────────┐    N consecutive       ┌────┴───────┐
              │     CLOSED      │ ──── failures ───────> │    OPEN    │
              │  (normal: calls │                        │ (reject all│
              │   go through)   │ <─── success ────────  │  calls fast)│
              └─────────────────┘                        └────┬───────┘
                   ▲                                          │
                   │                                          │ after timeout
                   │                                          │ (try again)
                   │                                          ▼
                   │                                  ┌───────────────┐
                   └──────── success ───────────────  │  HALF-OPEN    │
                                                      │ (limited test │
                                                      │  requests)    │
                                                      └───────────────┘
```

#### CLOSED (Normal)
Requests flow normally. The breaker counts failures.
If failures exceed a threshold → switch to **OPEN**.

#### OPEN (Tripped)
**All requests fail immediately** — no call to the downstream service at all.
After a cooldown period → switch to **HALF-OPEN**.

#### HALF-OPEN (Testing)
Allow a **small number** of test requests through:
- If they succeed → the downstream recovered → switch to **CLOSED**
- If they fail → still broken → switch back to **OPEN**

### Benefits

| Benefit                     | Description                                    |
|-----------------------------|------------------------------------------------|
| **Fail fast**               | Don't waste time waiting for a dead service    |
| **Prevent cascading failure** | Stop the domino effect                       |
| **Auto-recovery**           | Automatically resumes when the downstream heals|
| **Resource protection**     | Free up threads/connections for healthy calls  |

### With a Fallback

```
   Service A ──call──> Service B (circuit OPEN)
   ──> Fallback: return cached/default data instead of failing
   ──> User sees slightly degraded but functional experience ✅
```

> Popular circuit breaker libraries: Hystrix (Netflix), Resilience4j, Polly (.NET).

---

## 3. Health Checks & Heartbeats

### Real-World Analogy: Hospital Vital Signs Monitor 🫀

In an ICU, patients are connected to monitors that continuously check heart rate,
blood pressure, oxygen. If vitals drop, an **alarm sounds** immediately — nurses
don't need to physically check every patient every minute.

### Health Checks

A health check is a periodic **"Are you OK?"** probe. Load balancers and orchestrators
use them to decide whether to route traffic to a service.

```
   LOAD BALANCER                         Service Instances
   ┌──────────┐     GET /health    ┌─────┴─────┐
   │          │ ──────────────────>│ Server A  │ ──> 200 OK ✅ (healthy)
   │          │ ──────────────────>│ Server B  │ ──> 500 ERR ❌ (remove!)
   │          │ ──────────────────>│ Server C  │ ──> 200 OK ✅ (healthy)
   └──────────┘                    └───────────┘
   Routes only to A and C, removes B from rotation
```

### Types of Health Checks

| Type            | What it checks                                | Example endpoint        |
|-----------------|-----------------------------------------------|-------------------------|
| **Liveness**    | Is the process running at all?                | `GET /health/live`      |
| **Readiness**   | Is it ready to serve traffic? (DB connected?) | `GET /health/ready`     |
| **Deep**        | Check all dependencies (DB, cache, downstream)| `GET /health/deep`     |

```
   LIVENESS:  "Am I alive?"     ──> If fails, RESTART me
   READINESS: "Am I ready?"     ──> If fails, STOP sending me traffic (but don't restart)
```

### Heartbeats

A heartbeat is the **reverse**: the service **proactively signals** "I'm alive" to a
coordinator (e.g., service registry, orchestrator). If heartbeats stop, the
coordinator assumes the service is dead.

```
   Service ──> "heartbeat 💓" ──> Coordinator    (every 5 seconds)

   If coordinator doesn't receive a heartbeat for 15 seconds:
   ──> Assume service is dead
   ──> Remove from service registry
   ──> Restart or replace it
```

| Concept       | Direction         | Purpose                              |
|---------------|-------------------|--------------------------------------|
| Health Check  | Coordinator → Svc | "Are you OK?" (pull)                |
| Heartbeat     | Service → Coord.  | "I'm alive!" (push)                 |

---

## 4. The Three Pillars of Observability

### Real-World Analogy: Hospital Patient Monitoring 🏥

To understand a patient's condition, a doctor uses three tools:
1. **Vital signs on the monitor** (heart rate, BP, temp) — **Metrics**
2. **Doctor's notes / patient interview** — **Logs**
3. **Tracing the symptoms over time** (when did fever start? what triggered it?) — **Traces**

Similarly, to understand a system's health, you need three types of data:

### The Three Pillars

```
   ┌──────────────────────────────────────────────────────────────┐
   │                THE THREE PILLARS                             │
   ├──────────────┬─────────────────┬─────────────────────────────┤
   │   METRICS    │      LOGS       │         TRACES              │
   ├──────────────┼─────────────────┼─────────────────────────────┤
   │ Numeric data │ Discrete events │ Request journey across svcs │
   │ over time    │ with timestamps │                              │
   ├──────────────┼─────────────────┼─────────────────────────────┤
   │ CPU: 72%     │ [ERROR] 2024... │ Request #1234:              │
   │ Req/s: 1500  │ DB connection   │  → Gateway (2ms)            │
   │ Latency:45ms │ failed for user │  → AuthService (5ms)        │
   │              │ 42 at 10:32 AM  │  → OrderService (30ms)      │
   │              │                 │    → DB query (25ms)        │
   │              │                 │  → Response (37ms total)    │
   ├──────────────┼─────────────────┼─────────────────────────────┤
   │ Prometheus   │ ELK, Loki       │ Jaeger, Zipkin, Datadog     │
   │ Grafana      │ Splunk          │                              │
   └──────────────┴─────────────────┴─────────────────────────────┘
```

### Metrics

**Aggregated, numeric** measurements over time. Cheap to store, great for dashboards
and alerting.

```
   Common metrics:
   ┌────────────────────┬───────────────────────────────────┐
   │ Metric             │ What it tells you                 │
   ├────────────────────┼───────────────────────────────────┤
   │ Request rate       │ Requests per second               │
   │ Error rate         │ % of requests returning errors    │
   │ Latency (p50,p99)  │ How slow are responses?           │
   │ CPU / Memory       │ Resource utilization              │
   │ Queue depth        │ How backed up is the work?        │
   └────────────────────┴───────────────────────────────────┘
```

> 💡 **Percentiles matter!** Average latency hides problems. p99 latency ("99% of
> requests complete within X ms") reveals the worst experience.

### Logs

**Discrete, timestamped event records**. Good for debugging specific failures.

```
   [2024-07-24 10:32:15] [INFO]  User 42 logged in from IP 1.2.3.4
   [2024-07-24 10:32:16] [INFO]  Order 101 created for user 42
   [2024-07-24 10:32:17] [ERROR] Payment failed: card declined (user 42, order 101)
   [2024-07-24 10:32:18] [WARN]  Retrying payment (attempt 2/3)
```

- **Structured logs** (JSON) are searchable and machine-parseable.
- Use **log levels**: DEBUG < INFO < WARN < ERROR < FATAL.
- Centralize logs so you can search across all services at once.

### Distributed Tracing

A trace follows a **single request** as it flows through multiple services, showing
exactly where time is spent.

```
   TRACE for Request #1234 (total: 137ms):

   [Gateway     ] ████████ (8ms)
   [Auth Service] ████████████████ (16ms)
   [Order Svc   ] ████████████████████████████████████████ (45ms)
      └─[DB Query] ██████████████████████████████ (28ms)
   [Payment Svc ] ██████████████████████████████ (35ms)
   [Response    ] ████ (3ms)

   ↑ The trace shows: DB Query in Order Svc is the bottleneck (28ms).
   Without tracing, you'd just see "137ms total" and not know WHERE.
```

> Popular tracing tools: Jaeger, Zipkin, Datadog APM, AWS X-Ray.

### Why You Need All Three

```
   METRICS  ──> "Is there a problem?"        (detection — dashboards/alerts)
   TRACES   ──> "WHERE is the problem?"       (localization — which service)
   LOGS     ──> "WHY is there a problem?"    (root cause — specific error)
```

---

## 5. SLI, SLO, SLA

### Real-World Analogy: Hospital Service Guarantees 🏥

- **SLI (Service Level Indicator):** The actual measured vitals — "patient heart rate
  is 72 bpm."
- **SLO (Service Level Objective):** The internal target — "we aim to keep heart rate
  between 60–100 bpm." This is what the medical team strives for.
- **SLA (Service Level Agreement):** The contract with the patient — "if we fail to
  keep your heart rate in range for 99.9% of the time, treatment is free." A formal
  promise with consequences.

### Definitions

| Term  | Full Name                   | What it is                          | Audience    |
|-------|-----------------------------|-------------------------------------|-------------|
| **SLI** | Service Level Indicator   | A **measured** metric               | Engineers   |
| **SLO** | Service Level Objective   | An **internal target** for the SLI  | The team    |
| **SLA** | Service Level Agreement   | An **external contract** (with penalties) | Customers   |

### Example

```
   SLI:  "Percentage of requests that return within 200ms"
         (measured: 99.94% last month)

   SLO:  "99.9% of requests must return within 200ms"
         (internal goal — if we miss, we prioritize fixing it)

   SLA:  "99.5% of requests will return within 200ms, or you get 10% refund"
         (external promise — always LOOSER than the SLO to leave safety margin)
```

### The Error Budget

Your SLO gives you an **error budget** — the amount of failure you're allowed.

```
   SLO: 99.9% availability over 30 days (43,200 minutes)

   Error budget = 0.1% × 43,200 = 43.2 minutes of allowed downtime per month

   ┌─────────────────────────────────────────────────┐
   │  ████████████████████░░░░░░░░  Used: 20 min      │
   │  Budget remaining: 23 min                        │
   │  ✅ Safe to deploy new features                  │
   └─────────────────────────────────────────────────┘

   If budget is exhausted ──> STOP new deploys, focus on reliability!
```

> 💡 **Key insight:** The error budget is a tool for balancing **speed** (ship new
> features) vs **stability** (don't break things). Out of budget = freeze features.

---

## 6. Failover & Disaster Recovery

### Real-World Analogy: Hospital Backup Generator 🏥⚡

When the power goes out, the hospital doesn't go dark. A **backup generator** kicks
in within seconds. Critical systems (ICU, surgery) stay powered. This is **failover**.

If the entire hospital building is damaged (fire, flood), patients are transferred to
a **backup facility**. This is **disaster recovery**.

### Failover

When a component fails, traffic is automatically redirected to a **standby**.

```
   ACTIVE-PASSIVE FAILOVER:

   Normal:                         After failure:
   ┌──────────┐                    ┌──────────┐     ┌──────────┐
   │ Primary  │ (active, serving)  │ Primary  │ ❌  │ Standby  │ ✅ (promoted!)
   │ 🟢       │                    │ DEAD     │     │ 🟢       │ (now active)
   └──────────┘                    └──────────┘     └──────────┘
   ┌──────────┐
   │ Standby  │ (passive, waiting)
   │ ⏸️       │
   └──────────┘
```

```
   ACTIVE-ACTIVE (no downtime):

   ┌──────────┐    ┌──────────┐
   │ Server A │    │ Server B │    Both serve traffic simultaneously
   │ 🟢 active│    │ 🟢 active│    If one dies, the other handles everything
   └──────────┘    └──────────┘
```

### Multi-AZ and Multi-Region

```
   SINGLE AZ (risky):
   ┌────────────────────────────┐
   │  Availability Zone 1       │
   │  ┌──────┐  ┌──────┐        │
   │  │App   │  │ DB   │        │  If AZ goes down ──> everything dies 💀
   │  └──────┘  └──────┘        │
   └────────────────────────────┘

   MULTI-AZ (safer):
   ┌──────────────────┐  ┌──────────────────┐
   │  AZ-1            │  │  AZ-2            │
   │  ┌──────┐ ┌────┐ │  │ ┌──────┐ ┌────┐ │
   │  │App   │ │DB  │ │  │ │App   │ │DB  │ │  If AZ-1 dies ──> AZ-2 takes over ✅
   │  │🟢    │ │⚪   │ │  │ │🟢    │ │⚪   │ │  (DB replicates across AZs)
   │  └──────┘ └────┘ │  │ └──────┘ └────┘ │
   └──────────────────┘  └──────────────────┘

   MULTI-REGION (safest):
   ┌──────────────────┐                  ┌──────────────────┐
   │  US-East Region  │  ── replicate ──>│  EU-West Region  │
   │  (primary)       │                  │  (standby/D R)   │
   │  Full stack      │                  │  Full stack      │
   └──────────────────┘                  └──────────────────┘
   If entire US-East region goes down ──> fail over to EU-West
```

### Disaster Recovery Metrics

| Metric | Meaning                                            | Analogy                          |
|--------|----------------------------------------------------|----------------------------------|
| **RTO** (Recovery Time Objective) | Max acceptable **downtime** after a disaster | "We must be back online in 4 hours" |
| **RPO** (Recovery Point Objective)| Max acceptable **data loss** (measured in time) | "We can afford to lose at most 1 hour of data" |

```
   RPO (data loss):    How often do you back up?
   ┌──────────────────────────────────────────────────────┐
   │  Backup every 1 hour ──> RPO = 1 hour                 │
   │  (Worst case: lose the last hour of data)             │
   │                                                      │
   │  Continuous replication ──> RPO ≈ 0 seconds           │
   │  (No data lost)                                      │
   └──────────────────────────────────────────────────────┘

   RTO (downtime):     How fast can you recover?
   ┌──────────────────────────────────────────────────────┐
   │  Restore from tape ──> RTO = 24 hours                 │
   │  Failover to hot standby ──> RTO = 5 minutes          │
   │  Active-active ──> RTO ≈ 0 seconds                    │
   └──────────────────────────────────────────────────────┘
```

---

## 7. Interview Q&A

### Q: What is rate limiting, and what algorithms do you know?

Rate limiting controls how many requests a client can make per time window to protect
the system. Common algorithms: **Token Bucket** (allows bursts, refills over time),
**Leaky Bucket** (smooths to a steady rate), **Fixed Window** (count per time block),
and **Sliding Window** (rolling count, more accurate). I'd implement it at the API
Gateway layer for per-user limits.

### Q: Explain the circuit breaker pattern.

A circuit breaker stops a service from repeatedly calling a failing downstream
service. It has three states: **CLOSED** (normal, requests flow), **OPEN** (fail
fast — reject all requests immediately without calling downstream), and **HALF-OPEN**
(test a few requests to see if downstream recovered). This prevents cascading failures
and allows automatic recovery. Often paired with a **fallback** (return cached data).

### Q: What's the difference between liveness and readiness probes?

**Liveness** probe checks if the process is alive — if it fails, the orchestrator
**restarts** the service. **Readiness** probe checks if the service is ready to serve
traffic (e.g., DB is connected) — if it fails, traffic is **stopped** but the service
isn't restarted. Liveness = "should I restart you?" Readiness = "should I send you
traffic?"

### Q: What are the three pillars of observability?

**Metrics** (numeric measurements over time — CPU, latency, error rate — great for
dashboards and alerting), **Logs** (discrete timestamped events — great for debugging
specific failures), and **Traces** (a single request's journey across services — great
for finding bottlenecks). Together: metrics tell you *if* there's a problem, traces
tell you *where*, logs tell you *why*.

### Q: What's the difference between SLI, SLO, and SLA?

**SLI** is the measured metric (e.g., "99.94% of requests under 200ms"). **SLO** is
the internal target (e.g., "we aim for 99.9%"). **SLA** is the external contract with
penalties (e.g., "we guarantee 99.5% or you get a refund"). The SLA is always looser
than the SLO to provide a safety margin.

### Q: What is an error budget?

If your SLO is 99.9% availability, your error budget is the remaining 0.1% — the
amount of downtime you're "allowed." Over a month, that's ~43 minutes. If you've used
up the budget, you freeze new feature deploys and focus on reliability. If you have
budget remaining, you can afford to ship riskier changes.

### Q: What is the difference between RTO and RPO?

**RTO** (Recovery Time Objective) is the maximum acceptable **downtime** — how fast
you must be back online. **RPO** (Recovery Point Objective) is the maximum acceptable
**data loss** — how much data you can afford to lose, measured in time. RTO is about
*time to recover*, RPO is about *how much data you lose*. Lower values require more
expensive solutions (continuous replication, active-active).

### Q: How do you prevent cascading failures in microservices?

1. **Circuit breakers** — fail fast when a downstream is failing
2. **Rate limiting** — protect services from overload
3. **Timeouts** — don't wait forever for a dead service
4. **Bulkheads** — isolate resources so one failure doesn't consume all threads
5. **Fallbacks** — return cached/default data instead of failing
6. **Async communication** — decouple with queues so services aren't blocked

### Q: How would you design a reliable notification system?

1. Use a **message queue** (e.g., SQS) so the system doesn't lose notifications if a
   service is down
2. **Retry** with exponential backoff for transient failures
3. **Dead letter queue** for messages that fail repeatedly (don't lose them)
4. **Circuit breaker** when the email/SMS provider is down
5. **Idempotency** — sending the same notification twice should be safe
6. Monitor queue depth, error rates, and delivery latency

---

## Quick Reference Cheat Sheet

```
┌──────────────────────────┬──────────────────────────────────────────────┐
│ Concept                  │ One-liner                                    │
├──────────────────────────┼──────────────────────────────────────────────┤
│ Rate Limiting            │ Control request flow to prevent overload     │
│ Token Bucket             │ Tokens refill over time; allows bursts       │
│ Circuit Breaker          │ Fail fast when downstream is failing         │
│ Liveness Probe           │ "Should I restart you?"                      │
│ Readiness Probe          │ "Should I send you traffic?"                 │
│ Metrics                  │ Numeric data over time (dashboards)          │
│ Logs                     │ Discrete events (debugging specific issues)  │
│ Traces                   │ Request journey across services              │
│ SLI / SLO / SLA          │ Measured / target / contract                 │
│ Error Budget             │ Allowed failure; spend it on new features    │
│ RTO                      │ Max acceptable downtime                      │
│ RPO                      │ Max acceptable data loss                     │
└──────────────────────────┴──────────────────────────────────────────────┘
```

---

**Previous:** [03 — Microservices & APIs](03-microservices-and-apis.md)
**Next:** [05 — Messaging & Streaming →](05-messaging-and-streaming.md)
