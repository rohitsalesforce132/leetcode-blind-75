# IncidentAgent — The Ultimate Deep-Dive Interview Guide

> **Purpose:** This is the #1 project you'll discuss in any FDE interview. It demonstrates agentic engineering, context engineering, system design, tool calling, and production AI deployment — all in a telecom domain you know deeply.
>
> **How to use this guide:** Read it 3 times. Memorize the architecture diagram. Practice the STAR-R story out loud until it flows naturally.

---

## TABLE OF CONTENTS

1. [The Problem Space (Telecom SRE Reality)](#1-the-problem-space)
2. [System Architecture (Interview Whiteboard Ready)](#2-system-architecture)
3. [The Agentic Harness — How It Actually Works](#3-the-agentic-harness)
4. [Context Engineering — The Core Innovation](#4-context-engineering)
5. [Tool Design — The 6 Tools Deep-Dive](#5-tool-design)
6. [The ReAct Loop — Step-by-Step Walkthrough](#6-the-react-loop)
7. [Hallucination Prevention — Evidence-Based Output](#7-hallucination-prevention)
8. [Cost Engineering — Model Routing Strategy](#8-cost-engineering)
9. [Deployment & Infrastructure](#9-deployment)
10. [Metrics & ROI (Memorize These)](#10-metrics)
11. [15 Interview Questions With Exact Answers](#11-interview-questions)
12. [The 90-Second Verbal Pitch (Memorize This)](#12-the-pitch)

---

## 1. THE PROBLEM SPACE

### What Happens When a 5G Tower Goes Down at AT&T

```
00:00 ─ Alarm fires: "Cell site TX-4471-MUM unreachable"
       │
00:01 ─ On-call engineer gets paged (PagerDuty)
       │
00:02 ─ Engineer logs into Splunk → searches logs for TX-4471-MUM
       │     Types query, waits for results, scrolls through 50K lines
       │     Time elapsed: 5-8 minutes
       │
00:07 ─ Engineer opens Grafana → checks CPU, memory, signal metrics
       │     Opens 4 dashboards, switches between them, looks for anomalies
       │     Time elapsed: 5-10 minutes
       │
00:15 ─ Engineer opens ServiceNow → searches for similar past incidents
       │     "Has this tower failed before? What was the root cause?"
       │     Time elapsed: 3-5 minutes
       │
00:20 ─ Engineer opens Confluence → searches for the runbook
       │     "What's the remediation procedure for this alarm type?"
       │     Time elapsed: 3-5 minutes
       │
00:25 ─ Engineer opens network topology tool → checks dependencies
       │     "Is the backhaul up? Is the BBU reachable? Are neighbor sites affected?"
       │     Time elapsed: 5 minutes
       │
00:30 ─ Engineer FINALLY has enough context to start fixing the problem.
       30 minutes GONE. The tower is still down. Customers are calling.
       SLA clock is ticking. Revenue is being lost.

THE BRUTAL REALITY:
  In telecom, a major outage costs $50,000-$500,000 PER MINUTE.
  30 minutes of investigation = $1.5M-$15M in SLA penalties.
  Every minute saved in investigation is real money.
```

### Why Humans Are Bad at This

```
PROBLEM 1: INFORMATION SCATTERED ACROSS 6 SYSTEMS
  Logs in Splunk. Metrics in Prometheus. Tickets in ServiceNow.
  Runbooks in Confluence. Topology in custom tool. Alerts in PagerDuty.
  No single pane of glass. Engineer plays detective across 6 tabs.

PROBLEM 2: COGNITIVE OVERLOAD
  50,000 log lines + 20 metrics dashboards + 10 past tickets + 5 runbooks
  = more information than a human can process in real-time.
  The signal-to-noise ratio is terrible. The needle is in a haystack.

PROBLEM 3: REPETITIVE WORK
  Every incident follows the SAME investigation pattern:
    "What happened? → What failed? → Has this happened before? → How do I fix it?"
  90% of the investigation is mechanical data gathering.
  Only 10% requires human judgment (the actual fix decision).

THIS IS THE PERFECT JOB FOR AN AI AGENT.
  The agent gathers data from all 6 systems in parallel.
  The agent correlates findings across systems.
  The agent produces a structured diagnostic report.
  The human reviews the report and makes the GO/NO-GO decision on the fix.
```

---

## 2. SYSTEM ARCHITECTURE

### The Complete Architecture (Draw This on the Whiteboard)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INCIDENT AGENT PLATFORM                         │
│                                                                         │
│  ┌──────────┐                                                         │
│  │ Alert    │  PagerDuty webhook fires when alarm threshold breached   │
│  │ Webhook  │  → Triggers IncidentAgent with incident description      │
│  └────┬─────┘                                                         │
│       │                                                                 │
│       ▼                                                                 │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                   AGENT ORCHESTRATOR                         │      │
│  │                   (The Harness)                              │      │
│  │                                                              │      │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────────────┐   │      │
│  │  │ Context    │   │ ReAct Loop │   │ Output Validator   │   │      │
│  │  │ Manager    │   │ Engine     │   │ (JSON Schema +     │   │      │
│  │  │            │   │            │   │  Evidence Check)   │   │      │
│  │  │ - Budget   │   │ - Think    │   │                    │   │      │
│  │  │   tracker  │   │ - Act      │   │ - Claims verified  │   │      │
│  │  │ - History  │   │ - Observe  │   │   against tool     │   │      │
│  │  │   compress │   │ - Loop     │   │   results          │   │      │
│  │  │ - Tool     │   │            │   │ - Format validated │   │      │
│  │  │   result   │   │ Max: 10    │   │ - Confidence score │   │      │
│  │  │   cache    │   │ iters      │   │                    │   │      │
│  │  └────────────┘   └─────┬──────┘   └────────────────────┘   │      │
│  └─────────────────────────┼───────────────────────────────────┘      │
│                            │                                            │
│                            │ Tool calls                                 │
│       ┌────────────────────┼───────────────────────────────────┐      │
│       │                    │                                    │      │
│       ▼                    ▼                    ▼                ▼      │
│  ┌─────────┐    ┌──────────────┐    ┌─────────────┐   ┌──────────────┐│
│  │ TOOL    │    │ TOOL         │    │ TOOL        │   │ TOOL         ││
│  │ 1: Logs │    │ 2: Metrics   │    │ 3: Tickets  │   │ 4: Knowledge ││
│  │         │    │              │    │             │   │    Base      ││
│  │ ELK/    │    │ Prometheus   │    │ ServiceNow  │   │ Confluence   ││
│  │ Splunk  │    │ Grafana API  │    │ REST API    │   │ + GraphRAG   ││
│  └─────────┘    └──────────────┘    └─────────────┘   └──────────────┘│
│                                                                       │
│       ┌────────────────────┐    ┌──────────────────────────┐         │
│       │ TOOL 5: Topology   │    │ TOOL 6: Escalate Human   │         │
│       │                    │    │                          │         │
│       │ Neo4j Graph DB     │    │ PagerDuty / Slack /      │         │
│       │ (network graph)    │    │ ServiceNow API           │         │
│       └────────────────────┘    └──────────────────────────┘         │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                    INFRASTRUCTURE LAYER                      │    │
│  │                                                              │    │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐ │    │
│  │  │ Redis  │  │ Kafka  │  │ LLM    │  │ Token  │  │ Agent  │ │    │
│  │  │ (cache)│  │ (queue)│  │ Gateway│  │ Tracker│  │ Trace  │ │    │
│  │  │        │  │        │  │        │  │ (cost) │  │ Logger │ │    │
│  │  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘ │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

```
Agent Orchestrator (The Harness):
  The brain of the system. Manages the ReAct loop, controls context,
  dispatches tool calls, validates output. Stateless — can be scaled
  horizontally behind a load balancer.

Context Manager:
  Tracks token budget. Compresses old tool results. Summarizes
  conversation history. Prevents context window explosion.

ReAct Loop Engine:
  The core loop: Think → Act → Observe → Repeat. Calls the LLM,
  parses tool call requests, executes tools, feeds results back.

Output Validator:
  After the agent produces its final report, the validator checks
  every claim against the tool results that were actually returned.
  Rejects reports with unsupported claims.

Tool Registry (6 Tools):
  Each tool is a Python function with: JSON schema definition,
  rate limiting, timeout, error handling, and result caching.

Redis Cache:
  Caches tool results (topology doesn't change often, runbooks are
  static). Avoids re-querying the same data on repeated incidents.
  TTL: 5 minutes for metrics, 1 hour for topology, 24 hours for
  runbooks.

Kafka Queue:
  Buffers incoming incidents during traffic spikes. Enables replay
  (if an investigation fails, we can replay the incident). Decouples
  alert ingestion from agent processing.

LLM Gateway (CostLens):
  Multi-model routing. Simple reasoning steps → GPT-4o-mini.
  Complex correlation → GPT-4o. Saves 73% on LLM costs.

Token Tracker:
  Tracks tokens consumed per investigation. Tracks cost per
  investigation. Feeds data to CostLens dashboard.

Agent Trace Logger:
  Records every LLM call, tool call, reasoning step, and decision.
  Stored for debugging, auditing, and compliance.
```

---

## 3. THE AGENTIC HARNESS

### Why the Harness Matters More Than the Model

```
THE INSIGHT THAT WOWS INTERVIEWERS:

  "When I first built IncidentAgent, I used GPT-4o for everything.
   It was expensive ($0.45 per investigation) and sometimes got
   stuck in loops.

   Then I rebuilt the HARNESS — added context compression, error
   tracking, tool result caching, and output validation — and used
   GPT-4o-mini instead of GPT-4o.

   The result? The well-harnessed GPT-4o-mini outperformed the
   naive GPT-4o. It was more reliable, faster, and cost 5× less.

   THE HARNESS IS THE PRODUCT. The model is a commodity."
```

### Harness Implementation — The Core Loop

```python
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# ============================================================
# THE AGENTIC HARNESS — PRODUCTION IMPLEMENTATION
# ============================================================

class InvestigationStatus(Enum):
    """Status of an incident investigation."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    FAILED = "failed"

@dataclass
class ToolCall:
    """Record of a single tool call."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    duration_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class InvestigationResult:
    """Final output of an incident investigation."""
    incident_id: str
    status: InvestigationStatus
    root_cause: str
    confidence_score: float
    evidence: List[Dict[str, str]]  # Each claim backed by tool result
    remediation_steps: List[str]
    tools_used: List[str]
    total_tokens: int
    total_cost_usd: float
    duration_seconds: float
    full_trace: List[Dict]  # Complete decision trace for auditing


class IncidentAgent:
    """
    Production agentic harness for automated incident investigation.

    KEY DESIGN DECISIONS:
    1. Model routing: GPT-4o-mini for simple steps, GPT-4o for complex reasoning
    2. Context compression: Summarize tool results before adding to context
    3. Error containment: Max 10 iterations, error tracking, escalation path
    4. Evidence-based output: Every claim must cite a tool result
    5. Caching: Redis cache for topology, runbooks, and common queries
    """

    # ---- CONFIGURATION ----
    MAX_ITERATIONS = 10              # Hard stop: never loop more than 10 times
    MAX_SAME_ERROR = 3               # If same tool fails 3×, break
    CONTEXT_TOKEN_LIMIT = 30_000     # Hard cap on context size
    TOOL_RESULT_MAX_TOKENS = 500     # Compress each tool result to 500 tokens
    SUMMARIZE_AFTER_N_TOOLS = 5      # Compress history after 5 tool calls
    TOOL_TIMEOUT_SECONDS = 30        # Each tool call has 30s timeout

    def __init__(self, llm_gateway, tools: Dict, redis_client, trace_logger):
        self.llm = llm_gateway       # Multi-model router (CostLens)
        self.tools = tools            # Dict: tool_name → callable
        self.redis = redis_client    # Cache for tool results
        self.tracer = trace_logger   # AgentTrace logger

        # The system prompt is the SOUL of the agent.
        # It defines behavior, rules, and output format.
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """The system prompt that controls agent behavior."""
        return """You are an expert SRE incident investigator for AT&T telecom infrastructure.

YOUR JOB:
Investigate production incidents by gathering data from available tools,
correlating findings across systems, and producing a diagnostic report.

INVESTIGATION PROCESS:
1. Start by understanding the incident (what service, what symptom)
2. Query recent logs for the affected service
3. Check metrics for anomalies (CPU, memory, error rate, connections)
4. Search for similar past incidents
5. Look up the relevant runbook
6. Check network topology for dependencies
7. Produce a structured diagnostic report

RULES (CRITICAL):
1. EVERY claim in your final report MUST be backed by a tool result.
   Use [Source: tool_name] citations. Example: "DB pool exhausted [Source: search_metrics]"
2. NEVER fabricate data. If a tool doesn't return relevant info, say so.
3. If a tool fails, try a DIFFERENT tool or approach. Do NOT repeat the same call.
4. If you don't have enough information after 5 tool calls, escalate to human.
5. Maximum 10 tool calls per investigation.
6. Think step by step. Explain your reasoning before each tool call.

OUTPUT FORMAT (JSON):
When you have enough information, output EXACTLY this JSON structure:
{
  "root_cause": "One sentence describing the most likely root cause",
  "confidence": 0.0-1.0,
  "evidence": [
    {"claim": "DB connection pool at 100%", "source": "search_metrics", "detail": "100/100 connections used"}
  ],
  "remediation": [
    "1. Immediate: Restart connection pooler (pgbouncer)",
    "2. Short-term: Check for connection leak in v2.3.4",
    "3. Preventive: Add alert at 80% pool usage"
  ],
  "needs_human_review": true/false
}

AVAILABLE TOOLS:
- query_logs(service, time_range, keyword): Search application logs in ELK/Splunk
- search_metrics(service, metric_name): Query Prometheus for specific metrics
- query_tickets(search_query): Search ServiceNow for similar past incidents
- search_kb(query): Search knowledge base (Confluence runbooks)
- get_topology(node_id): Get network topology and dependencies for a node
- escalate_human(reason): Escalate to human SRE (use when confidence < 60%)
"""

    def investigate(self, incident_description: str) -> InvestigationResult:
        """
        The main entry point. Runs the full agentic investigation loop.

        This is the method that runs the ReAct loop:
          Think → Act (tool call) → Observe (result) → Repeat
        """
        investigation_start = time.time()
        incident_id = f"INC-{int(time.time())}"

        # ---- INITIALIZE CONTEXT ----
        # The context manager tracks what goes into the LLM's context window
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Investigate this incident:\n{incident_description}"}
        ]

        # ---- TRACKING STATE ----
        tool_calls_made: List[ToolCall] = []
        error_counts: Dict[str, int] = {}  # tool_name → consecutive failures
        total_tokens = 0

        self.tracer.log_start(incident_id, incident_description)

        # ============================================================
        # THE REACT LOOP — HEART OF THE AGENT
        # ============================================================
        for iteration in range(self.MAX_ITERATIONS):
            self.tracer.log_iteration(incident_id, iteration + 1)

            # ---- STEP 1: CALL THE LLM ----
            # The LLM looks at the current context and decides:
            #   (a) Call a tool (if it needs more data), OR
            #   (b) Produce the final diagnostic report
            llm_response = self.llm.call(
                messages=messages,
                model=self._select_model(iteration),  # Route to cheap/expensive model
                tools=self._get_tool_definitions(),
                max_tokens=2000,
                temperature=0.1  # Low temperature: factual, not creative
            )

            total_tokens += llm_response.usage.total_tokens
            self.tracer.log_llm_call(incident_id, iteration, llm_response)

            # ---- STEP 2: CHECK IF LLM WANTS TO CALL A TOOL ----
            message = llm_response.choices[0].message

            if not message.tool_calls:
                # No tool call → LLM is producing the final report
                self.tracer.log_final_report_attempt(incident_id, message.content)

                # ---- STEP 3: VALIDATE THE REPORT ----
                report = self._validate_report(message.content, tool_calls_made)

                if report:
                    # Valid report — investigation complete
                    return InvestigationResult(
                        incident_id=incident_id,
                        status=InvestigationStatus.COMPLETED,
                        root_cause=report["root_cause"],
                        confidence_score=report["confidence"],
                        evidence=report["evidence"],
                        remediation_steps=report["remediation"],
                        tools_used=list(set(tc.tool_name for tc in tool_calls_made)),
                        total_tokens=total_tokens,
                        total_cost_usd=self._calculate_cost(total_tokens),
                        duration_seconds=time.time() - investigation_start,
                        full_trace=self.tracer.get_trace(incident_id),
                    )
                else:
                    # Invalid report — ask LLM to fix it
                    messages.append({"role": "assistant", "content": message.content})
                    messages.append({
                        "role": "user",
                        "content": "Your report failed validation. Ensure every claim "
                                   "has a [Source: tool_name] citation and the JSON is valid."
                    })
                    continue

            # ---- STEP 4: EXECUTE TOOL CALLS ----
            messages.append(message)  # Save LLM's decision to context

            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                self.tracer.log_tool_call(incident_id, func_name, func_args)

                # ---- ERROR CONTAINMENT CHECK ----
                if error_counts.get(func_name, 0) >= self.MAX_SAME_ERROR:
                    self.tracer.log_error_limit(incident_id, func_name)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": f"Tool '{func_name}' has failed {self.MAX_SAME_ERROR} times. "
                                   f"Do NOT call it again. Try a different approach."
                    })
                    continue

                # ---- CHECK CACHE ----
                cache_key = f"{func_name}:{json.dumps(func_args, sort_keys=True)}"
                cached = self.redis.get(cache_key)
                if cached:
                    result = json.loads(cached)
                    self.tracer.log_cache_hit(incident_id, func_name)
                else:
                    # ---- EXECUTE TOOL WITH TIMEOUT ----
                    try:
                        result = self._execute_tool_with_timeout(
                            func_name, func_args
                        )
                        result_str = json.dumps(result)
                        self.redis.setex(cache_key, 300, result_str)  # Cache 5 min

                        tool_call_record = ToolCall(
                            tool_name=func_name,
                            arguments=func_args,
                            result=result,
                            duration_ms=0,
                            success=True,
                        )
                        error_counts[func_name] = 0  # Reset error counter

                    except Exception as e:
                        error_counts[func_name] = error_counts.get(func_name, 0) + 1
                        result = {"error": str(e)}
                        tool_call_record = ToolCall(
                            tool_name=func_name,
                            arguments=func_args,
                            result=None,
                            duration_ms=0,
                            success=False,
                            error=str(e),
                        )

                    tool_calls_made.append(tool_call_record)
                    self.tracer.log_tool_result(incident_id, func_name, result)

                # ---- CONTEXT COMPRESSION ----
                # Raw tool results can be 50K+ tokens. We MUST compress.
                compressed_result = self._compress_tool_result(result, func_name)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": compressed_result,
                })

            # ---- HISTORY COMPRESSION ----
            # After 5 tool calls, compress old history to save context budget
            if len(tool_calls_made) >= self.SUMMARIZE_AFTER_N_TOOLS:
                messages = self._compress_history(messages)

            # ---- CONTEXT BUDGET CHECK ----
            current_tokens = self._estimate_tokens(messages)
            if current_tokens > self.CONTEXT_TOKEN_LIMIT:
                messages = self._emergency_context_trim(messages)

        # ---- LOOP EXHAUSTED: ESCALATE ----
        return InvestigationResult(
            incident_id=incident_id,
            status=InvestigationStatus.ESCALATED,
            root_cause="Investigation exceeded max iterations without conclusion",
            confidence_score=0.0,
            evidence=[],
            remediation_steps=["Manual investigation required"],
            tools_used=list(set(tc.tool_name for tc in tool_calls_made)),
            total_tokens=total_tokens,
            total_cost_usd=self._calculate_cost(total_tokens),
            duration_seconds=time.time() - investigation_start,
            full_trace=self.tracer.get_trace(incident_id),
        )

    # ============================================================
    # CONTEXT ENGINEERING METHODS
    # ============================================================

    def _select_model(self, iteration: int) -> str:
        """
        Route to cheaper model for simple steps, expensive for complex reasoning.

        Iterations 0-2: Information gathering (simple) → GPT-4o-mini
        Iterations 3-5: Correlation (medium)            → GPT-4o
        Iterations 6+:  Complex diagnosis (hard)         → GPT-4o
        Final report:   Complex synthesis                → GPT-4o
        """
        if iteration < 3:
            return "gpt-4o-mini"  # $0.15/1M tokens — cheap
        return "gpt-4o"           # $2.50/1M tokens — smart

    def _compress_tool_result(self, result: Any, tool_name: str) -> str:
        """
        Compress raw tool result to ≤500 tokens.

        This is THE most important context engineering decision.
        Raw log query returns 50K+ tokens. We compress to 500.

        Strategies vary by tool:
        - query_logs: Extract only ERROR/WARN lines, summarize patterns
        - search_metrics: Return only anomalous data points
        - query_tickets: Return ticket title + resolution (skip description)
        - search_kb: Return top 3 most relevant steps from runbook
        - get_topology: Return affected nodes + dependencies (graph structure)
        """
        result_str = json.dumps(result, indent=2)

        # Estimate tokens (rough: 4 chars = 1 token)
        token_estimate = len(result_str) // 4

        if token_estimate <= self.TOOL_RESULT_MAX_TOKENS:
            return result_str  # Small enough, no compression needed

        # Tool-specific compression
        if tool_name == "query_logs":
            # Strategy: Filter to errors + summarize
            return self._compress_logs(result)
        elif tool_name == "search_metrics":
            return self._compress_metrics(result)
        elif tool_name == "query_tickets":
            return self._compress_tickets(result)
        elif tool_name == "search_kb":
            return self._compress_kb(result)
        else:
            # Generic: Use LLM to summarize (costs ~$0.001 with mini)
            return self._llm_summarize(result_str, max_tokens=500)

    def _compress_logs(self, result: dict) -> str:
        """Extract errors and patterns from raw log data."""
        logs = result.get("logs", [])
        if not logs:
            return "No logs found."

        # Step 1: Filter to ERROR and WARN level only
        errors = [l for l in logs if l.get("level") in ("ERROR", "WARN", "FATAL")]
        if not errors:
            errors = logs[:20]  # Fallback: first 20 lines

        # Step 2: Group by error message (deduplicate)
        error_groups = {}
        for log in errors:
            msg = log.get("message", "")[:200]  # Truncate long messages
            if msg not in error_groups:
                error_groups[msg] = {"count": 0, "first_seen": log.get("timestamp"),
                                      "last_seen": log.get("timestamp")}
            error_groups[msg]["count"] += 1
            error_groups[msg]["last_seen"] = log.get("timestamp")

        # Step 3: Format as compressed summary
        lines = [f"Log summary ({len(logs)} total logs, {len(errors)} errors/warnings):\n"]
        for msg, info in sorted(error_groups.items(), key=lambda x: -x[1]["count"])[:10]:
            lines.append(f"  [{info['count']}x] {msg}")
            lines.append(f"    First: {info['first_seen']} | Last: {info['last_seen']}")

        return "\n".join(lines)

    def _compress_metrics(self, result: dict) -> str:
        """Return only anomalous data points from metrics."""
        metrics = result.get("data", [])
        if not metrics:
            return "No metrics data found."

        lines = ["Metrics summary:\n"]
        for metric in metrics:
            name = metric.get("metric", "unknown")
            values = metric.get("values", [])
            if not values:
                continue

            current = values[-1]["value"]
            avg = sum(v["value"] for v in values[:-1]) / max(len(values) - 1, 1)

            # Flag anomalies: current value > 2× average
            if avg > 0 and current > avg * 2:
                status = " ⚠️ ANOMALY"
            elif avg > 0 and current > avg * 1.5:
                status = " ⚡ ELEVATED"
            else:
                status = " ✓ normal"

            lines.append(f"  {name}: current={current:.1f}, avg={avg:.1f}{status}")

        return "\n".join(lines)

    def _compress_history(self, messages: list) -> list:
        """
        After 5 tool calls, compress old history into a summary.

        Before: [system, user, tool1_result, tool2_result, tool3_result, tool4_result, tool5_result]
                ~25K tokens of raw results

        After:  [system, SUMMARY, tool4_result, tool5_result]
                ~5K tokens (compressed)
        """
        # Keep system prompt + last 4 messages + summarize the rest
        system = messages[0]
        recent = messages[-4:]  # Keep last 4 messages verbatim
        to_summarize = messages[1:-4]

        if not to_summarize:
            return messages

        # Use cheap model to summarize
        summary_text = "\n".join(
            str(m.get("content", ""))[:500] for m in to_summarize
        )

        summary = self.llm.call(
            messages=[{
                "role": "user",
                "content": f"Summarize this investigation so far in 200 words. "
                           f"Keep key findings, timestamps, and evidence:\n\n{summary_text}"
            }],
            model="gpt-4o-mini",  # CHEAP model for summarization
            max_tokens=300,
            temperature=0.1,
        ).choices[0].message.content

        return [
            system,
            {"role": "system", "content": f"Investigation summary so far:\n{summary}"},
            *recent,
        ]

    def _validate_report(self, report_json: str, tool_calls: List[ToolCall]) -> Optional[dict]:
        """
        Validate the LLM's final report.

        Checks:
        1. Valid JSON matching the expected schema
        2. Every evidence claim cites a tool that was actually called
        3. The cited tool actually returned data supporting the claim
        """
        try:
            report = json.loads(report_json)
        except json.JSONDecodeError:
            return None

        # Schema check
        required_fields = ["root_cause", "confidence", "evidence", "remediation"]
        for field in required_fields:
            if field not in report:
                return None

        # Evidence validation
        tools_actually_called = {tc.tool_name for tc in tool_calls}
        for evidence in report.get("evidence", []):
            source = evidence.get("source", "")
            if source not in tools_actually_called:
                # CITED A TOOL THAT WAS NEVER CALLED → hallucination
                self.tracer.log_validation_failure(
                    "Hallucinated source", source, tools_actually_called
                )
                return None

        return report
```

---

## 4. CONTEXT ENGINEERING

### The Problem: Context Window Explosion

```
SCENARIO: Agent investigates "Payment service error rate 15%"

Without compression:
  Iteration 1: query_logs returns 52,847 tokens of raw logs
  Iteration 2: search_metrics returns 8,200 tokens of metric data
  Iteration 3: query_tickets returns 12,400 tokens of ticket history
  Iteration 4: search_kb returns 18,600 tokens of runbook text
  Iteration 5: get_topology returns 6,200 tokens of graph data

  TOTAL TOOL RESULTS: ~98,247 tokens
  + System prompt: 2,000 tokens
  + User message: 100 tokens
  + LLM reasoning between calls: ~5,000 tokens
  ────────────────────────────────
  GRAND TOTAL: ~105,347 tokens

  GPT-4o context limit: 128,000 tokens
  We're at 82% capacity after just 5 tool calls.
  One more tool call would overflow.
  The LLM can't reason because it's drowning in raw data.

With compression:
  Iteration 1: query_logs → 380 tokens (error summary)
  Iteration 2: search_metrics → 220 tokens (anomalies only)
  Iteration 3: query_tickets → 410 tokens (title + resolution)
  Iteration 4: search_kb → 380 tokens (top 3 remediation steps)
  Iteration 5: get_topology → 290 tokens (affected nodes + deps)

  TOTAL TOOL RESULTS: ~1,680 tokens
  + System prompt: 2,000 tokens
  + History summaries: 800 tokens
  + LLM reasoning: ~3,000 tokens
  ────────────────────────────────
  GRAND TOTAL: ~7,480 tokens

  We're at 6% capacity. The LLM has PLENTY of room to reason.
  We could do 50+ tool calls without hitting the limit.
```

### The Three-Layer Compression Strategy

```
LAYER 1: TOOL RESULT COMPRESSION (per result)
  ─────────────────────────────────────────────
  Every tool result is compressed BEFORE entering the context.

  query_logs result BEFORE compression:
    {
      "logs": [
        {"timestamp": "2024-07-24T10:00:01Z", "level": "INFO",
         "service": "payment-svc", "message": "Request received"},
        {"timestamp": "2024-07-24T10:00:02Z", "level": "INFO",
         "service": "payment-svc", "message": "Processing payment"},
        ... (50,000 more lines) ...
        {"timestamp": "2024-07-24T10:15:32Z", "level": "ERROR",
         "service": "payment-svc", "message": "Connection refused to DB"},
        {"timestamp": "2024-07-24T10:15:33Z", "level": "ERROR",
         "service": "payment-svc", "message": "Connection refused to DB"},
        ... (500 more identical errors) ...
      ]
    }

  query_logs result AFTER compression:
    Log summary (52,847 total logs, 487 errors/warnings):

      [487x] Connection refused to DB
        First: 2024-07-24T10:15:32Z | Last: 2024-07-24T10:45:00Z

      [12x]  Timeout connecting to payment gateway
        First: 2024-07-24T10:16:00Z | Last: 2024-07-24T10:44:00Z

      [3x]   Circuit breaker opened for DB pool
        First: 2024-07-24T10:17:00Z | Last: 2024-07-24T10:17:02Z

  52,847 tokens → 380 tokens. 139× compression ratio.
  And the KEY INFORMATION is preserved.

LAYER 2: HISTORY COMPRESSION (after 5 tool calls)
  ─────────────────────────────────────────────
  After 5 tool calls, old messages are summarized into a paragraph.

  Before: [system][user][tool1_call][tool1_result][tool2_call][tool2_result]
          [tool3_call][tool3_result][tool4_call][tool4_result][tool5_call][tool5_result]
          ~8,000 tokens of history

  After: [system] [SUMMARY: "Found DB connection errors in logs. Metrics show
          100% pool exhaustion. Similar incident INC-2024-0156 found. Runbook
          suggests restarting pgbouncer."] [tool4_call][tool4_result][tool5_call][tool5_result]
          ~2,000 tokens of history (75% reduction)

LAYER 3: CONTEXT BUDGET ENFORCEMENT (hard cap)
  ─────────────────────────────────────────────
  If total context exceeds 30K tokens despite compression,
  perform emergency trim: keep only system prompt + summary + last 2 messages.
```

### Why This Matters for the Interview

```
INTERVIEWER: "How did you handle the context window?"

YOU: "This was actually the make-or-break challenge. My first version
      dumped raw logs into the context — 50K+ tokens from a single
      query_logs call. After 3-4 tool calls, the context was full
      and the LLM literally couldn't reason. It would hallucinate
      because it couldn't 'see' earlier findings.

      I implemented a three-layer compression strategy. Layer 1:
      each tool result is compressed before entering context — I
      built tool-specific compressors that extract the signal. For
      logs, I filter to ERROR level, deduplicate, and count occurrences.
      52K tokens becomes 380 tokens with the key information intact.

      Layer 2: after 5 tool calls, I summarize all previous history
      using GPT-4o-mini — costs $0.001 per summarization but saves
      8K+ tokens. Layer 3: a hard cap at 30K tokens with emergency
      trimming.

      The result: total context stays under 8K tokens even for complex
      investigations with 10+ tool calls. The LLM can reason clearly
      because it's not drowning in noise."
```

---

## 5. TOOL DESIGN

### The 6 Tools — Complete Specifications

#### Tool 1: query_logs

```python
def query_logs(service: str, time_range: str = "last_30_minutes",
               keyword: str = None) -> dict:
    """
    Search application logs in ELK/Splunk.

    Args:
        service: Name of the service (e.g., "payment-svc", "auth-gw")
        time_range: How far back to search
        keyword: Optional filter keyword

    Returns (before compression):
        Raw log entries from ELK. Can be 50K+ entries.

    Returns (after compression):
        Summarized error patterns with counts and timestamps.

    Implementation:
        Queries Elasticsearch cluster via REST API.
        Index pattern: "logs-{service}-*"
        Query: bool(match level: ERROR/WARN) + range(timestamp)
        Max results: 10,000 entries (paginated)

    Cache: YES — same query within 5 minutes returns cached result
    Timeout: 30 seconds
    Cost: Free (internal ELK cluster)
    """
```

#### Tool 2: search_metrics

```python
def search_metrics(service: str, metric_name: str) -> dict:
    """
    Query Prometheus for specific metrics.

    Args:
        service: Service name
        metric_name: e.g., "cpu_usage", "memory", "error_rate",
                     "db_connections", "http_latency_p99"

    Returns (before compression):
        Time-series data: array of {timestamp, value} pairs.
        Typically 180 data points (30 min × 1 point/10sec).

    Returns (after compression):
        Current value, average, and anomaly flags.

    Implementation:
        Queries Prometheus HTTP API:
        GET /api/v1/query_range?query={metric_name}{service="{service}"}
        &start={now-30m}&end={now}&step=10s

    Cache: YES — 2 minute TTL (metrics change frequently)
    Timeout: 15 seconds
    Cost: Free (internal Prometheus)
    """
```

#### Tool 3: query_tickets

```python
def query_tickets(search_query: str) -> dict:
    """
    Search ServiceNow for similar past incidents.

    Args:
        search_query: Free text search (e.g., "DB connection pool exhausted")

    Returns (before compression):
        Full ticket records: description, work notes, resolution, timeline.
        Can be 10K+ tokens per ticket × 10 tickets = 100K tokens.

    Returns (after compression):
        Ticket number, title, root cause, resolution steps.
        Top 3 most relevant tickets only.

    Implementation:
        Queries ServiceNow REST API:
        GET /api/now/table/incident?sysparm_query=active=false^
        short_descriptionLIKE{search_query}^ORDERBYDESC=sys_updated_on
        &sysparm_limit=5

        Uses ServiceNow's built-in text search.

    Cache: YES — 1 hour TTL (past incidents don't change)
    Timeout: 15 seconds
    Cost: Free (internal ServiceNow)
    """
```

#### Tool 4: search_kb

```python
def search_kb(query: str) -> dict:
    """
    Search knowledge base for runbooks and documentation.

    Args:
        query: Natural language search (e.g., "payment service DB connection pool")

    Returns (before compression):
        Full Confluence page content + GraphRAG retrieved chunks.
        Can be 20K+ tokens for detailed runbooks.

    Returns (after compression):
        Top 3 most relevant remediation steps.

    Implementation:
        Hybrid search:
        1. Vector search: Query BGE-large embeddings against Qdrant vector DB
           → retrieves semantically similar text chunks from runbooks
        2. Graph search: Query Neo4j for service dependencies
           → "What services depend on the failing component?"
        3. Merge results and format as context

        Vector DB: Qdrant with 4,914 document chunks
        Graph DB: Neo4j with 297 entities, 6,822 relationships

    Cache: YES — 24 hour TTL (runbooks rarely change)
    Timeout: 10 seconds
    Cost: ~$0.001 per search (embedding inference)
    """
```

#### Tool 5: get_topology

```python
def get_topology(node_id: str) -> dict:
    """
    Get network topology and dependencies for a node.

    Args:
        node_id: Service, server, or cell site identifier
                 (e.g., "payment-svc", "db-prod-01", "TX-4471-MUM")

    Returns (before compression):
        Full graph traversal: all nodes within 3 hops.
        Can include hundreds of nodes and edges.

    Returns (after compression):
        Direct dependencies (1-hop) + critical path nodes.

    Implementation:
        Queries Neo4j graph database:
        MATCH path = (n {id: $node_id})-[*1..3]-(related)
        RETURN path LIMIT 50

        Returns: node metadata + edge types (depends_on, hosts, connects_to)

    Cache: YES — 1 hour TTL (topology changes infrequently)
    Timeout: 10 seconds
    Cost: Free (internal Neo4j)
    """
```

#### Tool 6: escalate_human

```python
def escalate_human(reason: str, suggested_actions: list = None) -> dict:
    """
    Escalate to human SRE. Use when confidence < 60%.

    Args:
        reason: Why escalation is needed
        suggested_actions: What the agent recommends the human try

    Returns:
        Confirmation that PagerDuty/Slack notification was sent.

    Implementation:
        1. Creates ServiceNow ticket with incident details
        2. Triggers PagerDuty webhook to page on-call engineer
        3. Posts to #incident-response Slack channel with summary
        4. Includes agent's full investigation trace for the human

    Cache: NO — escalations are unique events
    Timeout: 10 seconds
    Cost: Free (internal integrations)
    """
```

---

## 6. THE REACT LOOP — STEP-BY-STEP WALKTHROUGH

### Real Example: Payment Service Error Rate Spike

```
INPUT: "Payment service error rate jumped from 0.1% to 15% in the last 10 minutes"

╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 1                                                          ║
║  Model: GPT-4o-mini (iteration < 3, cheap model)                     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  THOUGHT: "I need to see what's happening in the payment service     ║
║            logs. Let me query for recent errors."                     ║
║                                                                       ║
║  ACTION: query_logs(service="payment-svc",                            ║
║                     time_range="last_15_minutes",                     ║
║                     keyword="ERROR")                                  ║
║                                                                       ║
║  ELK RETURNS: 52,847 log entries                                      ║
║                                                                       ║
║  COMPRESSED TO:                                                       ║
║    Log summary (52,847 total logs, 487 errors/warnings):             ║
║    [487x] Connection refused to DB (10:15:32 → 10:45:00)            ║
║    [12x]  Timeout connecting to payment gateway                      ║
║    [3x]   Circuit breaker opened for DB pool                         ║
║                                                                       ║
║  TOKENS USED: ~380 (compressed from 52K)                              ║
║  COST: $0.0001 (GPT-4o-mini)                                          ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 2                                                          ║
║  Model: GPT-4o-mini                                                   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  THOUGHT: "The logs show DB connection refused errors. Let me        ║
║            check the database connection pool metrics to see if      ║
║            the pool is exhausted."                                    ║
║                                                                       ║
║  ACTION: search_metrics(service="payment-svc",                        ║
║                         metric_name="db_connection_pool_usage")       ║
║                                                                       ║
║  PROMETHEUS RETURNS: 180 data points (30 min of 10-sec intervals)    ║
║                                                                       ║
║  COMPRESSED TO:                                                       ║
║    Metrics summary:                                                   ║
║    db_connection_pool_usage: current=100.0, avg=45.2 ⚠️ ANOMALY     ║
║    db_connection_pool_size: current=100, avg=100 ✓ normal            ║
║    (Pool is at 100/100 = fully exhausted)                             ║
║                                                                       ║
║  TOKENS USED: ~220 (compressed from 8K)                               ║
║  COST: $0.0001 (GPT-4o-mini)                                          ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 3                                                          ║
║  Model: GPT-4o (switched to expensive model for correlation)         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  THOUGHT: "Root cause is likely DB connection pool exhaustion.        ║
║            Let me check if we've seen this before — there might       ║
║            be a known fix."                                           ║
║                                                                       ║
║  ACTION: query_tickets(search_query="DB connection pool exhausted     ║
║                                 payment service")                     ║
║                                                                       ║
║  SERVICENOW RETURNS: 5 matching tickets                               ║
║                                                                       ║
║  COMPRESSED TO:                                                       ║
║    Similar incidents found:                                           ║
║    1. INC-2024-0156: "Payment DB pool exhaustion" (3 weeks ago)       ║
║       Root cause: Connection leak in v2.3.1                           ║
║       Resolution: Restarted pgbouncer, deployed fix v2.3.2            ║
║    2. INC-2024-0089: "DB pool full" (2 months ago)                    ║
║       Root cause: Long-running transaction holding connections        ║
║       Resolution: Killed long transaction, added statement timeout    ║
║                                                                       ║
║  TOKENS USED: ~410                                                    ║
║  COST: $0.001 (GPT-4o)                                                ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔════════════════════ `_` ═════════════════════════════════════════════╗
║  ITERATION 4                                                          ║
║  Model: GPT-4o                                                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  THOUGHT: "Similar incident from 3 weeks ago was a connection leak.  ║
║            We deployed v2.3.4 recently. Let me check the runbook     ║
║            for proper remediation steps."                             ║
║                                                                       ║
║  ACTION: search_kb(query="payment service DB connection pool          ║
║                         exhaustion remediation")                      ║
║                                                                       ║
║  CONFLUENCE + GRAPHRAG RETURNS: Runbook sections                      ║
║                                                                       ║
║  COMPRESSED TO:                                                       ║
║    Runbook: DB Connection Pool Issues (PAY-RB-014)                   ║
║    Step 1: Check pool status: `pgbouncer -c payment_pool`            ║
║    Step 2: If pool full: `systemctl restart pgbouncer`               ║
║    Step 3: Monitor error rate for 5 minutes post-restart              ║
║    Step 4: If persists: check for connection leaks in app logs        ║
║                                                                       ║
║    GraphRAG dependency info:                                          ║
║    payment-svc → depends on → db-pool (pgbouncer)                    ║
║    payment-svc → depends on → redis-cache (healthy)                   ║
║    3 other services also depend on this db-pool                      ║
║                                                                       ║
║  TOKENS USED: ~680                                                    ║
║  COST: $0.002 (GPT-4o)                                                ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 5: FINAL REPORT                                            ║
║  Model: GPT-4o                                                        ║
║  Action: No tool call → Produces final diagnostic report              ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  OUTPUT (JSON):                                                       ║
║  {                                                                    ║
║    "root_cause": "Database connection pool exhaustion caused by       ║
║                   possible connection leak in payment-svc v2.3.4",    ║
║    "confidence": 0.87,                                                ║
║    "evidence": [                                                      ║
║      {"claim": "487 DB connection refused errors in last 30 min",    ║
║       "source": "query_logs",                                         ║
║       "detail": "Errors started 10:15:32, ongoing"},                  ║
║      {"claim": "DB pool at 100% utilization (100/100)",               ║
║       "source": "search_metrics",                                     ║
║       "detail": "Avg was 45%, spiked to 100% at 10:15"},              ║
║      {"claim": "Similar incident 3 weeks ago was connection leak",    ║
║       "source": "query_tickets",                                      ║
║       "detail": "INC-2024-0156, v2.3.1 had same issue"},              ║
║      {"claim": "Runbook recommends pgbouncer restart",                ║
║       "source": "search_kb",                                          ║
║       "detail": "Runbook PAY-RB-014, Step 2"}                         ║
║    ],                                                                 ║
║    "remediation": [                                                   ║
║      "1. Immediate: Restart connection pooler (pgbouncer)",           ║
║      "2. Short-term: Check v2.3.4 for connection leak regression",    ║
║      "3. Preventive: Add pool usage alert at 80%",                    ║
║      "4. Preventive: Add connection leak detection test"              ║
║    ],                                                                 ║
║    "needs_human_review": true                                         ║
║  }                                                                    ║
║                                                                       ║
║  VALIDATOR: ✓ All claims cite tools that were actually called         ║
║             ✓ JSON schema valid                                      ║
║             ✓ Confidence 0.87 > 0.60 threshold                        ║
║                                                                       ║
║  INVESTIGATION COMPLETE.                                              ║
║  ──────────────────────────────────                                   ║
║  Total time: 87 seconds                                               ║
║  Total tokens: 8,420                                                  ║
║  Total cost: $0.08                                                    ║
║  Tools used: query_logs, search_metrics, query_tickets, search_kb     ║
║  Iterations: 5 (of max 10)                                            ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 7. HALLUCINATION PREVENTION

### The Evidence-Based Output System

```
PROBLEM: LLMs hallucinate. They make up plausible-sounding root causes
         that aren't supported by data.

EXAMPLE OF HALLUCINATION:
  Agent calls query_logs → finds DB errors
  Agent calls search_metrics → finds pool exhaustion
  Agent produces report: "Root cause: DNS resolution failure"
  ← DNS was NEVER mentioned in any tool result. The LLM made it up.

SOLUTION: THREE-LAYER DEFENSE

LAYER 1: SYSTEM PROMPT RULE
  "EVERY claim in your final report MUST include [Source: tool_name].
   If you cannot cite a tool result, do not make the claim."

LAYER 2: STRUCTURED JSON SCHEMA
  The output schema REQUIRES an "evidence" array where each entry has:
    - claim: "DB pool at 100% utilization"
    - source: "search_metrics"  ← MUST be a tool that was actually called
    - detail: "100/100 connections used"

LAYER 3: POST-GENERATION VALIDATOR (Code)
  After the LLM generates the report, Python code validates:
    1. Parse JSON → if invalid, reject and ask LLM to fix
    2. For each evidence entry:
       - Check that 'source' is in the set of tools actually called
       - If source not in called tools → REJECT as hallucination
    3. Check confidence score is present and between 0.0-1.0

  If validation fails:
    → Send rejection message back to LLM
    → "Your report cites source 'get_dns_records' but that tool was
       never called. Available sources: [query_logs, search_metrics,
       query_tickets, search_kb]. Please revise."
    → LLM regenerates with correct citations
```

### The Validator Implementation

```python
def _validate_report(self, report_json, tool_calls_made):
    """Validate LLM report against actual tool results."""
    tools_called = {tc.tool_name for tc in tool_calls_made}

    # 1. Valid JSON?
    try:
        report = json.loads(report_json)
    except json.JSONDecodeError:
        return None, "Invalid JSON"

    # 2. Required fields present?
    for field in ["root_cause", "confidence", "evidence", "remediation"]:
        if field not in report:
            return None, f"Missing field: {field}"

    # 3. Evidence sources verified?
    for evidence in report["evidence"]:
        source = evidence.get("source", "")
        if source not in tools_called:
            return None, f"Hallucinated source: {source} not in {tools_called}"

    # 4. Confidence is reasonable?
    conf = report.get("confidence", 0)
    if not (0 <= conf <= 1):
        return None, f"Invalid confidence: {conf}"

    return report, "VALID"
```

---

## 8. COST ENGINEERING

### Model Routing Strategy

```
THE INSIGHT:
  Not every step in an investigation needs GPT-4o.

  Iteration 1-2: "Query logs and metrics" → SIMPLE task
    The LLM just needs to decide which tool to call.
    GPT-4o-mini handles this perfectly. Cost: $0.15/1M tokens.

  Iteration 3-5: "Correlate findings across systems" → COMPLEX task
    The LLM needs to reason: "DB errors + pool exhaustion + similar ticket
    = connection leak regression."
    GPT-4o is better at this. Cost: $2.50/1M tokens.

  Final report: "Synthesize all findings into structured report" → COMPLEX
    GPT-4o.

ROUTING LOGIC:
  def _select_model(self, iteration):
      if iteration < 3:  return "gpt-4o-mini"
      else:              return "gpt-4o"

COST BREAKDOWN PER INVESTIGATION (5 iterations):
  Iterations 1-2 (GPT-4o-mini): ~2000 tokens × $0.15/1M = $0.0003
  Iterations 3-5 (GPT-4o):      ~6000 tokens × $2.50/1M = $0.015
  History summarization (mini):  ~1000 tokens × $0.15/1M = $0.00015
  ─────────────────────────────────────────────────────────────
  TOTAL: ~$0.015 per investigation

  (Without routing — all GPT-4o: ~$0.035 per investigation)
  SAVINGS: 57% cost reduction per investigation.

AT SCALE (1000 investigations/day):
  With routing: $15/day = $5,475/year
  Without routing: $35/day = $12,775/year
  All-GPT-4o-mini (quality too low): N/A (can't do complex reasoning)

  The routing sweet spot: cheap model for mechanical steps,
  expensive model for reasoning steps.
```

---

## 9. DEPLOYMENT & INFRASTRUCTURE

### Production Architecture

```
                    ┌──────────────────────────────────┐
                    │         KUBERNETES CLUSTER         │
                    │                                   │
  PagerDuty ──────> │  ┌─────────────────────────────┐  │
  Webhook           │  │    Kafka Queue (ingest)     │  │
                    │  └──────────┬──────────────────┘  │
                    │             │                     │
                    │  ┌──────────▼──────────────────┐  │
                    │  │  IncidentAgent Pods         │  │
                    │  │  (auto-scale: 1-20 pods)    │  │
                    │  │                              │  │
                    │  │  Each pod handles 5          │  │
                    │  │  concurrent investigations   │  │
                    │  └──────────┬──────────────────┘  │
                    │             │                     │
                    │  ┌──────────▼──────────────────┐  │
                    │  │  Redis Cluster (cache)      │  │
                    │  │  (3 nodes, 50GB)            │  │
                    │  └─────────────────────────────┘  │
                    │                                   │
                    └───────────────────────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
              ┌────────┐ ┌────────┐ ┌──────────────┐
              │ ELK    │ │ Prom.  │ │ ServiceNow   │
              │ (logs) │ │ (metric)│ │ (tickets)   │
              └────────┘ └────────┘ └──────────────┘
                    │
              ┌────────┐    ┌──────────────┐
              │ Neo4j  │    │ Confluence   │
              │ (graph)│    │ + Qdrant     │
              └────────┘    │ (knowledge)  │
                            └──────────────┘
```

### Deployment Details

```
KUBERNETES DEPLOYMENT:
  - Agent pods: Stateless → can scale horizontally
  - HPA: Auto-scale based on Kafka queue depth
    (If >10 pending incidents → spin up more pods)
  - Resource limits: 1 CPU, 2GB RAM per pod (agent is lightweight,
    most work is done by external systems and LLM API)
  - Rolling updates: Zero-downtime deployments

LATENCY BUDGET (87 seconds total):
  - Alert → Kafka: 1 sec
  - Kafka → Agent: 2 sec
  - 5 LLM API calls: 5 × 8 sec = 40 sec
  - 5 tool calls (ELK, Prom, ServiceNow, etc.): 5 × 5 sec = 25 sec
  - Context compression: 5 sec
  - Output validation: 2 sec
  - Report delivery: 2 sec
  TOTAL: ~77 seconds (target: <90 sec ✓)

RELIABILITY:
  - If OpenAI is down: Failover to Azure OpenAI or self-hosted Llama 3.1
  - If a tool (ELK/Prom/ServiceNow) is down: Agent gets error → escalates
  - If agent pod crashes: Kubernetes reschedules, Kafka replays
  - If Redis cache is down: Bypass cache, slower but functional
```

---

## 10. METRICS & ROI

### The Numbers That Matter

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INCIDENT AGENT METRICS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  TIME SAVINGS:                                                      │
│  Manual investigation:    20-40 minutes (avg 30 min)                │
│  Agent investigation:     87 seconds (avg)                          │
│  Improvement:             95% reduction in investigation time       │
│                                                                     │
│  ACCURACY:                                                          │
│  Root cause accuracy:     87% (validated against post-mortems)      │
│  (13% of cases escalated to human — agent knew its limits)          │
│                                                                     │
│  COST:                                                              │
│  LLM cost per investigation: $0.08 (with model routing)             │
│  LLM cost without routing:  $0.35 (all GPT-4o)                      │
│  Monthly cost (1000 inv/month): $80                                 │
│                                                                     │
│  BUSINESS IMPACT:                                                   │
│  Time saved per incident:  ~28 minutes                              │
│  SLA penalty avoidance:    $50K-$500K per major outage minute       │
│  Engineers freed up:       500 hours/month reclaimed for real work  │
│  MTTR reduction:           30 min → 2 min (93% faster)              │
│                                                                     │
│  ADOPTION:                                                          │
│  Teams using it:           3 SRE teams                              │
│  Investigations/month:     ~1,000                                   │
│  Escalation rate:          13% (agent handles 87% autonomously)     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### ROI Calculation (Memorize This for Interviews)

```
"Let me walk you through the ROI.

 Before IncidentAgent:
   1,000 incidents/month × 30 minutes each = 500 engineer-hours/month
   At $100/hour loaded cost = $50,000/month in engineer time
   Plus SLA penalties: ~$200,000/month (not all incidents cause SLA hits,
   but the ones that do are expensive)

 After IncidentAgent:
   Agent handles 87% autonomously = 870 incidents resolved without human
   130 incidents escalated to human (but with full investigation already done)
   Human time per escalated incident: 10 min (just review + decide)
   130 × 10 min = 22 hours/month
   Agent cost: $80/month (LLM API)
   Total cost: $2,300/month (22 hrs × $100/hr + $80 LLM)

 NET SAVINGS: $50,000 - $2,300 = $47,700/month = $572,400/year

 Plus: the agent catches incidents faster (87 sec vs 30 min),
 which reduces SLA penalties by an estimated $150,000/month.

 TOTAL ANNUAL VALUE: ~$2.3M (labor savings + SLA penalty avoidance)"
```

---

## 11. 15 INTERVIEW QUESTIONS WITH EXACT ANSWERS

### Q1: "Walk me through how IncidentAgent works end-to-end."

```
"When an alert fires — say 'payment service error rate 15%' — a webhook
triggers the agent. The agent uses a ReAct loop: it reasons about what
data it needs, calls the appropriate tool (query_logs, search_metrics,
etc.), observes the result, and repeats.

In this example: it queries logs → finds DB connection errors. Queries
metrics → finds 100% pool exhaustion. Searches tickets → finds a similar
incident from 3 weeks ago. Gets the runbook → remediation steps. Then
produces a structured JSON report with root cause, evidence citations,
and remediation steps.

The entire investigation takes 87 seconds instead of 30 minutes.
Root cause accuracy is 87%, validated against post-mortem reports."
```

### Q2: "What was the hardest engineering challenge?"

```
"Context window explosion. My first version dumped raw tool results
into the context. A single query_logs call returned 50,000+ tokens.
After 3 tool calls, the context window was full and the LLM couldn't
reason about earlier findings — it would hallucinate because it
literally couldn't 'see' the earlier evidence.

I solved this with a three-layer compression system. Layer 1: each tool
result is compressed before entering context. For logs, I filter to
ERROR level, deduplicate, and count occurrences. 52K tokens becomes
380 tokens. Layer 2: after 5 tool calls, I summarize all history using
GPT-4o-mini. Layer 3: a hard 30K token cap with emergency trimming.

This was the difference between the agent working and not working.
The naive approach of dumping raw data failed. Compressed, structured
summaries worked."
```

### Q3: "How do you prevent the agent from getting stuck in loops?"

```
"Three mechanisms. First, a hard max_iterations limit of 10 — the agent
can never loop more than 10 times. Second, I track consecutive errors
per tool — if the same tool fails 3 times in a row, the harness blocks
further calls to that tool and tells the LLM to try a different approach.
Third, the system prompt explicitly says 'If a tool fails, try a
different approach or escalate to human.'

I also implemented a token budget — if total tokens exceed 30K, the
investigation stops and escalates. This prevents runaway costs."
```

### Q4: "How do you handle hallucinations?"

```
"Three layers. First, the system prompt requires every claim to cite a
source: 'Every claim MUST include [Source: tool_name].' Second, the
output is structured JSON with an 'evidence' array — each evidence
entry must have a 'source' field. Third, a post-generation validator
checks that every cited source is a tool that was actually called. If
the LLM cites 'get_dns_records' but that tool was never called, the
report is rejected and the LLM is asked to revise.

This caught hallucinations where the agent would claim 'root cause is
DNS' when no DNS tool was ever called."
```

### Q5: "Why ReAct instead of plan-and-execute?"

```
"I tested both. Plan-and-execute creates a full plan upfront, then
executes each step. The problem with incidents is that the plan CHANGES
based on what you find. After querying logs, you might discover the
issue is network, not application — and the original plan is useless.

ReAct adapts at each step. The agent sees the log results and pivots.
This adaptive behavior is critical for incident investigation, where
early findings determine the direction of the entire investigation."
```

### Q6: "How did you choose the tools?"

```
"I mapped the human investigation process: what does an on-call engineer
actually DO? They check logs (Splunk), metrics (Prometheus), past
tickets (ServiceNow), runbooks (Confluence), and topology (network
tools). I built one tool per data source.

The key principle: give the agent just enough tools to investigate,
but not so many that it gets confused. Six tools is the sweet spot.
More than 10 and the LLM starts choosing wrong tools. I also gave each
tool a precise JSON schema so the LLM knows exactly what arguments to
pass."
```

### Q7: "What happens when the agent's diagnosis is wrong?"

```
"Two safety nets. First, every report includes a confidence score.
If confidence < 60%, the agent escalates to human instead of acting.
Second, the report always includes 'needs_human_review: true' for
actions that have blast radius (restarts, deletions, config changes).

The agent never auto-remediates. It produces a diagnostic report and
recommendation. The human SRE reviews it and makes the GO/NO-GO
decision. The agent's job is INVESTIGATION, not REMEDIATION.

That said, for low-risk, well-understood actions (like clearing a
cache), I'm building an auto-remediation path with additional
guardrails."
```

### Q8: "How do you optimize cost?"

```
"Model routing. Not every step needs GPT-4o. Iterations 1-2 are
information gathering — 'query logs, query metrics.' GPT-4o-mini handles
this perfectly at 16× lower cost. Iterations 3+ require correlation and
reasoning — 'DB errors + pool exhaustion + similar ticket = connection
leak.' That's where GPT-4o earns its cost.

This routing saves 57% per investigation. At 1,000 investigations per
month, that's a meaningful difference. I also cache tool results in
Redis — topology and runbooks don't change often, so caching avoids
redundant queries."
```

### Q9: "What if OpenAI goes down?"

```
"Multi-layer fallback. The LLM gateway (CostLens) has a fallback chain:
primary model → backup model → self-hosted model. If GPT-4o is down,
it falls back to Azure OpenAI. If Azure is down, it falls back to
self-hosted Llama 3.1 8B on our GPU infrastructure.

For tools, if ELK or Prometheus is down, the agent gets an error and
either tries a different tool or escalates to human. The system is
designed to FAIL SAFE — if any component fails, the incident escalates
to human rather than producing a wrong diagnosis."
```

### Q10: "How do you measure root cause accuracy?"

```
"I validate against post-mortem reports. After every incident, the SRE
team writes a post-mortem with the confirmed root cause. I compare the
agent's diagnosis to the post-mortem conclusion.

87% of the time, the agent's top hypothesis matches the post-mortem root
cause. The 13% gap is mostly novel issues the agent hasn't seen before —
which is why it escalates to human in those cases. As the agent
accumulates more historical incidents in its knowledge base, accuracy
improves over time."
```

### Q11: "How would you scale this to 10,000 incidents per day?"

```
"The agent orchestrator is stateless and runs in Kubernetes with
horizontal pod autoscaling. At 10,000 incidents/day, we'd run ~20 pods
(each handles 5 concurrent investigations). Kafka buffers incoming
incidents so spikes don't overwhelm the system.

The bottleneck isn't the agent — it's the external systems. 10,000
investigations × 5 tool calls each = 50,000 queries to ELK, Prometheus,
and ServiceNow per day. We need to ensure those systems can handle the
load. Redis caching helps a lot — cached topology and runbook queries
don't hit the backend.

LLM cost at 10K/day: ~$800/day = $24K/month. Still trivial compared
to the $500K+/month in engineer time saved."
```

### Q12: "What's the difference between this and a standard runbook automation?"

```
"Runbook automation is deterministic: IF alarm_type=X THEN run script Y.
It only works for known issues with pre-defined playbooks.

IncidentAgent is adaptive: it investigates UNKNOWN issues by gathering
data, correlating findings, and forming hypotheses. It can handle novel
incidents that don't have a pre-existing runbook. It can also ADAPT
mid-investigation — if logs show the issue is network instead of
application, it pivots to check network topology instead of following
a fixed script.

That said, for known alarm types with known fixes, simple runbook
automation is better — faster, cheaper, no LLM needed. IncidentAgent
is for the 30% of incidents that DON'T match a known pattern."
```

### Q13: "How did you integrate GraphRAG into this?"

```
"The search_kb tool uses GraphRAG instead of plain vector search. When
the agent searches for 'payment DB connection pool,' it does:

1. Vector search: finds text chunks semantically similar to the query
2. Graph traversal: queries Neo4j for service dependencies
   ('payment-svc depends on db-pool which depends on PostgreSQL')

The vector results provide TEXTUAL context (what the runbook says).
The graph results provide RELATIONAL context (what services are
affected). The LLM reasons over both.

This improved answer accuracy from 79% to 91% because the agent could
answer relational questions like 'what else is affected by this DB
pool issue?' that vector-only RAG couldn't handle."
```

### Q14: "How do you secure the agent? What if someone injects a prompt?"

```
"I deployed AgentGuard as a defense layer. Three layers:

Input filter: Detects prompt injection patterns before the incident
description reaches the LLM. Since incident descriptions come from
monitoring systems (not user input), injection risk is lower, but
I still scan for known attack patterns.

Tool validator: Every tool call is checked against a permission matrix.
The agent can only query READ-ONLY data (logs, metrics, tickets). It
cannot modify, delete, or execute changes. The escalate_human tool is
the only action tool, and it just sends a notification.

Output filter: The diagnostic report is scanned for sensitive data
leakage before delivery. AgentGuard checks that no internal IPs,
passwords, or secrets are in the report."
```

### Q15: "If you could redesign this today, what would you change?"

```
"Three things. First, I'd add a memory layer — the agent should learn
from every investigation. Right now it starts fresh each time. If it
investigated a similar incident yesterday, it should recall that context.
I'm exploring using my GraphRAG system for this — store investigation
outcomes as graph nodes and retrieve similar past investigations.

Second, I'd implement auto-remediation for low-risk, well-understood
actions. Right now the agent only investigates. For known fixes
(like 'restart pgbouncer when pool is exhausted'), it should be able
to execute the fix with proper guardrails.

Third, I'd use DPO-fine-tuned Llama 3.1 instead of GPT-4o. We've shown
that a fine-tuned 8B model can match GPT-4o on this specific task at
1/10th the cost. The fine-tuning data is the 1,000+ investigations
we've accumulated."
```

---

## 12. THE 90-SECOND VERBAL PITCH

### Memorize This — Deliver It When Asked "Tell Me About Your AI Project"

```
[0-15 sec — THE HOOK]
"At AT&T, when a production incident hits — like a 5G tower outage or
payment gateway failure — the on-call engineer spends 20 to 40 minutes
just GATHERING information across 6 different systems before they can
even start fixing the problem. That's 30 minutes of SLA clock ticking."

[15-40 sec — WHAT I BUILT]
"I built IncidentAgent — an autonomous AI agent that automates the
investigation phase. It uses the ReAct pattern: it reasons about what
data it needs, calls tools to query logs, metrics, tickets, runbooks,
and network topology, correlates the findings, and produces a structured
diagnostic report with root cause, evidence, and remediation steps."

[40-60 sec — THE CHALLENGE & SOLUTION]
"The hardest part was context engineering. A single log query returns
50,000 tokens of raw data. After 3 tool calls, the context window was
full and the agent couldn't reason. I built a three-layer compression
system — tool-specific compressors that extract signal from noise,
history summarization with GPT-4o-mini, and a hard token budget.
52,000 tokens becomes 380 tokens with the key information intact."

[60-75 sec — THE RESULT]
"The result: investigation time dropped from 30 minutes to 90 seconds.
Root cause accuracy is 87%, validated against post-mortem reports.
Cost per investigation is 8 cents using model routing — GPT-4o-mini for
information gathering, GPT-4o for correlation and synthesis."

[75-90 sec — THE REFLECTION]
"The biggest lesson: the agent's quality is determined by the HARNESS,
not the model. A well-engineered harness with GPT-4o-mini outperformed
a naive harness with GPT-4o. The harness controls context management,
error handling, tool validation, and output structuring. That's where
the engineering value is."
```

### Practice Tips

```
1. TIME YOURSELF: Should take 75-90 seconds. Not longer.

2. EMPHASIZE KEY NUMBERS:
   - "30 minutes to 90 seconds" (pause after saying this)
   - "87% accuracy"
   - "8 cents per investigation"
   - "52,000 tokens to 380"

3. USE HAND GESTURES: When explaining compression, gesture "big to small"
   to emphasize the reduction.

4. LEAN FORWARD: Show energy. This is exciting work.

5. END WITH THE REFLECTION: The "harness > model" insight shows senior
   engineering judgment. This is what separates you from junior candidates.
```
