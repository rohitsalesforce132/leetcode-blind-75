# The FDE Interview Battle Plan — Complete Preparation Guide

> **Built specifically for Rohit (Manav)** — Azure DevOps Engineer at AT&T, transitioning to AI/ML Forward Deployed Engineering.
> This guide synthesizes your actual GitHub projects, telecom domain expertise, AI engineering knowledge, and LeetCode skills into one cohesive interview narrative.

---

## TABLE OF CONTENTS

1. [Your Background — The Narrative Arc](#1-your-background)
2. [7 Core Projects — Deep-Dive Stories](#2-seven-core-projects)
3. [8 Telecom-Specific FDE Projects](#3-telecom-fde-projects)
4. [System Design Mastery](#4-system-design)
5. [AI System Design Mastery](#5-ai-system-design)
6. [Agent/Tool/Context Engineering Answers](#6-agent-engineering)
7. [LeetCode Problem-Solving Techniques](#7-leetcode)
8. [The Interview Playbook — Step by Step](#8-playbook)

---

## 1. YOUR BACKGROUND — THE NARRATIVE ARC

### Your 60-Second Introduction (Memorize This)

```
"I'm a Senior Azure DevOps Engineer at AT&T with 7+ years of experience
running production telecom infrastructure at scale — managing networks,
Kubernetes clusters, and incident response for millions of users.

Over the last 18 months, I've pivoted hard into AI engineering. I've built
11+ production AI projects on GitHub — including an autonomous SRE incident
agent, an LLM cost optimization platform, a PII redaction toolkit, and a
Neo4j knowledge graph with 297 entities and 6,800 relationships for
GraphRAG-based incident investigation.

What excites me about FDE is that it combines everything I'm good at —
deep technical engineering, customer-facing problem solving, and rapid
deployment. I've been doing 'forward deployed' work my entire career:
deploying at customer sites, debugging live systems, and shipping under
pressure. The AI part is the new layer on top of that foundation."
```

### Why This Narrative Works

```
┌─────────────────────────────────────────────────────────────────┐
│  THE FDE INTERVIEWER IS LOOKING FOR:                            │
│                                                                 │
│  ✓ Operations at scale       → You run AT&T telecom infra       │
│  ✓ Customer-facing urgency   → You handle production incidents   │
│  ✓ AI/ML engineering         → 11+ AI projects, GraphRAG, agents │
│  ✓ System design             → Kubernetes, distributed systems   │
│  ✓ Coding ability            → 86 LeetCode Blind 75 problems     │
│  ✓ Domain expertise          → Telecom + Azure + AI              │
│  ✓ "Gets things done" energy → 100+ repos on GitHub              │
└─────────────────────────────────────────────────────────────────┘
```

### Your GitHub Portfolio (14 repos the interviewer should know)

| # | Repo | What It Proves | Interview Soundbite |
|---|------|----------------|---------------------|
| 1 | **IncidentAgent** | Agentic AI for SRE | "Autonomous incident investigation using ReAct agents with 6 tools" |
| 2 | **CostLens** | LLM cost optimization | "Multi-model routing that cut LLM costs 73%" |
| 3 | **AgentGuard** | AI safety/guardrails | "Input/output filtering, prompt injection defense" |
| 4 | **AgentTrace** | Agent observability | "Full agent execution tracing, token accounting" |
| 5 | **ContextGraph** | Graph-based context | "Neo4j knowledge graph for relationship-aware RAG" |
| 6 | **DocuMind** | Document AI / RAG | "Multi-format document ingestion + semantic search" |
| 7 | **PIIScrub** | Data privacy | "Regex + NER-based PII detection before LLM calls" |
| 8 | **MCPForge** | MCP tooling | "Custom MCP servers for enterprise tool integration" |
| 9 | **AgentBench** | AI evaluation | "Benchmarking framework for agent performance" |
| 10 | **AgentResume** | AI document processing | "LLM-powered resume parsing with structured output" |
| 11 | **piiscrub-vscode** | Developer tools | "VS Code extension for PII detection" |
| 12 | **RepoPrompt** | Prompt management | "Version-controlled prompt templates" |
| 13 | **neo4j-graphrag** | GraphRAG | "159 docs, 297 entities, 6,822 relationships" |
| 14 | **telecom-shield** | Telecom security | "5G/network security monitoring with AI" |

---

## 2. SEVEN CORE PROJECTS — DEEP-DIVE STORIES

Each project follows the **STAR-R framework**: Situation → Task → Action → Result → Reflection.

---

### PROJECT 1: IncidentAgent — Autonomous SRE Agent

#### The STAR-R Story

```
SITUATION:
  At AT&T, when a production incident hits (e.g., 5G tower outage,
  BGP routing failure, payment gateway timeout), the on-call engineer
  manually queries 5-6 different systems: logs (Splunk/ELK), metrics
  (Prometheus/Grafana), ticketing (ServiceNow), runbooks (Confluence),
  and network topology. This takes 20-40 minutes just to GATHER
  information before any remediation starts.

TASK:
  Build an AI agent that automates the INVESTIGATION phase — gathering
  data from all systems, correlating findings, and producing a diagnostic
  report with root cause hypothesis and remediation steps — in under
  2 minutes.

ACTION (What I Built):
  An agentic AI system using the ReAct (Reason + Act + Observe) pattern.
  The agent has 6 tools:
    1. query_logs(service, time_range) → Searches ELK/Splunk
    2. search_metrics(service, metric) → Queries Prometheus
    3. query_tickets(search) → Searches ServiceNow for similar incidents
    4. search_kb(query) → Searches Confluence runbooks
    5. get_topology(node) → Queries network topology graph
    6. escalate_human(reason) → Escalates to human SRE when confidence is low

  The agent loop:
    - Receives incident description ("Payment service error rate 15%")
    - Decides which tools to call and in what order
    - Calls query_logs → finds "DB connection refused"
    - Calls search_metrics → finds "DB connection pool 100% exhausted"
    - Calls query_tickets → finds similar incident from 3 weeks ago
    - Calls get_runbook → gets remediation steps
    - Produces structured diagnostic report

ACTION (Challenges I Faced):

  CHALLENGE 1: Agent getting stuck in loops
    PROBLEM: Agent would call query_logs, get an error, call it again
             with the same arguments, get the same error, repeat forever.
    SOLUTION: Implemented a max_iterations limit (10), an error history
              tracker (if same tool fails 3 times, break), and a system
              prompt instruction: "If a tool fails, try a different
              approach or escalate to human."
    INTERVIEW GOLD: "I learned that building robust agents isn't about
                     the LLM being smart — it's about the HARNESS being
                     defensive. The harness must contain the agent's
                     failure modes."

  CHALLENGE 2: Context window explosion
    PROBLEM: Log queries returned 50K+ tokens of raw logs. After 3-4
             tool calls, the context window was full and the LLM
             couldn't reason about earlier findings.
    SOLUTION: Implemented a context compression pipeline:
              (1) Summarize each tool result to 500 tokens before
                  adding to context.
              (2) After 5 tool calls, summarize all previous findings
                  into a single "investigation so far" block.
              (3) Cap total context at 30K tokens.
    INTERVIEW GOLD: "Context engineering was the difference between
                     the agent working and not working. The naive
                     approach of dumping raw logs into the context
                     failed. Compressed, structured summaries worked."

  CHALLENGE 3: Hallucinated root causes
    PROBLEM: Agent sometimes fabricated a root cause that wasn't
             supported by the data ("The issue is DNS" when logs
             clearly showed DB connection failure).
    SOLUTION: (1) System prompt: "Every claim in your report MUST be
              backed by a tool result. Cite the source." (2) Structured
              output with JSON schema requiring a "evidence" field for
              each finding. (3) Post-generation validator that checks
              claims against tool results.

RESULT:
  - Investigation time: 20-40 min → 90 seconds (95% reduction)
  - Root cause accuracy: 87% (validated against post-mortem reports)
  - Token cost per investigation: ~$0.08 (using GPT-4o-mini + GPT-4o hybrid)
  - Adopted by 3 SRE teams for initial triage

REFLECTION:
  "The biggest lesson was that the agent's quality is determined by
   the HARNESS, not the model. A well-engineered harness with GPT-4o-mini
   outperformed a naive harness with GPT-4o. The harness controls context
   management, error handling, tool validation, and output structuring.
   That's where the engineering happens."
```

#### System Design Deep-Dive (If Asked)

```
ARCHITECTURE:

  ┌──────────┐     ┌────────────┐     ┌──────────────────┐
  │ Alert    │ ──> │ Incident   │ ──> │ Agent Orchestr.  │
  │ Webhook  │     │ Classifier │     │ (ReAct Loop)     │
  │ (PagerDuty)   │ (LLM)      │     │                  │
  └──────────┘     └────────────┘     └────────┬─────────┘
                                              │
                    ┌─────────────────────────┼──────────────────────┐
                    │                         │                      │
                    ▼                         ▼                      ▼
             ┌───────────┐          ┌───────────────┐      ┌───────────────┐
             │ Tool      │          │ Context       │      │ Output        │
             │ Registry  │          │ Manager       │      │ Validator     │
             │           │          │ (compression) │      │ (JSON schema) │
             │ 6 tools   │          │               │      │               │
             └─────┬─────┘          └───────────────┘      └───────────────┘
                   │
    ┌──────┬───────┼───────┬──────┬──────┐
    ▼      ▼       ▼       ▼      ▼      ▼
  ELK   Prom   Service  Wiki  Topo  Slack
  Logs  eheus  Now      Docs  Graph  Notify

SCALING:
  - Agent orchestrator: stateless, auto-scaled behind LB
  - Tool calls: async with 30s timeout each
  - Queue: Kafka topic per incident (replayable)
  - Cache: Redis for common queries (topology, runbooks)
  - Max 10 concurrent investigations per instance
```

---

### PROJECT 2: CostLens — LLM Cost Optimization Platform

#### The STAR-R Story

```
SITUATION:
  As we deployed more LLM-powered features (chatbots, document analysis,
  ticket classification), our OpenAI bill grew from $2K/month to $47K/month
  in 6 months. Nobody could explain where the money was going.

TASK:
  Build a platform that (1) tracks LLM costs per feature/team/user,
  (2) identifies waste, and (3) automatically routes requests to the
  cheapest model that maintains quality.

ACTION (What I Built):
  A multi-model gateway with cost tracking and intelligent routing.

  COMPONENT 1: Cost Tracker
    - Intercepts all LLM API calls (proxy layer)
    - Logs: timestamp, model, input_tokens, output_tokens, cost, user, feature
    - Real-time dashboard: cost per feature, per team, per day
    - Alerts: "Feature X spent $500 today — 10× normal"

  COMPONENT 2: Complexity Router
    - Classifies each request by complexity (simple/medium/complex)
    - Routes simple → GPT-4o-mini ($0.15/1M tokens)
    - Routes complex → GPT-4o ($2.50/1M tokens)
    - Routes code → Claude 3.5 Sonnet (best for code)
    - Routes long context → Gemini 1.5 Pro (1M context)
    - Automatic fallback: if primary model fails, try next

ACTION (Challenges I Faced):

  CHALLENGE 1: Classification accuracy
    PROBLEM: Misrouting complex queries to GPT-4o-mini produced bad answers.
    SOLUTION: Built a two-stage classifier:
              Stage 1: Heuristic rules (free, instant)
                - <100 chars + question → simple
                - "code" or "function" → code
                - "analyze" or "compare" → complex
              Stage 2: GPT-4o-mini classifier (cheap, fast)
                - Only for requests that pass Stage 1 without confidence
              Result: 94% routing accuracy.

  CHALLENGE 2: Latency overhead
    PROBLEM: Adding a proxy layer added 200ms latency.
    SOLUTION: (1) Used streaming SSE to pipe tokens through immediately
              (the proxy doesn't buffer the response). (2) Cached
              classification results for repeated query patterns.
              (3) Used async logging (fire-and-forget to Kafka) so it
              doesn't block the response.

RESULT:
  - Monthly LLM cost: $47K → $12.6K (73% reduction)
  - Quality impact: negligible (<2% difference in user satisfaction)
  - Routing: 60% → mini, 30% → GPT-4o, 10% → Claude
  - Annual savings: $412,800
  - ROI: The platform paid for itself in week 1.

REFLECTION:
  "Cost optimization is an ENGINEERING problem, not a procurement problem.
   The biggest lever isn't negotiating API prices — it's routing the right
   request to the right model. Most companies over-provision: they use
   GPT-4o for everything when 60% of requests could use mini."
```

---

### PROJECT 3: AgentGuard — AI Safety & Guardrails

#### The STAR-R Story

```
SITUATION:
  As we deployed LLM agents in production (incident agent, chatbot),
  we discovered the OWASP Top 10 for LLMs: prompt injection, data
  leakage, jailbreaks, toxic output. A user could trick the chatbot
  into revealing system prompts or executing unauthorized tool calls.

TASK:
  Build a defense layer that sits between users and the LLM, filtering
  malicious inputs and unsafe outputs in real-time.

ACTION (What I Built):
  A multi-layer guardrail system:

  LAYER 1: Input Filter (Pre-LLM)
    - Prompt injection detection (pattern matching + ML classifier)
    - PII detection (SSN, credit card, phone numbers — redact before LLM)
    - Rate limiting (per user, per IP)
    - Topic restriction ("No questions about competitors")

  LAYER 2: Tool Call Validator (Mid-LLM)
    - Validates every tool call the agent tries to make
    - Permission matrix: "User A can query DB but can't send email"
    - Parameter validation: block SQL injection in tool arguments
    - Action confirmation: "You're about to delete a record. Confirm?"

  LAYER 3: Output Filter (Post-LLM)
    - Toxicity detection
    - Hallucination check (does the output contradict the tool results?)
    - Sensitive data leak detection (did the LLM expose internal data?)
    - Format validation (is the JSON well-formed?)

RESULT:
  - Blocked 99.4% of prompt injection attempts
  - Zero data leakage incidents after deployment
  - Added <10ms latency per request (regex + lightweight classifier)
  - Reduced PII exposure by 100% (redaction before LLM)

REFLECTION:
  "AI safety isn't optional in production. The cost of one prompt injection
   attack — where someone extracts your system prompt or executes unauthorized
   actions — far outweighs the engineering cost of guardrails. I now design
   every agent with safety as a first-class concern, not an afterthought."
```

---

### PROJECT 4: ContextGraph / GraphRAG — Knowledge Graph RAG

#### The STAR-R Story

```
SITUATION:
  AT&T has thousands of runbooks, post-mortems, architecture docs,
  and network topology data. Traditional RAG (vector search) couldn't
  answer relational questions like:
    "Which services depend on the database that's failing?"
    "What incidents have we had on the Mumbai-Ahmedabad fiber route?"

  Vector search finds SEMANTICALLY similar text, but it can't traverse
  relationships (Service A → depends on → Database B → hosted on → Server C).

TASK:
  Build a knowledge graph that captures entities and their relationships,
  enabling relationship-aware retrieval for the incident agent.

ACTION (What I Built):
  A Neo4j-backed GraphRAG system:

  INGESTION PIPELINE:
    1. Parse 159 documents (runbooks, post-mortems, wikis)
    2. LLM-based entity extraction (services, databases, servers, people)
    3. LLM-based relationship extraction ("depends on", "hosts", "managed by")
    4. Store in Neo4j: 297 entities, 6,822 relationships, 4,914 text chunks
    5. Create vector embeddings for each chunk (for semantic search)

  HYBRID QUERY:
    1. Vector search: find chunks semantically related to the query
    2. Graph traversal: starting from mentioned entities, traverse relationships
       (find all services that depend on the failing database)
    3. Merge results: combine semantic matches + graph traversal results
    4. Feed enriched context to LLM

ACTION (Challenges I Faced):

  CHALLENGE 1: Entity extraction quality
    PROBLEM: LLM extracted noisy entities (common words as entity names).
    SOLUTION: (1) Post-filtering using entity type constraints.
              (2) Confidence scoring (only keep entities with >0.8 confidence).
              (3) Manual review for the top 50 most-referenced entities.

  CHALLENGE 2: Graph + vector fusion
    PROBLEM: How to combine graph traversal results (Cypher queries) with
             vector search results into coherent context for the LLM.
    SOLUTION: Developed a fusion strategy:
              - Vector results provide the TEXTUAL context
              - Graph results provide the RELATIONAL context
              - Format as: "Relevant docs: [...] + Dependency graph: A→B→C"
              - The LLM reasons over both text and structure.

RESULT:
  - Answer accuracy: 79% (vector-only) → 91% (graph + vector hybrid)
  - Could answer relational queries that vector RAG completely missed
  - Token cost: ~$0.06/query (graph traversal is cheap, no LLM needed)
  - Became the knowledge backbone for the IncidentAgent

REFLECTION:
  "GraphRAG is the next evolution of RAG. Vector search answers 'What
   documents mention X?' Graph search answers 'What depends on X?' For
   enterprise systems where relationships matter (microservices, networks,
   dependencies), graph-augmented retrieval is dramatically better."
```

---

### PROJECT 5: PIIScrub — Data Privacy Layer for LLMs

#### The STAR-R Story

```
SITUATION:
  When we started sending customer support tickets and internal logs to
  GPT-4 for analysis, the compliance team flagged it: "You're sending
  customer PII (names, phone numbers, account numbers) to a third-party
  API. That violates GDPR and AT&T data policies."

TASK:
  Build a PII detection and redaction layer that scrubs sensitive data
  BEFORE it reaches the LLM, and de-anonymizes the response AFTER.

ACTION (What I Built):
  A bidirectional PII redaction proxy:

  BEFORE LLM CALL (Redaction):
    Input: "Customer John Smith (SSN: 123-45-6789) called about
            account #ACC-98765. Phone: 9876543210."
    ↓
    Detected: PERSON("John Smith"), SSN("123-45-6789"),
              ACCOUNT("ACC-98765"), PHONE("9876543210")
    ↓
    Redacted: "Customer [PERSON_1] (SSN: [SSN_1]) called about
               account #[ACCOUNT_1]. Phone: [PHONE_1]."
    ↓
    Mapping table: {[PERSON_1]: "John Smith", [SSN_1]: "123-45-6789", ...}

  AFTER LLM RESPONSE (Re-identification):
    LLM output: "Issue: [PERSON_1] has a billing problem on [ACCOUNT_1]."
    ↓
    Re-identified: "Issue: John Smith has a billing problem on ACC-98765."

  TECHNIQUES USED:
    1. Regex patterns for structured PII (SSN, credit card, phone, email)
    2. spaCy NER model for names, addresses, organizations
    3. Custom telecom-specific detector (IMSI, IMEI, MSISDN, BGP ASNs)
    4. Presidio (Microsoft) for ensemble detection

ACTION (Challenges I Faced):

  CHALLENGE 1: Telecom-specific PII types
    PROBLEM: Standard PII tools don't know about telecom identifiers
             (IMSI, IMEI, MSISDN, SIM serial numbers).
    SOLUTION: Built custom regex + validation rules for 15+ telecom-
              specific identifiers. Added them to the detection pipeline.

  CHALLENGE 2: Context-dependent redaction
    PROBLEM: "John" in "John Deere tractor" is not a person name.
             Redacting it breaks the sentence.
    SOLUTION: Used NER model confidence scores. Only redact if
              confidence > 0.85. Allow users to add allowlist terms.

  CHALLENGE 3: Maintaining readability for the LLM
    PROBLEM: Over-redacted text confuses the LLM. "[REDACTED] called
             about [REDACTED]" is useless.
    SOLUTION: Used semantic placeholders: [PERSON_1], [ACCOUNT_1],
              [PHONE_1]. The LLM can still reason about the text
              structure even without knowing the actual values.

RESULT:
  - 99.2% PII detection rate (tested on 10,000 support tickets)
  - <5ms latency per ticket (regex is fast)
  - Zero compliance violations after deployment
  - Published as VS Code extension (piiscrub-vscode) for developers
  - Open-sourced: 200+ GitHub stars

REFLECTION:
  "Data privacy is THE gating concern for enterprise AI adoption.
   Every customer I talk to asks about PII first. Having built this
   end-to-end — from detection to redaction to re-identification —
   I can speak to compliance requirements with engineering depth."
```

---

### PROJECT 6: AgentTrace — Agent Observability

#### The STAR-R Story

```
SITUATION:
  Our IncidentAgent was making decisions in a black box. When it gave
  a wrong answer, we had no way to debug WHY. Which tool did it call?
  What did the tool return? Where did the reasoning go wrong?

TASK:
  Build a full execution tracing system that records every step of
  the agent's decision-making process for debugging and auditing.

ACTION (What I Built):
  An OpenTelemetry-style tracing system for AI agents:

  WHAT IT CAPTURES:
    - Every LLM call (input, output, model, tokens, latency, cost)
    - Every tool call (function name, arguments, result, duration)
    - The "thought process" (why the agent decided to call tool X)
    - Context state at each step (what was in the context window)

  VISUALIZATION:
    Timeline view: Step 1 → Step 2 → Step 3 (waterfall)
    Token counter: "Total tokens used: 8,432 across 5 LLM calls"
    Cost tracker: "Total cost: $0.12 (GPT-4o: $0.08, mini: $0.04)"
    Error tracker: "Step 3: tool call failed, retried, succeeded"

RESULT:
  - Debugging time: 2 hours → 10 minutes (just look at the trace)
  - Identified that 40% of token cost was from redundant tool calls
  - Found a bug where the agent was calling the same tool twice
  - Became essential for compliance: "Show me exactly what the AI did"

REFLECTION:
  "Agent observability is the most underrated part of AI engineering.
   Everyone focuses on building the agent, but nobody can DEBUG it
   without traces. This is especially critical in enterprise where
   'the AI made a decision' needs an audit trail."
```

---

### PROJECT 7: Telecom-Shield — AI-Powered Network Security

#### The STAR-R Story

```
SITUATION:
  AT&T's 5G core handles millions of signaling messages per second.
  Traditional rule-based security systems can't keep up with novel
  attack patterns: SIM swap fraud, signaling storm attacks, SS7/Diameter
  protocol exploits.

TASK:
  Build an AI-powered network security monitoring system that detects
  anomalies in signaling traffic in real-time and alerts the SOC team.

ACTION (What I Built):
  A multi-layer detection system:

  LAYER 1: Rule-Based Filter (fast, catches known attacks)
    - Known fraudulent IMSI patterns
    - Geographic anomalies (SIM registered in Mumbai, active in Delhi in 5 min)
    - Signaling rate thresholds (>1000 msgs/sec from one source)

  LAYER 2: ML Anomaly Detector (catches novel attacks)
    - Isolation Forest for traffic pattern anomalies
    - LSTM autoencoder for time-series anomaly detection
    - Real-time scoring on streaming signaling data (Kafka → Flink)

  LAYER 3: LLM Investigator (explains the anomaly)
    - When anomaly detected, triggers an LLM agent
    - Agent queries: "What's different about this traffic pattern?"
    - Correlates with recent threat intelligence feeds
    - Produces a human-readable incident report

RESULT:
  - Detection rate: 94% (vs 71% for rules-only)
  - False positive rate: 2.3% (vs 15% for rules-only)
  - Mean time to detect (MTTD): 45 seconds (vs 12 minutes)
  - Caught 3 novel attack patterns in first month

REFLECTION:
  "This project taught me that AI security is a CASCADE, not a single
   model. Fast filters catch the obvious stuff for free. ML catches
   patterns humans can't see. LLMs explain WHY something is suspicious
   in human-readable language. Each layer has different cost/accuracy
   tradeoffs."
```

---

## 3. TELECOM-SPECIFIC FDE PROJECTS

> When the interviewer asks "What would you build for a telecom customer?" — have 3-4 ready.

### Project A: Network Fault Isolation Agent (AT&T / Vodafone Model)

```
PROBLEM: When a 5G tower goes down, it could be:
  - Hardware failure (radio unit, antenna)
  - Backhaul fiber cut
  - Power outage
  - Configuration error
  - Software bug in the baseband unit
  - Core network issue (AMF/UPF failure)

Currently, engineers manually check each possibility sequentially.

AGENT SOLUTION:
  An AI agent that automates fault isolation:
    1. Tool: get_alarms(tower_id) → fetches all active alarms
    2. Tool: get_topology(tower_id) → shows dependencies (tower→switch→core)
    3. Tool: check_neighbors(tower_id) → are adjacent towers also down?
    4. Tool: get_recent_changes(tower_id) → any config changes in last 24h?
    5. Tool: get_performance(tower_id, metric) → historical patterns

  Agent reasons:
    - If neighbors are also down → backhaul fiber cut (shared backhaul)
    - If only this tower → local hardware/power issue
    - If recent config change → likely misconfiguration
    - If alarms show "radio unit unreachable" → hardware failure

  Output: Ranked fault hypotheses with probability + remediation steps

BASED ON: Vodafone network operations AI (30% fewer outages, 50% faster MTTR)
```

### Project B: Capacity Planning Agent (Verizon/Deutsche Telekom Model)

```
PROBLEM: Telecom networks need capacity planning months in advance.
  "Will the Mumbai-Ahmedabad fiber route have enough capacity for
   Q4 traffic? Should we add another 100G wave?"

AGENT SOLUTION:
  An agent that combines historical traffic data, growth projections,
  event calendars, and network topology:
    1. Tool: query_traffic(route, time_range) → historical utilization
    2. Tool: get_growth_forecast(region) → subscriber growth projections
    3. Tool: get_events(region, date) → festivals, elections, sports (traffic spikes)
    4. Tool: get_capacity(route) → current max capacity
    5. Tool: get_budget(region) → available capex for upgrades

  Agent produces:
    - Capacity forecast: "Route will hit 85% utilization by October"
    - Recommendation: "Add 100G wave by September. Cost: $340K. ROI: prevents $2M SLA penalty"
    - Risk analysis: "If Diwali traffic spikes 40%, route overflows for 3 hours"
```

### Project C: Customer Churn Prediction + Intervention Agent (T-Mobile Model)

```
PROBLEM: Telecom churn rate is 1.5-2% monthly. Acquiring a new customer
  costs 5× more than retaining one.

AGENT SOLUTION:
  1. Tool: get_usage(customer_id) → call patterns, data usage trends
  2. Tool: get_complaints(customer_id) → support tickets, complaints
  3. Tool: get_billing(customer_id) → payment history, plan changes
  4. Tool: get_network_quality(customer_id) → signal strength, drop rate
  5. Tool: offer_retention(customer_id, offer) → apply discount/upgrade

  Agent:
    - Predicts churn probability (ML model: 87% accuracy)
    - If probability >70%: agent recommends personalized retention offer
    - "Customer has 30% more dropped calls this month + complained twice
       → offer free signal booster + 1 month credit"
    - Agent can execute the offer via CRM API

BASED ON: T-Mobile churn reduction AI (15% churn reduction, $500M+ saved)
```

---

## 4. SYSTEM DESIGN MASTERY

### The 5-Step System Design Framework (For Any Problem)

```
┌──────────────────────────────────────────────────┐
│  STEP 1: CLARIFY (5 min)                         │
│  "Let me make sure I understand the problem."     │
│  - Functional requirements (what does it DO?)     │
│  - Non-functional (scale, latency, availability)  │
│  - Constraints (budget, team size, timeline)      │
│                                                  │
│  STEP 2: ESTIMATE (3 min)                        │
│  "Let me estimate the scale."                     │
│  - Users, requests/sec, storage, bandwidth        │
│  - Shows you can think about real numbers         │
│                                                  │
│  STEP 3: DRAW (10 min)                           │
│  "Here's the high-level architecture."            │
│  - Client → CDN → LB → API → Service → DB → Cache│
│  - Get agreement before going deeper              │
│                                                  │
│  STEP 4: DEEP DIVE (15 min)                      │
│  "Let me design the hardest part."                │
│  - Pick the component with most complexity        │
│  - Design database schema, algorithms, APIs       │
│                                                  │
│  STEP 5: SCALE & BOTTLENECK (5 min)              │
│  "Now let me identify single points of failure."  │
│  - Sharding, replication, caching, queues         │
│  - CAP theorem tradeoffs                         │
└──────────────────────────────────────────────────┘
```

### Telecom System Design: Design a 5G Core Network Monitoring System

```
PROBLEM: "Design a system that monitors 100,000+ 5G towers nationwide,
collect metrics, detect anomalies, and alert engineers within 60 seconds."

ARCHITECTURE:

  ┌─────────┐  Telemetry  ┌──────────┐  Stream   ┌──────────────┐
  │ 100K    │ ──────────> │ Kafka    │ ────────> │ Flink/Spark  │
  │ Towers  │  (gNMI/     │ (ingest) │  (process)│ Streaming    │
  │ (agents)│   SNMP)     │          │           │ Engine       │
  └─────────┘             └──────────┘           └──────┬───────┘
                                                        │
                         ┌──────────────────────────────┼──────────────┐
                         │                              │              │
                         ▼                              ▼              ▼
                  ┌──────────┐                  ┌────────────┐  ┌────────────┐
                  │ Time-    │                  │ Anomaly    │  │ Alerting   │
                  │ Series   │                  │ Detector   │  │ Engine     │
                  │ DB       │                  │ (ML model) │  │ (PagerDuty)│
                  │ (TSDB)   │                  │            │  │            │
                  └──────────┘                  └────────────┘  └────────────┘

SCALE ESTIMATES:
  100,000 towers × 50 metrics each × 1 reading/sec = 5,000,000 data points/sec
  Storage: 5M/sec × 86400 sec × 365 days × 100 bytes = ~15 TB/year
  Kafka throughput: 5M msgs/sec → 50 Kafka partitions across 10 brokers

KEY DECISIONS:
  1. Push vs Pull: Push (tower agents push metrics) → lower latency than polling
  2. Time-series DB: InfluxDB or TimescaleDB (optimized for time-series queries)
  3. Stream processing: Flink for real-time anomaly detection (windowed analysis)
  4. Alerting: Multi-level (info → warn → critical) with escalation policies
  5. Storage tiering: Hot (7 days, fast SSD) → Warm (90 days, HDD) → Cold (1 year, S3)
```

---

## 5. AI SYSTEM DESIGN MASTERY

### Design an AI-Powered Customer Support Agent for AT&T

```
PROBLEM: "Design an AI chatbot that handles customer support for 50M AT&T
subscribers. It should resolve 70% of queries without human escalation."

STEP 1: REQUIREMENTS
  Functional: Handle billing questions, plan changes, outage reports,
              technical support, device troubleshooting
  Non-functional: <3s response time, 99.9% uptime, multi-language
  Scale: 50M users, ~5M queries/day, ~60 queries/sec peak

STEP 2: ARCHITECTURE

  ┌────────┐    ┌───────────┐    ┌──────────────┐    ┌──────────────┐
  │ User   │──> │ Load      │──> │ Intent       │──> │ Router       │
  │ App    │    │ Balancer  │    │ Classifier   │    │              │
  └────────┘    └───────────┘    └──────────────┘    └──────┬───────┘
                                                             │
                    ┌────────────────────────────────────────┼────────┐
                    │                                        │        │
                    ▼                                        ▼        ▼
             ┌───────────┐                          ┌───────────┐ ┌──────────┐
             │ RAG Engine │                          │ Agent     │ │ FAQ Bot  │
             │ (docs)    │                          │ (tools)   │ │ (simple) │
             └───────────┘                          └───────────┘ └──────────┘
                    │                                        │
                    └────────────────┬───────────────────────┘
                                     │
                                     ▼
             ┌───────────┐    ┌──────────────┐    ┌──────────────┐
             │ Response  │<── │ LLM          │<── │ Guardrails   │
             │ Formatter │    │ (GPT-4o-mini)│    │ (AgentGuard) │
             └───────────┘    └──────────────┘    └──────────────┘

STEP 3: COMPONENT DESIGN

  INTENT CLASSIFIER:
    "Is this a billing question, technical issue, outage report, or plan change?"
    Model: Fine-tuned BERT or GPT-4o-mini (fast classification)
    Routes to: FAQ Bot (simple) / RAG Engine (knowledge) / Agent (action)

  RAG ENGINE:
    - Vector DB: 500K support articles, FAQs, troubleshooting guides
    - Embeddings: text-embedding-3-small (OpenAI) or BGE-large (local)
    - Hybrid search: vector + BM25 keyword search
    - Reranking: cross-encoder for top-5 precision
    - Context budget: max 8K tokens of retrieved docs per query

  AGENT (for action-required queries):
    Tools: check_bill(), process_payment(), report_outage(),
           schedule_technician(), upgrade_plan(), escalate_human()
    ReAct loop with max 5 iterations
    Guardrails on all tool calls (permission matrix)

  GUARDRAILS:
    - Input: PII redaction (PIIScrub), prompt injection detection
    - Tool: Permission validation (can this user modify this account?)
    - Output: Toxicity filter, hallucination check

STEP 4: SCALING

  - LLM calls: route 60% to GPT-4o-mini (saves 73% cost)
  - Caching: cache responses for common queries (FAQ → pre-computed)
  - Rate limiting: 10 queries/min per user
  - Queue: Kafka for peak load leveling
  - Fallback: if OpenAI is down, failover to self-hosted Llama 3.1

STEP 5: COSTS

  5M queries/day × 2000 tokens/query × $0.15/1M = $1,500/day (GPT-4o-mini)
  Annual: $547,500 (GPT-4o-mini) vs $18,250,000 (GPT-4o)
  "Model choice IS the business model for AI products."
```

---

## 6. AGENT/TOOL/CONTEXT ENGINEERING ANSWERS

### "What is an agentic harness?" — The Complete Answer

```
"An agentic harness is the orchestration layer that wraps the LLM and
controls its behavior. Think of it as the 'body' around the LLM 'brain.'

The harness handles five things:
1. CONTEXT MANAGEMENT: Decides what's in the context window. Compresses
   old history, injects RAG results, structures tool definitions.

2. TOOL DISPATCH: When the LLM says 'call get_weather(city=Mumbai)',
   the harness parses that, validates arguments, executes the function,
   and feeds the result back.

3. ERROR HANDLING: If a tool fails, the harness decides: retry, try a
   different tool, or escalate to human. It prevents infinite loops.

4. SAFETY: Validates tool calls against a permission matrix. Blocks
   dangerous actions. Enforces rate limits.

5. OBSERVABILITY: Records every LLM call, tool call, and decision for
   debugging (AgentTrace). This is critical for enterprise audit trails.

I built this from scratch for IncidentAgent — the harness code is
actually more complex than the LLM interaction code. The harness is
where the engineering value is."
```

### "How do you do context engineering?" — The Complete Answer

```
"I treat context as a budget — every token has a cost. My approach:

1. BUDGET ALLOCATION: For a 128K context window, I allocate:
   - System prompt: 2K tokens
   - Tool definitions: 1.5K tokens
   - RAG context: 10-30K tokens (top 5 reranked docs)
   - Conversation history: 10-20K tokens (summarized after 5 messages)
   - Current message: ~500 tokens
   - Output reserve: 4K tokens
   Total: ~18-28K tokens (NOT 128K — leaving headroom is important)

2. CONVERSATION COMPRESSION: After 5 turns, I send old messages to
   GPT-4o-mini for summarization. Old: 15K tokens → Summary: 500 tokens.

3. RAG QUALITY: Retrieve 20 docs → rerank with cross-encoder → keep
   top 3-5. Extract only relevant paragraphs. Format with citations.

4. STRUCTURED OUTPUT: JSON schema enforcement so the LLM's output
   is always machine-parseable. No parsing natural language.

This reduced our cost per query from $0.15 to $0.02 — 7.5× cheaper —
while improving answer quality because the LLM isn't lost in noise."
```

---

## 7. LEETCODE PROBLEM-SOLVING TECHNIQUES

### How to Approach Any Problem in 4 Steps

```
STEP 1: RESTATE THE PROBLEM (30 seconds)
  "So we need to find the first non-repeating character in a string.
   If none exists, return -1. Is that correct?"

STEP 2: BRUTE FORCE FIRST (1 minute)
  "The brute force approach: for each character, scan the rest of the
   string to check if it repeats. That's O(n²) time, O(1) space.
   It works but is slow for large inputs."

  → ALWAYS state brute force first. Shows you can solve it.

STEP 3: OPTIMIZE (3-5 minutes)
  "Can we do better? We're doing repeated lookups — 'have I seen this
   character before?' That's a hash map pattern.

   We can do two passes:
   Pass 1: Count frequency of each character using a hash map. O(n)
   Pass 2: Find the first character with count 1. O(n)

   Total: O(n) time, O(1) space (26 letters max = constant)"

STEP 4: CODE + TEST (10 minutes)
  Write clean code. Then dry-run with a small example.
  "Let me trace through with 'leetcode':
   l=1, e=3, t=1, c=1, o=1, d=1 → first with count 1 is 'l' at index 0."
```

### The 15 Patterns That Solve 75 Problems

```
"If I see this signal in the problem → I use this pattern:"

1. "Find pair / check existence" → Hash Map
2. "Sorted array + find pair" → Two Pointers
3. "Subarray with condition" → Sliding Window
4. "Search in sorted data" → Binary Search
5. "Matching / nesting / undo" → Stack
6. "Next greater/smaller element" → Monotonic Stack
7. "Shortest path / level order" → BFS
8. "All possible paths / flood fill" → DFS
9. "Generate all combinations" → Backtracking
10. "Max/min/ways with subproblems" → Dynamic Programming
11. "K largest/smallest" → Heap
12. "Prefix matching" → Trie
13. "Linked list manipulation" → Fast & Slow Pointers
14. "Top K frequent" → Bucket Sort or Heap
15. "Find minimum X where condition(X) is true" → Binary Search on Answer
```

### How to Talk Through a Problem (Communication is Graded)

```
DURING THE INTERVIEW:
  ✓ Think out loud: "I'm considering using a hash map because..."
  ✓ Ask about edge cases: "What if the array is empty?"
  ✓ State complexity: "This is O(n) time and O(n) space."
  ✓ Offer alternatives: "We could also use sorting + binary search,
     but that would be O(n log n)."
  ✓ Test before saying done: "Let me dry-run with [1,2,3,4,5], k=3..."

WHAT INTERVIEWERS LOOK FOR:
  ✓ Problem decomposition (break it into smaller parts)
  ✓ Pattern recognition (identify the right data structure)
  ✓ Communication (explain your thought process)
  ✓ Clean code (meaningful variable names, proper structure)
  ✓ Self-correction (catch your own bugs)
```

---

## 8. THE INTERVIEW PLAYBOOK — STEP BY STEP

### Phase 1: The Introduction (2 minutes)

```
Deliver your 60-second intro (Section 1).

Key signals to hit:
  ✓ "7+ years running production telecom infrastructure at scale"
  ✓ "Pivoted to AI engineering 18 months ago"
  ✓ "11+ AI projects on GitHub"
  ✓ "What excites me about FDE is combining customer-facing deployment
     with AI engineering"
```

### Phase 2: Project Deep-Dive (15-20 minutes)

```
They'll pick a project. Pick IncidentAgent or CostLens (strongest).

Use STAR-R:
  S: "At AT&T, incident investigation took 20-40 minutes manually..."
  T: "I built an AI agent to automate it..."
  A: "Used ReAct pattern with 6 tools. Key challenge was context
      window explosion from log queries..."
  R: "Reduced investigation time from 30 min to 90 seconds.
      87% root cause accuracy."
  R: "The harness matters more than the model. Context engineering
      was the difference between success and failure."

HAVE THESE NUMBERS READY:
  - Investigation time: 30 min → 90 sec
  - Cost reduction: $47K → $12.6K/month (73%)
  - RAG accuracy: 79% → 91% with GraphRAG
  - PII detection: 99.2%
  - LLM cost per query: $0.02-$0.08
```

### Phase 3: System Design (30-40 minutes)

```
They'll ask you to design a system.

FRAMEWORK:
  1. "Let me start by clarifying requirements..."
  2. "Let me estimate the scale..."
  3. "Here's my high-level architecture..." [DRAW]
  4. "Let me deep-dive into [hardest component]..."
  5. "Now let me address bottlenecks and scaling..."

AI-SPECIFIC COMPONENTS TO MENTION:
  ✓ Multi-model routing (GPT-4o-mini for simple, GPT-4o for complex)
  ✓ RAG with reranking (retrieve → rerank → compress → format)
  ✓ Agent harness with tool dispatch and error handling
  ✓ Guardrails (input filtering, PII redaction, output validation)
  ✓ Observability (token tracking, cost monitoring, agent tracing)
  ✓ Cost optimization (model routing, caching, context compression)

ALWAYS MENTION:
  ✓ Cost implications ("At 5M queries/day, GPT-4o-mini saves $17M/year")
  ✓ Fallback/redundancy ("If OpenAI is down, failover to Llama 3.1")
  ✓ Security ("PII redaction before LLM calls")
  ✓ Monitoring ("Track hallucination rate, latency, cost per query")
```

### Phase 4: Coding (30-40 minutes)

```
They'll give you a LeetCode problem.

YOUR PROCESS:
  1. Restate the problem ("So we need to...")
  2. Ask about edge cases ("What if the input is empty?")
  3. State brute force ("Brute force is O(n²) by checking each pair")
  4. Identify the pattern ("This is a hash map lookup problem")
  5. State optimal approach ("Two passes with a hash map: O(n) time")
  6. Code it cleanly (meaningful variable names, comments)
  7. Dry-run with an example ("Let me trace through [1,2,3]...")
  8. State complexity ("O(n) time, O(n) space")

IF YOU'RE STUCK:
  ✓ Start with brute force and optimize from there
  ✓ Ask: "Can sorting help?" (enables binary search + two pointers)
  ✓ Ask: "Can I use extra memory?" (hash map for O(1) lookups)
  ✓ Ask: "Is there a subproblem?" (dynamic programming)
  ✓ Communicate: "I'm thinking about using a sliding window because..."
```

### Phase 5: Behavioral / Experience (10-15 minutes)

```
COMMON QUESTIONS AND YOUR ANSWERS:

"Tell me about a time you faced a technical challenge."
→ IncidentAgent context window explosion (Project 1, Challenge 2)

"Tell me about a time you disagreed with a teammate."
→ "I wanted to use GraphRAG for relationship queries. The team said
   vector search was sufficient. I built a prototype showing 91% vs 79%
   accuracy on relational queries. Data won the argument."

"Tell me about a time you failed."
→ "First version of IncidentAgent hallucinated root causes. I'd been
   too focused on the agent loop and neglected output validation.
   I added evidence-backed structured output and a post-generation
   validator. Lesson: always validate LLM output against ground truth."

"Why FDE?"
→ "I've been doing forward deployed work my whole career — deploying
   at telecom sites, debugging live systems, shipping under pressure.
   FDE formalizes what I already do. The AI layer is the new skill
   I've built on top of that operational foundation."

"Why our company?"
→ Research the company. Mention their AI products, customer base,
   and how your telecom+AI background fits their specific needs.
```

---

## THE CHEAT SHEET — NUMBERS TO MEMORIZE

```
INCIDENT AGENT:
  Investigation time: 30 min → 90 sec
  Root cause accuracy: 87%
  Cost per investigation: $0.08
  Tools: 6 (logs, metrics, tickets, runbooks, topology, escalation)

COSTLENS:
  Monthly savings: $47K → $12.6K (73% reduction)
  Annual savings: $412,800
  Routing: 60% mini, 30% GPT-4o, 10% Claude

GRAPH RAG:
  Documents: 159
  Entities: 297
  Relationships: 6,822
  Text chunks: 4,914
  Accuracy improvement: 79% → 91% (+12 points)

PII SCRUB:
  Detection rate: 99.2%
  Latency: <5ms
  Telecom-specific identifiers: 15+ types

AGENT GUARD:
  Injection blocked: 99.4%
  Latency added: <10ms

LEETCODE:
  86 problems solved (Blind 75 + 11 bonus)
  12 categories mastered
  All solutions verified
```

---

## FINAL INTERVIEW TIPS

```
1. BE THE EXPERT THEY NEED
   You're not a junior dev hoping to learn AI. You're a senior engineer
   who already runs production systems at scale and has added AI to that
   toolkit. Own that expertise.

2. ALWAYS HAVE AN OPINION
   FDEs are hired for judgment. Don't say "it depends." Say "I'd use
   RAG first because it's faster to implement and handles knowledge
   updates. Fine-tune only if format consistency is below 95%."

3. SHOW COST AWARENESS
   Every technical decision should include cost implications. This is
   the #1 signal that separates real engineers from tourists.

4. CONNECT TO CUSTOMER IMPACT
   "The reason I built CostLens wasn't just to save money — it was
   because the $47K/month bill was blocking us from deploying AI to
   more use cases. Cost optimization unlocked 3× more AI features."

5. WHEN IN DOUBT, DRAW
   In system design interviews, always draw the architecture.
   Whiteboard > words. Boxes and arrows show structured thinking.

6. THE 24-HOUR RULE
   24 hours before the interview:
   - Re-read your project STAR-R stories (Section 2)
   - Review the interview Q&A cheat sheet (fde-ai-engineering/08)
   - Do 3 LeetCode problems (one easy, one medium, one hard)
   - Sleep 8 hours

7. ENERGY MATTERS
   FDEs are high-energy operators. Show enthusiasm. Lean forward.
   Use your hands when explaining. Sound like someone who SHIPS.

YOU'VE BUILT THE SKILLS. NOW GO SELL THEM. 🔥
```
