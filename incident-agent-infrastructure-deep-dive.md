# IncidentAgent Infrastructure Deep-Dive — How Every Tool Actually Works

> **Purpose:** The interviewer will drill into "How exactly did you use Redis? What data structures? What TTLs?" This guide gives you exact, technical, code-level answers for every infrastructure component.

---

## TABLE OF CONTENTS

1. [Redis — The Multi-Layer Cache (Detailed)](#1-redis)
2. [Kafka — The Event Backbone](#2-kafka)
3. [LLM Gateway — Model Routing Engine](#3-llm-gateway)
4. [AgentTrace — Observability Layer](#4-agenttrace)
5. [Neo4j — Network Topology Graph](#5-neo4j)
6. [Qdrant — Vector Database for RAG](#6-qdrant)
7. [Prometheus — Metrics Collection](#7-prometheus)
8. [ELK / Elasticsearch — Log Aggregation](#8-elk)
9. [ServiceNow — Ticket Integration](#9-servicenow)
10. [The Complete Request Flow (End-to-End)](#10-request-flow)
11. [Interview Q&A — Infrastructure Specifics](#11-interview-qa)

---

## 1. REDIS — THE MULTI-LAYER CACHE

### Why Redis?

```
PROBLEM: The agent calls 5-6 tools per investigation. Each tool queries
         a backend system (ELK, Prometheus, ServiceNow). These queries
         take 2-5 seconds each. For 1,000 investigations/day, that's
         5,000+ queries hitting backend systems.

         Many of these queries are REDUNDANT:
         - Network topology barely changes (maybe once a week)
         - Runbooks are static (updated monthly)
         - The same metric might be queried 3 times in 10 minutes
           by different investigations on the same incident

SOLUTION: Redis cache. Store tool results in Redis with appropriate TTLs.
          Subsequent calls for the same data return instantly from cache
          instead of querying the backend again.

IMPACT:  60% of tool calls hit cache → 60% less load on backends
         Cache hit latency: <1ms (vs 2-5 sec for backend queries)
```

### How Redis Is Actually Used — Three Separate Use Cases

```
┌─────────────────────────────────────────────────────────────────┐
│                  REDIS USAGE IN INCIDENTAGENT                    │
│                                                                 │
│  USE CASE 1: Tool Result Cache (TTL-based)                      │
│  ─────────────────────────────────────────────────────           │
│  Cache tool query results so repeated calls return instantly.   │
│  Key: "tool:{tool_name}:{hashed_args}"                         │
│  Val: JSON-serialized tool result                                │
│  TTL: Varies per tool (see below)                                │
│                                                                 │
│  USE CASE 2: Error Rate Limiter (Sliding Window)                │
│  ─────────────────────────────────────────────────────           │
│  Track tool failure rates. If a tool is failing repeatedly,     │
│  circuit-break it instead of hammering a dead backend.          │
│  Key: "errors:{tool_name}:{minute_bucket}"                      │
│  Val: Integer (count of failures in that minute)                │
│  TTL: 300 seconds (5 minutes of history)                        │
│                                                                 │
│  USE CASE 3: Active Investigation State                         │
│  ─────────────────────────────────────────────────────           │
│  Track investigations in progress. Used for:                    │
│  - Deduplication (don't investigate same incident twice)        │
│  - Rate limiting (max 5 concurrent per pod)                     │
│  Key: "active_investigations:{incident_signature}"              │
│  Val: JSON {investigation_id, pod_id, started_at}               │
│  TTL: 300 seconds (if pod crashes, stale lock expires)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Use Case 1: Tool Result Cache — The Core Usage

#### TTL Strategy Per Tool (Memorize This Table)

```
┌─────────────────────┬──────────────┬──────────────────────────────┐
│ Tool                │ TTL          │ Why This TTL?                │
├─────────────────────┼──────────────┼──────────────────────────────┤
│ query_logs          │ 60 seconds   │ Logs change every second.    │
│                     │              │ But during an active incident,│
│                     │              │ the same 60-sec window is    │
│                     │              │ queried repeatedly. Cache    │
│                     │              │ prevents re-querying ELK for │
│                     │              │ the same time window.        │
├─────────────────────┼──────────────┼──────────────────────────────┤
│ search_metrics      │ 120 seconds  │ Metrics update every 10-60s. │
│                     │              │ 2-min cache is fresh enough   │
│                     │              │ for correlation. If agent    │
│                     │              │ needs real-time, it can      │
│                     │              │ bypass cache with force flag.│
├─────────────────────┼──────────────┼──────────────────────────────┤
│ query_tickets       │ 3600 seconds │ Past incidents don't change. │
│                     │ (1 hour)     │ Safe to cache for an hour.   │
├─────────────────────┼──────────────┼──────────────────────────────┤
│ search_kb           │ 86400 sec    │ Runbooks are updated         │
│                     │ (24 hours)   │ maybe once a month. Cache    │
│                     │              │ for a full day.              │
├─────────────────────┼──────────────┼──────────────────────────────┤
│ get_topology        │ 3600 seconds │ Network topology changes     │
│                     │ (1 hour)     │ infrequently (new deploy,    │
│                     │              │ config change). 1-hr cache   │
│                     │              │ is safe.                     │
├─────────────────────┼──────────────┼──────────────────────────────┤
│ escalate_human      │ NO CACHE     │ Every escalation is unique.  │
│                     │              │ Never cache action tools.    │
└─────────────────────┴──────────────┴──────────────────────────────┘
```

#### The Caching Code

```python
import hashlib
import json
import redis
from datetime import timedelta

class ToolCache:
    """
    Redis-based cache for tool results.

    DESIGN DECISIONS:
    1. Cache key = hash of (tool_name + sorted_args) → deterministic
    2. TTL varies per tool (see TTL_CONFIG below)
    3. Optional force_refresh flag to bypass cache
    4. Cache stores COMPRESSED results (not raw) to save Redis memory
    5. Cache hits tracked for observability (cache hit ratio metric)
    """

    # TTL configuration per tool (in seconds)
    TTL_CONFIG = {
        "query_logs": 60,        # 1 minute
        "search_metrics": 120,   # 2 minutes
        "query_tickets": 3600,   # 1 hour
        "search_kb": 86400,      # 24 hours
        "get_topology": 3600,    # 1 hour
        # escalate_human: not cached (no entry = infinite TTL = never cached)
    }

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.hits = 0
        self.misses = 0

    def _make_key(self, tool_name: str, args: dict) -> str:
        """
        Create a deterministic cache key.

        Example:
          tool_name = "query_logs"
          args = {"service": "payment-svc", "time_range": "last_30_minutes"}

          key = "tool:query_logs:a3f7b2c1d4e5..."
        """
        # Sort args to ensure same args always produce same key
        # (dict ordering is insertion-order in Python 3.7+, so we sort)
        args_str = json.dumps(args, sort_keys=True)
        args_hash = hashlib.sha256(args_str.encode()).hexdigest()[:16]
        return f"tool:{tool_name}:{args_hash}"

    def get(self, tool_name: str, args: dict, force_refresh: bool = False):
        """
        Try to get a cached result. Returns (result, cache_hit_bool).
        """
        if force_refresh or tool_name not in self.TTL_CONFIG:
            self.misses += 1
            return None, False

        key = self._make_key(tool_name, args)
        cached = self.redis.get(key)

        if cached is not None:
            self.hits += 1
            return json.loads(cached), True

        self.misses += 1
        return None, False

    def set(self, tool_name: str, args: dict, result: dict):
        """
        Store a result in cache with the tool's configured TTL.
        """
        if tool_name not in self.TTL_CONFIG:
            return  # Don't cache this tool

        key = self._make_key(tool_name, args)
        ttl = self.TTL_CONFIG[tool_name]

        # Store as compressed JSON to save Redis memory
        result_str = json.dumps(result, separators=(',', ':'))  # Compact JSON
        self.redis.setex(key, ttl, result_str)

    def invalidate(self, tool_name: str, args: dict):
        """
        Manually invalidate a cache entry.
        Used when we KNOW the underlying data changed.
        """
        key = self._make_key(tool_name, args)
        self.redis.delete(key)

    def get_hit_ratio(self) -> float:
        """Cache effectiveness metric for monitoring."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
```

#### How It Integrates with the Agent Loop

```python
class IncidentAgent:

    def execute_tool(self, tool_name, args, force_refresh=False):
        """
        Execute a tool call WITH caching.

        Flow:
        1. Check Redis cache → if hit, return cached result (<1ms)
        2. If miss, call the actual backend (2-5 sec)
        3. Store result in cache with appropriate TTL
        4. Return result
        """
        # STEP 1: Check cache
        cached_result, was_cached = self.cache.get(
            tool_name, args, force_refresh=force_refresh
        )

        if was_cached:
            self.tracer.log("cache_hit", tool_name, args)
            return cached_result

        # STEP 2: Cache miss → execute actual tool
        self.tracer.log("cache_miss", tool_name, args)

        try:
            result = self.tools[tool_name](**args)

            # STEP 3: Store in cache (only if result is not an error)
            if result and "error" not in result:
                self.cache.set(tool_name, args, result)

            return result

        except Exception as e:
            # Don't cache errors — next call should retry
            return {"error": str(e)}
```

#### Real Example of Cache Impact

```
SCENARIO: Three incidents fire simultaneously, all related to the same
          database (db-prod-01):

Incident A: "payment-svc error rate 15%"
Incident B: "order-svc error rate 22%"
Incident C: "inventory-svc timeout errors"

WITHOUT CACHE:
  Agent A calls get_topology("db-prod-01") → 3.2 sec → Neo4j
  Agent B calls get_topology("db-prod-01") → 3.1 sec → Neo4j (same query!)
  Agent C calls get_topology("db-prod-01") → 3.4 sec → Neo4j (same query!)
  Total backend queries: 3
  Total time: ~10 sec

WITH CACHE:
  Agent A calls get_topology("db-prod-01") → 3.2 sec → Neo4j → cached
  Agent B calls get_topology("db-prod-01") → 0.8 ms → CACHE HIT
  Agent C calls get_topology("db-prod-01") → 0.9 ms → CACHE HIT
  Total backend queries: 1 (instead of 3)
  Total time: ~3.2 sec (67% faster)

"When 3 incidents share the same root cause (database failure), caching
 prevents redundant backend queries. This is critical during major
 outages where many alerts fire simultaneously."
```

### Use Case 2: Circuit Breaker with Redis

```python
class CircuitBreaker:
    """
    Use Redis to track tool failure rates and circuit-break failing tools.

    WHY: If ELK is down, every query_logs call will timeout after 30 sec.
         Without a circuit breaker, 10 iterations × 30 sec = 5 minutes wasted.
         With circuit breaker, after 3 failures, we STOP calling ELK and
         tell the agent to try a different tool.

    HOW: Redis sorted set tracks failures per tool per minute.
         If failure count exceeds threshold, circuit opens.
    """

    FAILURE_THRESHOLD = 3       # Open circuit after 3 failures in window
    RECOVERY_TIMEOUT = 60       # Try again after 60 seconds
    WINDOW_SECONDS = 120        # 2-minute sliding window

    def __init__(self, redis_client):
        self.redis = redis_client

    def is_open(self, tool_name: str) -> bool:
        """Check if circuit breaker is OPEN (tool should not be called)."""
        key = f"circuit:{tool_name}"

        # Check if circuit was explicitly opened
        state = self.redis.hget(key, "state")
        if state == "open":
            # Check if recovery timeout has elapsed
            opened_at = float(self.redis.hget(key, "opened_at") or 0)
            if time.time() - opened_at > self.RECOVERY_TIMEOUT:
                # Half-open: allow one test call
                self.redis.hset(key, "state", "half-open")
                return False
            return True  # Circuit still open
        return False

    def record_success(self, tool_name: str):
        """Record a successful tool call → close circuit."""
        key = f"circuit:{tool_name}"
        self.redis.hset(key, "state", "closed")
        self.redis.hset(key, "failure_count", 0)

    def record_failure(self, tool_name: str):
        """Record a failed tool call → maybe open circuit."""
        key = f"circuit:{tool_name}"
        failure_count = int(self.redis.hincrby(key, "failure_count", 1))

        if failure_count >= self.FAILURE_THRESHOLD:
            self.redis.hset(key, "state", "open")
            self.redis.hset(key, "opened_at", time.time())
            self.redis.expire(key, self.WINDOW_SECONDS)


# INTEGRATION WITH AGENT LOOP:
def execute_tool(self, tool_name, args):
    # Check circuit breaker FIRST
    if self.circuit_breaker.is_open(tool_name):
        return {
            "error": f"Tool '{tool_name}' is circuit-broken "
                     f"(backend appears down). Try a different tool."
        }

    try:
        result = self.tools[tool_name](**args)
        self.circuit_breaker.record_success(tool_name)
        return result
    except Exception as e:
        self.circuit_breaker.record_failure(tool_name)
        return {"error": str(e)}
```

### Use Case 3: Deduplication Lock

```python
class InvestigationLock:
    """
    Prevent duplicate investigations for the same incident.

    WHEN: PagerDuty sends 5 alerts for the same underlying issue.
          Without dedup, 5 agents investigate the same thing → 5× cost.

    HOW: Redis SETNX (set-if-not-exists) as a distributed lock.
    """

    LOCK_TTL = 300  # 5 minutes (if agent crashes, lock auto-expires)

    def __init__(self, redis_client):
        self.redis = redis_client

    def try_acquire(self, incident_signature: str) -> bool:
        """
        Try to acquire investigation lock.

        incident_signature: hash of (service + alarm_type + time_window)
        Returns True if this agent should investigate, False if another
        agent is already on it.
        """
        key = f"investigation_lock:{incident_signature}"

        # SETNX = Set if Not eXists (atomic operation)
        # Returns 1 if set succeeded (we got the lock), 0 if already exists
        acquired = self.redis.setnx(key, json.dumps({
            "pod_id": os.environ.get("POD_NAME", "unknown"),
            "started_at": time.time()
        }))

        if acquired:
            # Set TTL so lock auto-expires if pod crashes
            self.redis.expire(key, self.LOCK_TTL)
            return True

        # Another agent is already investigating this
        return False

    def release(self, incident_signature: str):
        """Release the lock when investigation completes."""
        key = f"investigation_lock:{incident_signature}"
        self.redis.delete(key)


# USAGE IN AGENT:
def investigate(self, incident_description):
    signature = self._compute_signature(incident_description)

    if not self.lock.try_acquire(signature):
        self.tracer.log("duplicate_incident_skipped", signature)
        return InvestigationResult(
            status=InvestigationStatus.SKIPPED,
            root_cause="Duplicate incident — another agent is investigating"
        )

    try:
        result = self._run_investigation(incident_description)
        return result
    finally:
        self.lock.release(signature)  # Always release
```

### Redis Configuration

```python
# Redis connection pool configuration
import redis

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis-cluster"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    db=0,
    max_connections=50,         # Connection pool size
    socket_timeout=2,           # 2 sec timeout (Redis should be fast)
    socket_connect_timeout=2,
    retry_on_timeout=True,
    retry_on_error=[redis.ConnectionError, redis.TimeoutError],
    health_check_interval=30,   # Check connection health every 30s
    decode_responses=True,      # Auto-decode bytes to str
)

# Redis Cluster (for HA in production):
# 3 master nodes + 3 replica nodes
# Failover: If a master dies, replica promotes automatically
# Memory: 50GB total (tool results are small, ~1KB each)
# Eviction: allkeys-lru (evict least recently used when memory full)
```

---

## 2. KAFKA — THE EVENT BACKBONE

### Why Kafka?

```
PROBLEM: During a major outage, 500+ alerts fire in 2 minutes.
         If each alert directly triggers an agent:
         - 500 concurrent LLM API calls → API rate limits hit
         - 500 concurrent tool queries → ELK/Prometheus overloaded
         - Agent pods overwhelmed → OOM crashes

         We need a BUFFER that smooths out the spike.

SOLUTION: Kafka queue. Alerts go into a Kafka topic. Agent pods
         consume at their own pace. Spikes get buffered.

KAFKA ACTS AS:
  1. Buffer: Absorbs alert spikes (500 alerts queue up, agents process 10 at a time)
  2. Decoupler: Alert producers don't know about agents (and vice versa)
  3. Replay: If an investigation fails, we can re-process the message
  4. Ordering: Incidents from the same service are processed in order
```

### Kafka Topic Design

```
TOPIC: incident-alerts
  Partitions: 12 (allows 12 concurrent consumers)
  Replication: 3 (each partition replicated to 3 brokers for HA)
  Retention: 7 days (can replay failed investigations)

PARTITIONING STRATEGY:
  Key by service name → all alerts for "payment-svc" go to same partition
  → processed in order by same consumer
  → prevents race conditions if two alerts for same service fire simultaneously

  partition = hash(service_name) % 12

CONSUMER GROUP: incident-agent-group
  12 consumers (one per partition)
  Each consumer pod runs 1 consumer thread
  Auto-scaling: If lag grows, Kubernetes spins up more pods
```

### Kafka Producer (Alert Ingestion)

```python
from kafka import KafkaProducer
import json

class AlertProducer:
    """Pushes incoming alerts to Kafka."""

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=os.environ.get("KAFKA_BROKERS", "kafka:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",              # Wait for all replicas (strongest durability)
            retries=3,               # Retry on transient failures
            linger_ms=10,            # Batch messages for 10ms (throughput)
            compression_type="lz4",  # Compress for network efficiency
            max_in_flight_requests_per_connection=5,
        )

    def publish_alert(self, alert: dict):
        """
        Publish an alert to Kafka.

        Alert format from PagerDuty webhook:
        {
            "incident_id": "INC-2024-7891",
            "service": "payment-svc",
            "severity": "critical",
            "description": "Error rate > 15%",
            "fired_at": "2024-07-24T10:15:00Z",
            "metadata": {"tower_id": None, "region": "west"}
        }
        """
        # Key = service name → ensures ordering per service
        key = alert.get("service", "unknown")

        self.producer.send(
            topic="incident-alerts",
            key=key,
            value=alert,
        )
        self.producer.flush(timeout=5)
```

### Kafka Consumer (Agent Trigger)

```python
from kafka import KafkaConsumer
import json

class IncidentConsumer:
    """Consumes alerts from Kafka and triggers investigations."""

    def __init__(self, agent: IncidentAgent):
        self.consumer = KafkaConsumer(
            "incident-alerts",
            bootstrap_servers=os.environ.get("KAFKA_BROKERS", "kafka:9092"),
            group_id="incident-agent-group",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            auto_offset_reset="latest",      # Only process new alerts
            enable_auto_commit=False,         # Manual commit (at-least-once)
            max_poll_records=5,               # Process 5 at a time max
            session_timeout_ms=30000,         # 30s heartbeat timeout
            consumer_timeout_ms=1000,         # Non-blocking poll
        )
        self.agent = agent

    def run(self):
        """Main consumer loop. Runs in each Kubernetes pod."""
        print("Incident consumer started. Waiting for alerts...")

        for message in self.consumer:
            alert = message.value
            print(f"Received alert: {alert['incident_id']} "
                  f"for service: {alert['service']}")

            try:
                # Run the investigation
                result = self.agent.investigate(
                    alert["description"],
                    incident_id=alert["incident_id"],
                    metadata=alert.get("metadata", {})
                )

                # Deliver result to SRE team
                self._deliver_result(result)

                # Commit offset ONLY after successful processing
                # (If we crash before commit, Kafka redelivers)
                self.consumer.commit()

            except Exception as e:
                print(f"Investigation failed: {e}")
                # Don't commit → Kafka will redeliver this message
                # After 3 retries, message goes to Dead Letter Queue
                self._handle_failure(alert, e)

    def _deliver_result(self, result: InvestigationResult):
        """Send investigation report to the right place."""
        if result.status == InvestigationStatus.COMPLETED:
            # Post to Slack #incident-response
            self.slack.post(
                channel="#incident-response",
                text=self._format_report(result)
            )
            # Create ServiceNow ticket with the report
            self.servicenow.create_ticket(
                short_description=result.root_cause,
                description=json.dumps(result.evidence, indent=2),
                priority=self._severity_from_confidence(result.confidence_score),
            )
        elif result.status == InvestigationStatus.ESCALATED:
            # Page on-call engineer via PagerDuty
            self.pagerduty.page(
                urgency="high",
                description=f"Agent escalated: {result.root_cause}",
                details=result.full_trace,
            )
```

### Dead Letter Queue (DLQ)

```python
"""
If an investigation fails 3 times, the Kafka message goes to a DLQ.

TOPIC: incident-alerts-dlq

This prevents poison-pill messages from blocking the main queue.
Ops team monitors the DLQ and investigates manually.
"""

MAX_RETRIES = 3

def _handle_failure(self, alert, error):
    retry_key = f"retries:{alert['incident_id']}"
    retry_count = self.redis.incr(retry_key)
    self.redis.expire(retry_key, 3600)  # Reset after 1 hour

    if retry_count >= MAX_RETRIES:
        # Send to DLQ
        self.dlq_producer.send(
            topic="incident-alerts-dlq",
            key=alert.get("service"),
            value={**alert, "error": str(error), "retries": retry_count},
        )
        self.slack.post(
            channel="#ops-alerts",
            text=f"🚨 Incident {alert['incident_id']} failed after "
                 f"{retry_count} retries. Moved to DLQ. Error: {error}"
        )
    # If retries < MAX, don't commit → Kafka redelivers
```

---

## 3. LLM GATEWAY — MODEL ROUTING ENGINE

### What It Is

```python
"""
The LLM Gateway (CostLens) sits between the agent and the LLM providers.
It routes requests to the cheapest model that can handle the task,
tracks costs, and handles failover.

WHY: The agent makes 5-10 LLM calls per investigation. If all go to
     GPT-4o ($2.50/1M tokens), each investigation costs $0.35.
     With routing (simple steps → GPT-4o-mini at $0.15/1M), cost drops
     to $0.08. That's 77% savings.
"""

class LLMGateway:
    """Multi-model routing gateway with cost tracking and failover."""

    # Model pricing (per 1M tokens)
    PRICING = {
        "gpt-4o":              {"input": 2.50, "output": 10.00},
        "gpt-4o-mini":         {"input": 0.15, "output": 0.60},
        "claude-3.5-sonnet":   {"input": 3.00, "output": 15.00},
        "llama-3.1-8b-local":  {"input": 0.00, "output": 0.00},  # Self-hosted
    }

    # Fallback chain: if primary fails, try next
    FALLBACK_CHAIN = [
        "gpt-4o",
        "gpt-4o-mini",
        "llama-3.1-8b-local",  # Last resort: self-hosted
    ]

    def __init__(self):
        self.total_cost = 0.0
        self.total_tokens = 0
        self.call_log = []

    def call(self, messages, model="auto", tools=None, **kwargs):
        """
        Call LLM with automatic model routing.

        model="auto": Gateway decides based on task complexity
        model="gpt-4o-mini": Force specific model
        """
        if model == "auto":
            model = self._classify_and_route(messages, tools)

        # Try primary model, fall back on failure
        for model_name in self._get_fallback_chain(model):
            try:
                response = self._call_provider(model_name, messages, tools, **kwargs)
                self._track_cost(model_name, response.usage)
                return response
            except (RateLimitError, ServiceUnavailableError) as e:
                print(f"Model {model_name} failed: {e}. Trying fallback...")
                continue

        raise AllModelsFailedError("All models in fallback chain failed")

    def _classify_and_route(self, messages, tools):
        """
        Decide which model to use based on the request.

        SIMPLE tasks → GPT-4o-mini (cheap):
          - "Which tool should I call?" (just needs to pick from list)
          - "Summarize this text" (compression task)
          - Simple classification

        COMPLEX tasks → GPT-4o (expensive):
          - "Correlate logs + metrics + tickets to find root cause"
          - "Generate diagnostic report with evidence"
          - Multi-step reasoning
        """
        last_message = messages[-1].get("content", "")

        # Heuristic classification (FREE — no LLM call needed)
        if len(last_message) < 500 and ("tool" in last_message.lower()
                                         or "summarize" in last_message.lower()):
            return "gpt-4o-mini"

        # Check if this is a tool-decision step (simple)
        if tools and "tool_calls" not in str(messages[-3:]):
            return "gpt-4o-mini"  # Just deciding which tool to call

        # Complex reasoning → GPT-4o
        return "gpt-4o"

    def _track_cost(self, model, usage):
        """Track token usage and cost per call."""
        input_cost = (usage.prompt_tokens / 1_000_000) * self.PRICING[model]["input"]
        output_cost = (usage.completion_tokens / 1_000_000) * self.PRICING[model]["output"]
        call_cost = input_cost + output_cost

        self.total_cost += call_cost
        self.total_tokens += usage.total_tokens

        self.call_log.append({
            "model": model,
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "cost_usd": call_cost,
            "timestamp": time.time(),
        })
```

---

## 4. AGENTTRACE — OBSERVABILITY LAYER

### What It Captures

```python
"""
AgentTrace records EVERY step of the investigation for debugging
and auditing. Like OpenTelemetry but for AI agents.

WHY: Without traces, when the agent gives a wrong diagnosis, you have
     NO IDEA what went wrong. Did it call the wrong tool? Did it
     misinterpret a result? Did the LLM hallucinate?

     With traces, you can replay the exact decision sequence and
     find the bug in 10 minutes instead of 2 hours.
"""

class AgentTracer:
    """Records full execution trace of agent investigations."""

    def __init__(self):
        self.traces = {}  # incident_id → list of events

    def log_start(self, incident_id, description):
        self._add_event(incident_id, {
            "type": "investigation_started",
            "description": description,
            "timestamp": time.time(),
        })

    def log_iteration(self, incident_id, iteration_num):
        self._add_event(incident_id, {
            "type": "iteration_start",
            "iteration": iteration_num,
            "timestamp": time.time(),
        })

    def log_llm_call(self, incident_id, iteration, response):
        self._add_event(incident_id, {
            "type": "llm_call",
            "iteration": iteration,
            "model": response.model,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "cost_usd": response.usage.total_tokens * 0.000002,  # Approx
            "tool_calls_requested": [tc.function.name for tc in
                                     (response.choices[0].message.tool_calls or [])],
            "timestamp": time.time(),
        })

    def log_tool_call(self, incident_id, tool_name, args):
        self._add_event(incident_id, {
            "type": "tool_call",
            "tool": tool_name,
            "arguments": args,
            "timestamp": time.time(),
        })

    def log_tool_result(self, incident_id, tool_name, result):
        # Truncate large results for storage
        result_str = json.dumps(result)
        self._add_event(incident_id, {
            "type": "tool_result",
            "tool": tool_name,
            "result_size_bytes": len(result_str),
            "result_preview": result_str[:500],  # Store preview only
            "success": "error" not in result if isinstance(result, dict) else True,
            "timestamp": time.time(),
        })

    def log_cache_hit(self, incident_id, tool_name):
        self._add_event(incident_id, {
            "type": "cache_hit",
            "tool": tool_name,
            "timestamp": time.time(),
        })

    def log_error(self, incident_id, tool_name, error):
        self._add_event(incident_id, {
            "type": "tool_error",
            "tool": tool_name,
            "error": str(error),
            "timestamp": time.time(),
        })

    def log_final_report(self, incident_id, report):
        self._add_event(incident_id, {
            "type": "final_report",
            "report": report,
            "timestamp": time.time(),
        })

    def get_trace(self, incident_id) -> list:
        """Get full trace for debugging/auditing."""
        return self.traces.get(incident_id, [])

    def _add_event(self, incident_id, event):
        if incident_id not in self.traces:
            self.traces[incident_id] = []
        self.traces[incident_id].append(event)
```

### What a Trace Looks Like

```json
[
  {"type": "investigation_started", "description": "Payment error rate 15%"},
  {"type": "iteration_start", "iteration": 1},
  {"type": "llm_call", "model": "gpt-4o-mini", "input_tokens": 2100, "output_tokens": 45,
   "tool_calls_requested": ["query_logs"]},
  {"type": "tool_call", "tool": "query_logs", "arguments": {"service": "payment-svc"}},
  {"type": "cache_miss"},
  {"type": "tool_result", "tool": "query_logs", "result_size_bytes": 152000, "success": true},
  {"type": "iteration_start", "iteration": 2},
  {"type": "llm_call", "model": "gpt-4o-mini", "input_tokens": 2480, "output_tokens": 38,
   "tool_calls_requested": ["search_metrics"]},
  {"type": "tool_call", "tool": "search_metrics", "arguments": {"service": "payment-svc",
   "metric_name": "db_connection_pool_usage"}},
  {"type": "cache_miss"},
  {"type": "tool_result", "tool": "search_metrics", "result_size_bytes": 8200, "success": true},
  {"type": "iteration_start", "iteration": 3},
  {"type": "llm_call", "model": "gpt-4o", "input_tokens": 2820, "output_tokens": 52,
   "tool_calls_requested": ["query_tickets"]},
  {"type": "tool_call", "tool": "query_tickets", "arguments": {"search_query": "DB pool payment"}},
  {"type": "cache_miss"},
  {"type": "tool_result", "tool": "query_tickets", "result_size_bytes": 24000, "success": true},
  {"type": "iteration_start", "iteration": 4},
  {"type": "llm_call", "model": "gpt-4o", "input_tokens": 3450, "output_tokens": 48,
   "tool_calls_requested": ["search_kb"]},
  {"type": "tool_call", "tool": "search_kb", "arguments": {"query": "DB pool remediation"}},
  {"type": "cache_hit"},
  {"type": "tool_result", "tool": "search_kb", "result_size_bytes": 8600, "success": true},
  {"type": "iteration_start", "iteration": 5},
  {"type": "llm_call", "model": "gpt-4o", "input_tokens": 4200, "output_tokens": 380,
   "tool_calls_requested": []},
  {"type": "final_report", "report": {"root_cause": "DB pool exhaustion",
   "confidence": 0.87}}
]
```

---

## 5. NEO4J — NETWORK TOPOLOGY GRAPH

### What's Stored

```python
"""
Neo4j stores the network topology as a graph.

Nodes: services, databases, servers, cell towers, routers, switches
Edges: depends_on, hosts, connects_to, routes_through, managed_by

This lets the agent answer questions like:
  "What services depend on the failing database?"
  "Is the backhaul fiber route shared with other towers?"
  "What's the blast radius of this failure?"
"""

# CYPHER QUERIES USED BY get_topology TOOL:

# Query 1: Get all dependencies of a node (1-3 hops)
GET_DEPENDENCIES = """
MATCH path = (n {id: $node_id})-[:DEPENDS_ON*1..3]->(dependency)
RETURN n.id AS node, dependency.id AS depends_on,
       dependency.type AS type, dependency.status AS status
LIMIT 50
"""

# Query 2: Get reverse dependencies (who depends on THIS node?)
# "If this DB goes down, what services are affected?"
GET_REVERSE_DEPS = """
MATCH (dependent)-[:DEPENDS_ON]->(n {id: $node_id})
RETURN dependent.id AS affected_service, dependent.type AS type
LIMIT 50
"""

# Query 3: Get all cell towers sharing a backhaul
GET_SHARED_BACKHAUL = """
MATCH (tower:CellTower {id: $tower_id})-[:ROUTES_THROUGH]->(backhaul),
      (other:CellTower)-[:ROUTES_THROUGH]->(same_backhaul)
WHERE backhaul = same_backhaul AND other.id <> $tower_id
RETURN other.id AS shared_tower, backhaul.id AS backhaul
"""
```

### How get_topology Tool Uses Neo4j

```python
from neo4j import GraphDatabase

class TopologyTool:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://neo4j:7687",
            auth=("neo4j", os.environ.get("NEO4J_PASSWORD")),
        )

    def get_topology(self, node_id: str) -> dict:
        """Get topology and dependencies for a network node."""
        with self.driver.session() as session:
            # Get forward dependencies (what this node depends on)
            deps = session.run(GET_DEPENDENCIES, node_id=node_id)
            dependencies = [{
                "node": r["depends_on"],
                "type": r["type"],
                "status": r["status"]
            } for r in deps]

            # Get reverse dependencies (who depends on this node)
            affected = session.run(GET_REVERSE_DEPS, node_id=node_id)
            affected_services = [{
                "service": r["affected_service"],
                "type": r["type"]
            } for r in affected]

        return {
            "node": node_id,
            "depends_on": dependencies,
            "affected_services": affected_services,  # Blast radius
            "summary": f"{node_id} has {len(dependencies)} dependencies "
                       f"and {len(affected_services)} dependent services"
        }
```

### Real Query Result

```
INPUT: get_topology("payment-svc")

NEO4J RETURNS:
{
  "node": "payment-svc",
  "depends_on": [
    {"node": "db-prod-01", "type": "postgresql", "status": "degraded"},
    {"node": "redis-cache-01", "type": "redis", "status": "healthy"},
    {"node": "auth-gw", "type": "service", "status": "healthy"},
    {"node": "kafka-broker-01", "type": "kafka", "status": "healthy"}
  ],
  "affected_services": [
    {"service": "checkout-svc", "type": "microservice"},
    {"service": "billing-svc", "type": "microservice"},
    {"service": "mobile-app-api", "type": "api_gateway"}
  ],
  "summary": "payment-svc has 4 dependencies and 3 dependent services"
}

COMPRESSED FOR AGENT CONTEXT:
  Topology for payment-svc:
  Depends on: db-prod-01 (postgresql, DEGRADED ⚠️),
              redis-cache-01 (healthy ✓), auth-gw (healthy ✓)
  Blast radius: 3 services affected (checkout-svc, billing-svc, mobile-app-api)
```

---

## 6. QDRANT — VECTOR DATABASE FOR RAG

### How search_kb Uses Qdrant + Neo4j Together

```python
"""
The search_kb tool does HYBRID search:

1. VECTOR SEARCH (Qdrant): Find text chunks semantically similar to query
2. GRAPH SEARCH (Neo4j): Find entity relationships mentioned in query
3. MERGE: Combine both into context for the LLM

This is GraphRAG — the combination that improved accuracy from 79% to 91%.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class KnowledgeBaseTool:
    def __init__(self):
        self.qdrant = QdrantClient(host="qdrant", port=6333)
        self.neo4j = GraphDatabase.driver("bolt://neo4j:7687", auth=...)
        self.embedder = EmbeddingModel("BAAI/bge-large-en-v1.5")

    def search_kb(self, query: str) -> dict:
        """
        Hybrid search: vector + graph.
        """
        # STEP 1: Vector search (semantic similarity)
        query_embedding = self.embedder.embed(query)

        vector_results = self.qdrant.search(
            collection_name="runbooks",
            query_vector=query_embedding,
            limit=20,  # Get top 20 candidates
        )

        # Extract document chunks with scores
        vector_chunks = [{
            "text": hit.payload["text"],
            "source": hit.payload["source"],
            "score": hit.score,
            "title": hit.payload.get("title", ""),
        } for hit in vector_results]

        # STEP 2: Keyword search (BM25-style exact matching)
        keyword_results = self._keyword_search(query)
        # Complement vector search with exact-term matches

        # STEP 3: Merge using Reciprocal Rank Fusion
        merged = self._reciprocal_rank_fusion(vector_chunks, keyword_results)

        # STEP 4: Graph enrichment
        # Extract entities from the query and find relationships
        entities = self._extract_entities(query)
        graph_context = self._get_entity_relationships(entities)

        # STEP 5: Return top 5 merged results + graph context
        return {
            "documents": merged[:5],
            "graph_context": graph_context,
            "total_found": len(merged),
        }

    def _keyword_search(self, query):
        """Full-text keyword search (complements vector search)."""
        # Uses Qdrant's payload filtering or Elasticsearch
        # Catches exact-term matches that vector search might miss
        # Example: searching for "BGP-4471" (exact ID) vs semantic match
        pass

    def _reciprocal_rank_fusion(self, *result_lists, k=60):
        """
        Merge multiple ranked lists using RRF.

        RRF score = sum(1 / (k + rank_in_each_list))

        This is the standard way to merge vector + keyword search.
        """
        scores = {}
        for result_list in result_lists:
            for rank, item in enumerate(result_list):
                key = item["text"][:100]  # Dedup key
                scores[key] = scores.get(key, 0) + (1 / (k + rank))

        # Sort by fused score
        all_items = {item["text"][:100]: item
                     for item in result_lists[0]}  # Flatten
        return sorted(all_items.values(),
                      key=lambda x: scores.get(x["text"][:100], 0),
                      reverse=True)
```

---

## 7. PROMETHEUS — METRICS COLLECTION

### How search_metrics Queries Prometheus

```python
"""
Prometheus stores time-series metrics. The agent queries it to find
anomalies: "Is CPU elevated? Is memory leaking? Is error rate spiking?"
"""

import requests

class MetricsTool:
    PROMETHEUS_URL = "http://prometheus:9090/api/v1"

    def search_metrics(self, service: str, metric_name: str) -> dict:
        """Query Prometheus for a specific metric."""

        # Build PromQL query
        # Examples:
        #   metric_name = "cpu_usage" → query: 'cpu_usage{service="payment-svc"}'
        #   metric_name = "db_connections" → query: 'db_connection_pool_usage{service="payment-svc"}'
        query = f'{metric_name}{{service="{service}"}}'

        # Query range (last 30 minutes, 10-second resolution)
        params = {
            "query": query,
            "start": int(time.time()) - 1800,  # 30 min ago
            "end": int(time.time()),
            "step": "10s",  # 10-second resolution
        }

        response = requests.get(
            f"{self.PROMETHEUS_URL}/query_range",
            params=params,
            timeout=15,
        )

        data = response.json()["data"]["result"]

        # Process: extract values, compute stats, detect anomalies
        if not data:
            return {"error": f"No data for {metric_name} on {service}"}

        values = [(float(v[0]), float(v[1])) for v in data[0]["values"]]

        current_value = values[-1][1]
        historical_avg = sum(v[1] for v in values[:-6]) / max(len(values) - 6, 1)

        # Anomaly detection: current > 2× average
        is_anomaly = current_value > historical_avg * 2 if historical_avg > 0 else False

        return {
            "metric": metric_name,
            "service": service,
            "current": current_value,
            "average_30min": historical_avg,
            "is_anomaly": is_anomaly,
            "values": [{"timestamp": t, "value": v} for t, v in values],
        }
```

---

## 8. ELK — LOG AGGREGATION

### How query_logs Queries Elasticsearch

```python
"""
Elasticsearch stores application logs. The agent queries it to find
error patterns.

RAW RESULT: 50,000+ log entries (each entry has timestamp, level,
            service, message, trace_id, etc.)

COMPRESSED: Error summary — top error messages with counts and time ranges
"""

class LogsTool:
    ELASTICSEARCH_URL = "http://elasticsearch:9200"

    def query_logs(self, service: str, time_range: str = "last_30_minutes",
                   keyword: str = None) -> dict:
        """Search logs in Elasticsearch."""

        # Parse time range
        time_map = {
            "last_5_minutes": 300,
            "last_15_minutes": 900,
            "last_30_minutes": 1800,
            "last_1_hour": 3600,
        }
        seconds_ago = time_map.get(time_range, 1800)

        # Build Elasticsearch query
        must_clauses = [
            {"match": {"service": service}},
            {"range": {"@timestamp": {"gte": f"now-{seconds_ago}s"}}}
        ]

        if keyword:
            must_clauses.append({"match": {"message": keyword}})

        es_query = {
            "query": {"bool": {"must": must_clauses}},
            "sort": [{"@timestamp": "desc"}],
            "size": 10000,  # Max 10K entries
        }

        response = requests.post(
            f"{self.ELASTICSEARCH_URL}/logs-{service}-*/_search",
            json=es_query,
            timeout=30,
        )

        hits = response.json()["hits"]["hits"]
        logs = [hit["_source"] for hit in hits]

        return {
            "service": service,
            "time_range": time_range,
            "total_logs": len(logs),
            "logs": logs,
        }
```

---

## 9. THE COMPLETE REQUEST FLOW

```
PRODUCTION INCIDENT: "payment-svc error rate 15%"

TIME 0.0s   PagerDuty fires alert
             │
             ▼
TIME 0.1s   AlertProducer publishes to Kafka topic "incident-alerts"
             Key: "payment-svc" → Partition 3
             │
             ▼
TIME 0.5s   IncidentConsumer (pod-3) picks up message from partition 3
             │
             ▼
TIME 0.6s   InvestigationLock.try_acquire("payment-svc-error-rate")
             → Redis SETNX → acquired ✓
             │
             ▼
TIME 0.7s   Agent starts investigation. System prompt + user message loaded.
             Context Manager initialized. Token budget: 30K.
             │
             ▼
TIME 1.0s   ═══ ITERATION 1 ═══
             LLM Gateway routes to GPT-4o-mini (iteration < 3)
             LLM says: "Call query_logs(payment-svc, last_30_min)"
             │
             ▼
TIME 1.1s   ToolCache.get("query_logs", args) → CACHE MISS
             CircuitBreaker.is_open("query_logs") → CLOSED ✓
             │
             ▼
TIME 1.2s   LogsTool queries Elasticsearch
             ES returns 10,000 log entries (52K tokens uncompressed)
             │
TIME 4.5s   ELK response received (3.3 sec query time)
             │
             ▼
TIME 4.6s   ToolCache.set("query_logs", args, result) → Cached with 60s TTL
             │
             ▼
TIME 4.7s   ContextManager compresses result:
             52,847 tokens → 380 tokens (139× compression)
             Adds to context. Total context: ~2,500 tokens.
             │
             ▼
TIME 5.0s   AgentTrace logs: iteration 1 complete, cache miss,
             query_logs, 52K→380 tokens, 3.3 sec
             │
             ▼
TIME 5.5s   ═══ ITERATION 2 ═══
             LLM Gateway routes to GPT-4o-mini
             LLM says: "Call search_metrics(payment-svc, db_pool_usage)"
             │
TIME 5.6s   ToolCache → MISS
             Prometheus query → 8,200 tokens of metric data
             │
TIME 8.0s   Compressed: 220 tokens. Context total: ~3,000 tokens.
             │
             ▼
TIME 8.5s   ═══ ITERATION 3 ═══
             LLM Gateway routes to GPT-4o (iteration ≥ 3, needs reasoning)
             LLM says: "Call query_tickets(DB pool payment)"
             │
TIME 8.6s   ToolCache → MISS
             ServiceNow API → 24,000 tokens of ticket data
             │
TIME 11.0s  Compressed: 410 tokens. Context total: ~3,600 tokens.
             │
             ▼
TIME 11.5s  ═══ ITERATION 4 ═══
             LLM Gateway routes to GPT-4o
             LLM says: "Call search_kb(DB pool remediation)"
             │
TIME 11.6s  ToolCache → HIT! (Another investigation cached this 2 min ago)
             Cache returns in 0.8ms instead of querying Confluence
             │
TIME 11.7s  Compressed (from cache): 380 tokens. Context total: ~4,200 tokens.
             │
             ▼
TIME 12.0s  ═══ ITERATION 5: FINAL REPORT ═══
             LLM Gateway routes to GPT-4o
             LLM produces JSON diagnostic report (no tool call)
             │
TIME 20.0s  Report received. Validator runs:
             ✓ JSON valid
             ✓ All evidence sources cite tools that were called
             ✓ Confidence 0.87 > 0.60 threshold
             │
             ▼
TIME 20.1s  InvestigationLock.release()
             AgentTrace saves full trace
             │
             ▼
TIME 20.2s  Result delivered:
             → Slack #incident-response: Diagnostic report
             → ServiceNow: Ticket created with root cause + remediation
             → PagerDuty: Alert acknowledged
             │
             ▼
TIME 20.5s  Kafka consumer commits offset

═══ TOTAL: 20.5 seconds ═══
(Includes 3.3 sec ELK query, 2.4 sec Prom query, 2.4 sec ServiceNow query,
 8 sec LLM reasoning, rest = overhead)
```

---

## 10. INTERVIEW Q&A — INFRASTRUCTURE SPECIFICS

### Q: "How exactly do you use Redis?"

```
"Three use cases. First and most important: tool result caching. Each
tool call caches its result in Redis with a tool-specific TTL. Topology
and runbooks are cached for 1-24 hours because they rarely change. Logs
and metrics are cached for 1-2 minutes — enough to prevent redundant
queries during concurrent incidents but short enough to stay fresh.

The cache key is a hash of the tool name plus sorted arguments, so the
same query always hits the same cache entry. During a major outage where
10 alerts fire for the same root cause, the first agent populates the
cache and the other 9 get instant cache hits — saving 90% of backend
load.

Second: circuit breaker. I track consecutive failures per tool in Redis.
If ELK fails 3 times, the circuit opens and the agent skips ELK calls
for 60 seconds, preventing 30-second timeouts on every iteration.

Third: investigation deduplication. Redis SETNX acts as a distributed
lock — if two alerts fire for the same incident, only one agent
investigates. The other sees the lock and skips.

Cache hit ratio in production: 60%. That's 60% of tool calls served
from Redis in under 1 millisecond instead of hitting backends."
```

### Q: "Why Kafka instead of just calling the agent directly?"

```
"Three reasons. First: spike absorption. During a major outage, 500
alerts can fire in 2 minutes. Without Kafka, that's 500 concurrent
LLM API calls — we'd hit rate limits and the system would collapse.
Kafka buffers the spike. Agent pods consume at their own pace.

Second: durability and replay. If an agent pod crashes mid-investigation,
the Kafka message isn't acknowledged. Another pod picks it up and
retries. If the investigation fails 3 times, the message goes to a Dead
Letter Queue for manual review. Nothing is lost.

Third: ordering guarantees. We partition by service name, so all alerts
for 'payment-svc' go to the same partition and are processed in order.
This prevents race conditions when two alerts for the same service
fire simultaneously."
```

### Q: "How does the LLM Gateway decide which model to use?"

```
"Heuristic classification — no LLM call needed. If the request is in
the first 3 iterations (information gathering — just picking which tool
to call), route to GPT-4o-mini at $0.15 per million tokens. If it's
iteration 3+ (correlation and reasoning), route to GPT-4o at $2.50 per
million tokens.

This saves 57% per investigation. The insight is that 'deciding which
tool to call' is a simple task that mini handles perfectly, while
'correlating logs + metrics + tickets into a root cause hypothesis'
needs the reasoning power of GPT-4o.

The gateway also handles failover. If GPT-4o returns a 429 rate limit,
it falls back to GPT-4o-mini, then to self-hosted Llama 3.1 8B."
```

### Q: "Why Neo4j for topology? Why not just a relational database?"

```
"Because the queries are inherently GRAPH queries. 'What services
depend on the failing database, directly or transitively, up to 3 hops
away?' In SQL, that's a recursive CTE — slow and complex. In Neo4j,
it's a single Cypher pattern match that traverses the graph in
milliseconds.

The graph also enables blast-radius analysis: 'If I restart pgbouncer,
what services will be affected?' The agent traverses reverse
dependencies to answer this. That's a graph traversal, not a table join.

Additionally, the graph is used for GraphRAG — when searching the
knowledge base, I traverse the graph to find related entities and
inject those relationships into the LLM context. This improved
accuracy from 79% to 91%."
```

### Q: "How do you monitor the agent itself?"

```
"AgentTrace records every LLM call, tool call, cache hit/miss, error,
and reasoning step. Each event has a timestamp. This creates a full
waterfall trace of the investigation.

For real-time monitoring, I track:
  - Investigation duration (P50: 85 sec, P95: 180 sec, P99: 300 sec)
  - Cache hit ratio (target: >50%, actual: 60%)
  - LLM cost per investigation (target: <$0.10, actual: $0.08)
  - Tool failure rate (target: <5%, actual: 2.1%)
  - Escalation rate (target: <20%, actual: 13%)
  - Root cause accuracy (target: >80%, actual: 87%)

These metrics are pushed to Prometheus and visualized in Grafana.
If escalation rate spikes above 20%, it means the agent is struggling
— either the tools are failing or the incident types are novel."
```

### Q: "What happens if Redis goes down?"

```
"The agent degrades gracefully. Cache misses become normal — every tool
call hits the backend directly. Slower (no cache hits) but still
functional. The circuit breaker stops working, but the max_iterations
limit still prevents infinite loops.

Investigation deduplication stops working — two agents might
investigate the same incident. That's wasteful but not harmful.

The system is designed for Redis failure. I use a Redis cluster with
3 masters and 3 replicas. If a master dies, a replica promotes
automatically. Total Redis downtime in production: near zero."
```
