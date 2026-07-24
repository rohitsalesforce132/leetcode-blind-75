# Telecom FDE Projects — Deep-Dive Interview Guide

> **Purpose:** When the interviewer asks "What would you build for a telecom customer?" — these two projects prove you combine AI engineering with DEEP telecom domain knowledge. Nobody else in the interview will have this combination.

---

## TABLE OF CONTENTS

1. [Project A: Network Fault Isolation Agent](#project-a)
   - [The Problem (5G Tower Outage Reality)](#a-problem)
   - [System Architecture](#a-architecture)
   - [The 5 Tools — Complete Specifications](#a-tools)
   - [The Agent Decision Tree](#a-decision-tree)
   - [Real Investigation Walkthrough](#a-walkthrough)
   - [Context Engineering for Network Data](#a-context)
   - [15 Interview Q&As](#a-qa)
   - [90-Second Pitch](#a-pitch)

2. [Project B: Capacity Planning Agent](#project-b)
   - [The Problem (Capacity Planning at Scale)](#b-problem)
   - [System Architecture](#b-architecture)
   - [The 5 Tools — Complete Specifications](#b-tools)
   - [The Forecasting Engine](#b-forecasting)
   - [Real Analysis Walkthrough](#b-walkthrough)
   - [Risk Analysis & SLA Modeling](#b-risk)
   - [15 Interview Q&As](#b-qa)
   - [90-Second Pitch](#b-pitch)

---

## PROJECT A: NETWORK FAULT ISOLATION AGENT
### Based on: Vodafone Network Operations AI (30% fewer outages, 50% faster MTTR)

---

### <a id="a-problem"></a>THE PROBLEM — 5G TOWER OUTAGE REALITY

#### What Happens When a Cell Tower Goes Dark

```
THE ALARM CASCADE:

00:00 ─ Tower TX-4471-MUM goes unreachable
       NOC dashboard turns RED
       │
00:01 ─ 12 alarms fire simultaneously:
         • "gNB unreachable" (baseband unit)
         • "S1 connection lost" (5G core link)
         • "Backhaul link down" (fiber to tower)
         • "Power alert" (site power)
         • "Environmental alarm" (temperature/humidity)
         • "Clock sync lost" (PTP/GPS)
         • "Radio unit offline" (RRU/AAU)
         │
00:02 ─ NOC engineer assigned
         Opens 6 different tools to investigate:
         ① Fault Management System (FMS) → see raw alarms
         ② Network Topology Viewer → check backhaul dependencies
         ③ Neighbor cell map → are adjacent towers affected?
         ④ Change Management System → any recent config changes?
         ⑤ Performance Management → historical KPIs
         ⑥ Field Dispatch System → send technician
         │
00:05 ─ Engineer checks: "Is this tower alone, or are neighbors down too?"
         Opens topology viewer → loads slowly (30 sec)
         Checks 3 neighbor towers manually
         │
00:10 ─ Engineer checks: "Was there a recent config change?"
         Opens change management → searches by tower ID
         Finds: "BGP config updated 2 hours ago by Team X"
         │
00:15 ─ Engineer checks: "Is the backhaul up?"
         Opens fiber monitoring → checks the route
         Finds: "Backhaul fiber Route-MUM-AHM-12 showing LOS"
         │
00:20 ─ Engineer STILL doesn't know the root cause.
         Is it the fiber cut? The BGP change? Hardware failure?
         They must eliminate each possibility one by one.
         │
00:25 ─ Engineer dispatches a field tech to investigate physically.
         Field tech drive time: 90 minutes.
         │
02:00 ─ Field tech arrives. Reports: "Backhaul fiber is cut at km 47.
         Excavator damaged it during road construction."
         │
02:05 ─ Engineer reroutes traffic to backup fiber path.
         Tower comes back online.

THE DAMAGE:
  Total downtime: 2 hours 5 minutes
  Customers affected: ~15,000 subscribers in the area
  SLA penalty: $50,000-$150,000 (depends on contract)
  Engineer time wasted: 25 minutes of manual investigation
  Field tech wasted trip? NO — but could have been dispatched EARLIER
  with the RIGHT equipment if the agent had identified fiber cut.

THE REALITY: If the agent had investigated in 90 seconds instead of 25
minutes, AND if it had dispatched the field tech with fiber repair
equipment immediately (instead of generic "investigate"), the tower
could have been restored in 60 minutes instead of 125 minutes.
That's a 52% MTTR reduction.
```

#### Why This Is Perfect for an AI Agent

```
THE INVESTIGATION IS A DECISION TREE — IDEAL FOR LLM REASONING:

  Tower down → Check neighbors
    ├── Neighbors also down → SHARED BACKHAUL FAILURE
    │   ├── Check fiber route alarms → Fiber LOS confirmed? → FIBER CUT
    │   └── No fiber alarms → Check upstream switch → SWITCH FAILURE
    │
    └── Only this tower → LOCAL ISSUE
        ├── Check power alarms → Power alert? → POWER OUTAGE
        ├── Check recent changes → Config change in 24h? → MISCONFIGURATION
        ├── Check radio alarms → RRU offline? → HARDWARE FAILURE
        └── Check environmental → Temp/humidity alarm? → ENVIRONMENTAL

  This is a CLASSIC pattern-matching + reasoning problem.
  LLMs are excellent at this — better than humans at holding all
  alarm signals in "context" simultaneously and matching patterns.
```

---

### <a id="a-architecture"></a>SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                NETWORK FAULT ISOLATION AGENT ARCHITECTURE                │
│                                                                         │
│  ┌──────────┐                                                          │
│  │ Fault     │  Alarm webhook: "Tower TX-4471-MUM unreachable"        │
│  │ Mgmt Sys  │  → Triggers Fault Isolation Agent                       │
│  │ (FMS)     │                                                         │
│  └────┬──────┘                                                         │
│       │                                                                 │
│       ▼                                                                 │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                   FAULT ISOLATION AGENT                       │      │
│  │                   (ReAct Loop, max 8 iterations)             │      │
│  │                                                              │      │
│  │  ┌────────────┐   ┌────────────┐   ┌────────────────────┐   │      │
│  │  │ Telecom    │   │ ReAct Loop │   │ Fault Hypothesis   │   │      │
│  │  │ Knowledge  │   │ Engine     │   │ Ranker             │   │      │
│  │  │ Base       │   │            │   │                    │   │      │
│  │  │ (GraphRAG  │   │ Think →    │   │ Scores each        │   │      │
│  │  │  telecom   │   │ Act →      │   │ hypothesis by      │   │      │
│  │  │  domain)   │   │ Observe →  │   │ probability +      │   │      │
│  │  │            │   │ Loop       │   │ evidence strength  │   │      │
│  │  └────────────┘   └─────┬──────┘   └────────────────────┘   │      │
│  └─────────────────────────┼───────────────────────────────────┘      │
│                            │                                            │
│       ┌────────────────────┼───────────────────────────────────┐      │
│       │                    │                                    │      │
│       ▼                    ▼                    ▼                ▼      │
│  ┌─────────┐    ┌──────────────┐    ┌─────────────┐   ┌──────────────┐│
│  │ TOOL 1  │    │ TOOL 2       │    │ TOOL 3      │   │ TOOL 4       ││
│  │ get_    │    │ get_         │    │ check_      │   │ get_recent_  ││
│  │ alarms  │    │ topology     │    │ neighbors   │   │ changes     ││
│  │         │    │              │    │             │   │              ││
│  │ Fault   │    │ Network      │    │ Adjacent    │   │ Change       ││
│  │ Mgmt    │    │ Topology     │    │ cell sites  │   │ Mgmt Sys     ││
│  │ System  │    │ (Neo4j)      │    │ status      │   │ (ServiceNow) ││
│  └─────────┘    └──────────────┘    └─────────────┘   └──────────────┘│
│                                                                        │
│  ┌─────────────────────┐    ┌──────────────────────┐                  │
│  │ TOOL 5              │    │ TOOL 6               │                  │
│  │ get_performance     │    │ dispatch_field_tech  │                  │
│  │                     │    │                      │                  │
│  │ Historical KPIs     │    │ Dispatch field tech  │                  │
│  │ (PM data)           │    │ with RIGHT equipment │                  │
│  │ Prometheus/InfluxDB │    │ based on hypothesis  │                  │
│  └─────────────────────┘    └──────────────────────┘                  │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │ INFRASTRUCTURE: Redis (cache) | Kafka (queue) | AgentTrace  │     │
│  └──────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### <a id="a-tools"></a>THE 5 TOOLS — COMPLETE SPECIFICATIONS

#### Tool 1: get_alarms

```python
def get_alarms(tower_id: str, severity: str = "all",
               time_range: str = "last_2_hours") -> dict:
    """
    Fetch all active alarms for a cell tower from the Fault Management System.

    Telecom-specific alarm types the tool handles:
      - gNB alarms: baseband unit unreachable, S1/N2 connection lost
      - Transport alarms: backhaul LOS (loss of signal), fiber cut
      - Power alarms: commercial power lost, battery low, generator fault
      - Radio alarms: RRU/AAU offline, RF output low, VSWR alarm
      - Environmental: temperature high, humidity, door open, intrusion
      - Clock: PTP/GPS sync lost, frequency sync error
      - Core: AMF/UPF connection failure, S-NSSAI slice unavailable

    Returns alarm list with: type, severity (critical/major/minor),
    timestamp, probable cause (3GPP standard codes).

    Source: Fault Management System (Ericsson ENIQ / Nokia AMOS /
            Huawei U2020 / Generic SNMP traps)
    Cache: 30 seconds (alarms change rapidly during active incidents)
    Timeout: 10 seconds
    """
```

#### Tool 2: get_topology

```python
def get_topology(node_id: str, depth: int = 3) -> dict:
    """
    Get network topology and dependencies for a tower from Neo4j graph.

    Telecom-specific topology this traverses:

    FORWARD (what this tower depends on):
      TX-4471-MUM ──ROUTES_THROUGH──> Backhaul-Fiber-MUM-AHM-12
      TX-4471-MUM ──CONNECTS_TO──> Aggregation-Switch-AGG-03
      TX-4471-MUM ──BACKED_BY──> Backup-Microwave-Link-MW-07
      Aggregation-Switch-AGG-03 ──CONNECTS_TO──> Core-Router-CR-MUM-01
      Core-Router-CR-MUM-01 ──DEPENDS_ON──> AMF-5G-Core-MUM

    REVERSE (what depends on this tower):
      TX-4471-MUM ──SERVES──> Coverage-Area-MUM-Sector-7
      Coverage-Area-MUM-Sector-7 ──HAS_SUBSCRIBERS──> ~15,000 UEs

    The graph also stores:
      - Fiber route physical path (km markers, manhole locations)
      - Equipment models (Ericsson AIR 3268, Nokia AEQU, Huawei AAU)
      - Band/frequency (700MHz, 3.5GHz n78, 28GHz mmWave)
      - Site type (macro, micro, small cell, DAS)

    Source: Neo4j network topology graph (synced from inventory system)
    Cache: 1 hour (topology changes infrequently)
    Timeout: 5 seconds (graph query is fast)
    """
```

#### Tool 3: check_neighbors

```python
def check_neighbors(tower_id: str) -> dict:
    """
    Check status of adjacent cell sites.

    THIS IS THE MOST IMPORTANT TOOL FOR ROOT CAUSE ISOLATION.

    If neighbors are also down → shared infrastructure failure
      (backhaul fiber, aggregation switch, power grid)

    If only this tower → local site issue
      (hardware, local power, local config)

    The tool queries:
      1. Neo4j: find all towers within handover distance (typically 1-5km)
      2. FMS: check alarm status for each neighbor
      3. PM data: check if neighbors show increased traffic (offload from
         failed tower → neighbors get overloaded)

    Returns:
    {
        "tower_id": "TX-4471-MUM",
        "neighbors": [
            {"id": "TX-4472-MUM", "status": "operational", "distance_km": 1.2},
            {"id": "TX-4473-MUM", "status": "operational", "distance_km": 2.1},
            {"id": "TX-4474-PUN", "status": "DOWN ⚠️", "distance_km": 3.5},
        ],
        "shared_infrastructure": {
            "backhaul": "Backhaul-Fiber-MUM-AHM-12",
            "shared_with": ["TX-4471-MUM", "TX-4474-PUN"],  # ← BOTH DOWN!
            "aggregation_switch": "AGG-03"
        },
        "pattern": "MULTI_SITE_FAILURE → shared infrastructure likely cause"
    }

    Cache: 30 seconds
    Timeout: 5 seconds
    """
```

#### Tool 4: get_recent_changes

```python
def get_recent_changes(node_id: str, time_range: str = "last_24_hours") -> dict:
    """
    Check for recent configuration changes on the tower or its dependencies.

    Telecom-specific changes that cause outages:
      - BGP/routing config changes (most common cause of cascading failures)
      - RF parameter changes (power, tilt, band activation)
      - Software/firmware upgrades (baseband, RRU firmware)
      - 5G core config (slice config, AMF/UPF reassignment)
      - Backhaul bandwidth reconfiguration
      - planned maintenance (O&M window work)

    Source: Change Management System (ServiceNow / Remedy)
            + Network config management (Git-backed network configs)

    Returns:
    {
        "changes_found": true,
        "changes": [
            {
                "change_id": "CHG-2024-0892",
                "type": "BGP_ROUTING_CONFIG",
                "description": "Updated BGP neighbor config on AGG-03",
                "changed_by": "team-network-ops",
                "timestamp": "2024-07-24T08:15:00Z",
                "risk_level": "medium",
                "rollback_available": true,
                "correlation_strength": "HIGH"  # Changed 2h before outage
            }
        ],
        "correlation": "Config change 2 hours before outage — HIGH correlation"
    }

    Cache: 1 hour (change records don't update frequently)
    Timeout: 10 seconds
    """
```

#### Tool 5: get_performance

```python
def get_performance(tower_id: str, metric: str = "all",
                    time_range: str = "last_24_hours") -> dict:
    """
    Get historical performance KPIs for a tower.

    Telecom-specific KPIs:
      - RRC Connection Success Rate (%)
      - ERAB Setup Success Rate (%)
      - Handover Success Rate (%)
      - DL/UL Throughput (Mbps)
      - PRB Utilization (%)
      - Connected UEs (subscriber count)
      - RF Coverage (RSRP/RSRQ distribution)
      - Backhaul utilization (%)
      - Packet drop rate (%)

    Source: Performance Management system (Prometheus / InfluxDB /
            Ericsson PM Export / Nokia Performance Manager)

    Returns:
    {
        "tower_id": "TX-4471-MUM",
        "metrics": [
            {
                "name": "connected_ues",
                "current": 0,           # ← Zero! Tower is down
                "average_24h": 12450,
                "trend": "SUDDEN_DROP",  # Dropped from 12K to 0 at 10:00
                "drop_time": "2024-07-24T10:00:32Z"
            },
            {
                "name": "backhaul_utilization",
                "current": 0,           # ← Zero! No traffic flowing
                "average_24h": 67.5,
                "trend": "SUDDEN_DROP"
            }
        ],
        "pattern": "COMPLETE_SERVICE_LOSS — all metrics dropped to zero simultaneously"
    }

    Cache: 60 seconds
    Timeout: 10 seconds
    """
```

#### Tool 6: dispatch_field_tech (Action Tool)

```python
def dispatch_field_tech(tower_id: str, hypothesis: str,
                        required_equipment: list = None) -> dict:
    """
    Dispatch a field technician with the RIGHT equipment based on the
    agent's hypothesis.

    THIS IS THE DIFFERENTIATOR — the agent doesn't just diagnose,
    it dispatches with precision:

    Hypothesis: FIBER_CUT
    → Required equipment: OTDR tester, fusion splicer, spare fiber
    → Estimated repair: 2-4 hours
    → Escalation: Call fiber construction team

    Hypothesis: HARDWARE_FAILURE (RRU)
    → Required equipment: Replacement RRU, crane (if rooftop), tools
    → Estimated repair: 1-3 hours
    → Escalation: Call site access team

    Hypothesis: POWER_OUTAGE
    → Required equipment: Portable generator
    → Estimated repair: Until grid power restored
    → Escalation: Call power company

    Hypothesis: MISCONFIGURATION
    → Required equipment: Laptop with network access (remote fix)
    → Estimated repair: 15-30 minutes (rollback config)
    → Escalation: NO field dispatch needed — remote fix!

    Source: Field Dispatch System (custom API)
    Cache: None (unique action)
    Timeout: 5 seconds
    """
```

---

### <a id="a-decision-tree"></a>THE AGENT DECISION TREE

```
THE AGENT'S REASONING TREE (Encoded in System Prompt + GraphRAG):

TOWER DOWN
    │
    ├── Step 1: get_alarms(tower_id)
    │   What alarms are firing?
    │   │
    │   ├── "Backhaul LOS" alarm → TRANSPORT ISSUE
    │   │   └── Go to TRANSPORT_PATH ↓
    │   │
    │   ├── "Power alert" → POWER ISSUE
    │   │   └── Go to POWER_PATH ↓
    │   │
    │   ├── "RRU offline" → HARDWARE ISSUE
    │   │   └── Go to HARDWARE_PATH ↓
    │   │
    │   └── "gNB unreachable" (generic) → NEED MORE DATA
    │       └── Continue investigation ↓
    │
    ├── Step 2: check_neighbors(tower_id)
    │   Are adjacent towers also down?
    │   │
    │   ├── YES (2+ neighbors down) → SHARED INFRASTRUCTURE FAILURE
    │   │   │
    │   │   ├── get_topology → Find shared backhaul/switch
    │   │   │   └── Shared fiber route? → FIBER CUT (high probability)
    │   │   │   └── Shared aggregation switch? → SWITCH FAILURE
    │   │   │
    │   │   └── CONCLUSION: Multi-site failure → shared backhaul
    │   │       Dispatch: fiber team with OTDR + splicing equipment
    │   │
    │   └── NO (neighbors operational) → LOCAL SITE ISSUE
    │       │
    │       ├── get_recent_changes → Config change in 24h?
    │       │   └── YES → MISCONFIGURATION (rollback + verify)
    │       │       Remote fix — NO field dispatch needed
    │       │
    │       ├── No config change → Check hardware alarms
    │       │   └── "RRU offline" or "VSWR high" → HARDWARE FAILURE
    │       │       Dispatch: field tech with replacement RRU
    │       │
    │       └── No hardware alarms → Check power
    │           └── "Commercial power lost" → POWER OUTAGE
    │               Dispatch: field tech with portable generator
    │
    └── Step 3: get_performance(tower_id)
        Confirm hypothesis with KPI data:
        │
        ├── ALL metrics → 0 simultaneously → COMPLETE SERVICE LOSS
        │   Consistent with: fiber cut, power loss, or baseband failure
        │
        ├── Some metrics degraded but not zero → PARTIAL FAILURE
        │   Consistent with: interference, capacity issue, config error
        │
        └── Metrics showing gradual decline → DEGRADATION
            Consistent with: hardware aging, thermal throttling

OUTPUT: Ranked Fault Hypothesis Report
    {
        "primary_hypothesis": {
            "fault_type": "BACKHAUL_FIBER_CUT",
            "probability": 0.91,
            "evidence": [
                "2 of 4 neighbor towers also down [check_neighbors]",
                "Shared backhaul: Fiber-MUM-AHM-12 [get_topology]",
                "Backhaul LOS alarm active [get_alarms]",
                "All KPIs dropped to zero at same timestamp [get_performance]"
            ]
        },
        "secondary_hypothesis": {
            "fault_type": "AGGREGATION_SWITCH_FAILURE",
            "probability": 0.08,
            "evidence": ["Shared switch AGG-03 [get_topology]"]
        },
        "dispatch_recommendation": {
            "team": "Fiber Repair Team",
            "equipment": ["OTDR tester", "fusion splicer", "spare fiber"],
            "location": "Fiber route MUM-AHM, km 40-50 (based on LOS alarm)",
            "estimated_repair": "2-4 hours"
        },
        "temporary_mitigation": {
            "action": "Reroute traffic to backup microwave link MW-07",
            "can_execute": true,
            "impact": "Reduced capacity (200Mbps vs 10Gbps fiber)",
            "recommended": "YES — restore partial service while fiber is repaired"
        }
    }
```

---

### <a id="a-walkthrough"></a>REAL INVESTIGATION WALKTHROUGH

```
INPUT: "Tower TX-4471-MUM unreachable. All services down."

╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 1                                                         ║
║  Model: GPT-4o-mini (information gathering)                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  THOUGHT: "I need to understand what alarms are firing and whether  ║
║            this is an isolated failure or a multi-site issue."       ║
║                                                                      ║
║  ACTION: Parallel tool calls:                                        ║
║    get_alarms("TX-4471-MUM")                                         ║
║    check_neighbors("TX-4471-MUM")                                    ║
║                                                                      ║
║  ALARMS RESULT (compressed):                                         ║
║    Active alarms for TX-4471-MUM (14 total, 4 critical):             ║
║    [CRITICAL] gNB unreachable (10:00:32)                             ║
║    [CRITICAL] S1 connection lost (10:00:35)                          ║
║    [CRITICAL] Backhaul LOS detected (10:00:30)  ← FIRST!             ║
║    [CRITICAL] Clock sync lost (10:00:40)                             ║
║    [MAJOR] RRU-1 offline (10:01:15)                                  ║
║    [MAJOR] RRU-2 offline (10:01:16)                                  ║
║    [MINOR] Environmental temp normal                                 ║
║                                                                      ║
║    KEY INSIGHT: Backhaul LOS alarm fired FIRST (10:00:30),           ║
║    before all other alarms. This suggests backhaul failure           ║
║    CAUSED the cascade, not a symptom.                                ║
║                                                                      ║
║  NEIGHBORS RESULT:                                                   ║
║    Neighbor check for TX-4471-MUM:                                   ║
║    TX-4472-MUM: Operational ✓ (1.2km)                               ║
║    TX-4473-MUM: Operational ✓ (2.1km)                               ║
║    TX-4474-PUN: DOWN ⚠️ (3.5km)                                     ║
║    TX-4475-PUN: Operational ✓ (4.1km)                               ║
║                                                                      ║
║    Pattern: 1 of 4 neighbors also down                               ║
║    Shared infrastructure check:                                      ║
║    TX-4471-MUM and TX-4474-PUN share backhaul:                      ║
║    Fiber-MUM-AHM-12 ← BOTH TOWERS USE THIS FIBER                    ║
║                                                                      ║
║    CONCLUSION: Multi-site failure on shared backhaul                 ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 2                                                         ║
║  Model: GPT-4o (switching to reasoning model)                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  THOUGHT: "Two towers sharing the same fiber are both down. The      ║
║    backhaul LOS alarm was the first to fire. This strongly suggests  ║
║    a fiber cut. Let me confirm by checking the fiber route status    ║
║    and recent changes."                                              ║
║                                                                      ║
║  ACTION: Parallel tool calls:                                        ║
║    get_topology("Fiber-MUM-AHM-12")                                  ║
║    get_recent_changes("TX-4471-MUM")                                 ║
║                                                                      ║
║  TOPOLOGY RESULT:                                                    ║
║    Fiber route Fiber-MUM-AHM-12:                                     ║
║    Type: Underground fiber, 67km                                     ║
║    Status: LOS (Loss of Signal) at approximately km 47               ║
║    Serves: TX-4471-MUM, TX-4474-PUN (both down ✓)                   ║
║    Backup path: Microwave MW-07 (available, 200Mbps capacity)        ║
║    Last maintenance: 2024-06-15 (cable integrity test — passed)      ║
║    Construction activity: Roadwork permit issued for km 45-50        ║
║    on 2024-07-22 (2 days ago) ← CORRELATION!                        ║
║                                                                      ║
║  CHANGES RESULT:                                                     ║
║    Changes for TX-4471-MUM in last 24h:                              ║
║    CHG-2024-0892: BGP config on AGG-03 (2h ago)                     ║
║    Risk: medium. BUT: AGG-03 serves TX-4471-MUM only partially.     ║
║    TX-4474-PUN (also down) does NOT use AGG-03.                     ║
║    → Config change is UNLIKELY cause (doesn't explain both towers)   ║
║                                                                      ║
║  REASONING:                                                          ║
║    - Both towers on same fiber: DOWN                                 ║
║    - Fiber LOS at km 47                                              ║
║    - Roadwork permit at km 45-50 (2 days ago)                        ║
║    - BGP change doesn't explain multi-site failure                   ║
║    → PRIMARY HYPOTHESIS: Fiber cut at ~km 47 due to construction     ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 3                                                         ║
║  Model: GPT-4o (final synthesis)                                     ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  THOUGHT: "Let me confirm the performance data shows complete        ║
║    service loss consistent with fiber cut, and check if backup       ║
║    microwave link can provide temporary service."                    ║
║                                                                      ║
║  ACTION: get_performance("TX-4471-MUM", "all", "last_1_hour")        ║
║                                                                      ║
║  PERFORMANCE RESULT:                                                 ║
║    TX-4471-MUM KPI summary:                                          ║
║    connected_ues: 0 (was 12,450) ← COMPLETE LOSS                     ║
║    backhaul_utilization: 0% (was 67%) ← NO TRAFFIC                   ║
║    All KPIs dropped to zero at 10:00:32Z                            ║
║    Pattern: SIMULTANEOUS_TOTAL_LOSS (consistent with backhaul cut)   ║
║                                                                      ║
║  BACKUP LINK CHECK:                                                  ║
║    Microwave link MW-07:                                             ║
║    Status: Available, not currently carrying traffic                 ║
║    Capacity: 200 Mbps (fiber was 10 Gbps — 50× less)                 ║
║    Can serve: ~2,000 subscribers (out of 15,000) at reduced QoS     ║
║    Switchover command: Available (automated via NMS)                 ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║  FINAL DIAGNOSTIC REPORT                                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  {                                                                   ║
║    "primary_hypothesis": {                                           ║
║      "fault_type": "BACKHAUL_FIBER_CUT",                             ║
║      "probability": 0.91,                                            ║
║      "location_estimate": "Fiber route MUM-AHM-12, km 45-48",       ║
║      "probable_cause": "Construction excavation (permit issued       ║
║                         2024-07-22 for roadwork at km 45-50)",      ║
║      "evidence": [                                                   ║
║        {"claim": "Backhaul LOS was first alarm (10:00:30)",         ║
║         "source": "get_alarms"},                                     ║
║        {"claim": "2 towers on same fiber both down",                ║
║         "source": "check_neighbors + get_topology"},                 ║
║        {"claim": "Fiber LOS at ~km 47",                              ║
║         "source": "get_topology"},                                    ║
║        {"claim": "Roadwork permit at km 45-50 (2 days ago)",        ║
║         "source": "get_topology (construction records)"},            ║
║        {"claim": "All KPIs zero simultaneously (complete loss)",    ║
║         "source": "get_performance"}                                  ║
║      ]                                                               ║
║    },                                                                ║
║    "secondary_hypothesis": {                                         ║
║      "fault_type": "AGGREGATION_SWITCH_FAILURE",                     ║
║      "probability": 0.06,                                            ║
║      "reason": "AGG-03 also serves this tower, but doesn't          ║
║                 explain TX-4474-PUN being down"                      ║
║    },                                                                ║
║    "dispatch_recommendation": {                                      ║
║      "team": "Fiber Repair Team (Region West)",                      ║
║      "equipment": ["OTDR tester", "fusion splicer",                  ║
║                    "spare fiber cable (1km)", "excavation gear"],    ║
║      "dispatch_location": "NH-48, km marker 47, Mumbai side",        ║
║      "estimated_repair_time": "3-5 hours",                           ║
║      "priority": "P1 — 15,000 subscribers affected"                  ║
║    },                                                                ║
║    "immediate_mitigation": {                                         ║
║      "action": "Activate microwave backup link MW-07",               ║
║      "capacity": "200 Mbps (serves ~2,000 subscribers)",             ║
║      "command": "nms switchover --from Fiber-MUM-AHM-12              ║
║                  --to MW-07 --tower TX-4471-MUM",                    ║
║      "impact": "Reduced throughput for priority subscribers.         ║
║                Non-priority traffic queued.",                        ║
║      "recommended": "YES — restore partial service immediately"      ║
║    },                                                                ║
║    "customer_impact": {                                              ║
║      "subscribers_affected": 15000,                                  ║
║      "area": "Mumbai Western Suburbs, Sector 7",                     ║
║      "estimated_sla_penalty": "$75,000-$150,000 if > 2 hours",      ║
║      "priority_customers": 47 (enterprise circuits)                  ║
║    },                                                                ║
║    "confidence": 0.91                                                ║
║  }                                                                   ║
║                                                                      ║
║  INVESTIGATION TIME: 78 seconds                                      ║
║  TOTAL TOKENS: 6,200                                                 ║
║  TOTAL COST: $0.05                                                   ║
║  ITERATIONS: 3                                                       ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

### <a id="a-context"></a>CONTEXT ENGINEERING FOR NETWORK DATA

#### The Unique Challenge: Alarm Data Is Extremely Noisy

```
PROBLEM: A single tower can generate 100+ alarms per minute during a
major failure. The alarm data is REPETITIVE (same alarm re-fires every
10 seconds), INTERDEPENDENT (one failure triggers cascading alarms),
and NOISY (irrelevant alarms mixed with critical ones).

RAW ALARM DATA (from get_alarms):
  10:00:30 [CRITICAL] Backhaul LOS detected — Port 1/1/1
  10:00:32 [CRITICAL] gNB unreachable — gNB ID 4471
  10:00:35 [CRITICAL] S1 connection lost — peer AMF-MUM-01
  10:00:38 [CRITICAL] Backhaul LOS detected — Port 1/1/1  ← DUPLICATE
  10:00:40 [CRITICAL] Clock sync lost — PTP grandmaster
  10:00:42 [MAJOR] RRU-1 offline — Radio unit 1
  10:00:44 [MAJOR] RRU-2 offline — Radio unit 2
  10:00:46 [CRITICAL] Backhaul LOS detected — Port 1/1/1  ← DUPLICATE
  10:00:48 [CRITICAL] gNB unreachable — gNB ID 4471       ← DUPLICATE
  10:00:50 [MAJOR] Handover failure — all targets
  10:00:52 [MINOR] Door open — cabinet 3
  10:00:54 [CRITICAL] Backhaul LOS detected — Port 1/1/1  ← DUPLICATE
  ... (87 more alarms in the next 3 minutes)

COMPRESSION STRATEGY FOR ALARM DATA:
  1. DEDUPLICATE: Group identical alarms, show count
  2. TIMELINE: Show FIRST occurrence of each alarm type
  3. SEVERITY FILTER: Critical + Major only (skip Minor unless relevant)
  4. CORRELATION: Group cascading alarms
  5. ROOT CAUSE HINT: Highlight the alarm that fired FIRST

COMPRESSED RESULT (380 tokens):
  Alarms for TX-4471-MUM (101 total, 4 critical, 3 major):

  TIMELINE (first occurrence):
  10:00:30 [CRITICAL] Backhaul LOS ← FIRST ALARM (likely root cause)
  10:00:32 [CRITICAL] gNB unreachable (cascaded from backhaul loss)
  10:00:35 [CRITICAL] S1 connection lost (cascaded)
  10:00:40 [CRITICAL] Clock sync lost (cascaded — lost PTP from backhaul)
  10:00:42 [MAJOR] RRU-1 offline (cascaded — lost fronthaul)
  10:00:44 [MAJOR] RRU-2 offline (cascaded)

  DEDUPLICATION: "Backhaul LOS" re-fired 23× (suppressed)
                 "gNB unreachable" re-fired 18× (suppressed)

  IRRELEVANT: "Door open" alarm (minor, unrelated)

  PATTERN: Single root cause (backhaul LOS) → 6 cascading alarm types

This compression turns 101 alarms into 8 lines. The agent can reason
about the PATTERN instead of drowning in individual alarms.
```

---

### <a id="a-qa"></a>INTERVIEW Q&As — FAULT ISOLATION AGENT

**Q: "How does this compare to existing telecom fault management systems?"**

```
"Existing fault management systems (Ericsson ENIQ, Huawei U2020) are
rule-based. They show alarms and their probable cause codes, but they
don't CORRELATE across systems. They can't check whether a BGP config
change 2 hours ago is related to this outage. They can't cross-reference
construction permits with fiber route locations.

The agent adds CROSS-DOMAIN CORRELATION. It pulls data from the fault
management system, topology graph, change management system, performance
manager, and even external data (construction permits, weather feeds).
The LLM reasons across all these domains simultaneously.

The existing systems also can't DISPATCH. They show alarms and wait for
the human to decide. The agent produces a diagnostic report AND a
dispatch recommendation with the right equipment and location."
```

**Q: "Why use an LLM for fault isolation? Why not a decision tree algorithm?"**

```
"Great question. For KNOWN fault patterns (backhaul LOS → fiber cut),
a deterministic decision tree is better — faster, cheaper, 100%
reproducible. I'd use rule-based automation for those.

The LLM agent is for the 30% of faults that DON'T match known patterns.
Novel failure modes, multi-fault scenarios (fiber cut + config change
happened simultaneously), and ambiguous alarm patterns. The LLM can
reason about these in ways decision trees can't.

The ideal system is HYBRID: rules for known patterns (70% of cases),
agent for novel patterns (30% of cases). The agent kicks in when the
rule engine says 'unknown fault pattern' or 'multiple conflicting
hypotheses.'"
```

**Q: "How accurate is the agent's fault diagnosis?"**

```
"Based on 200 incidents validated against post-mortem reports:
  - Primary hypothesis correct: 89%
  - Primary or secondary hypothesis correct: 94%
  - Completely wrong (all hypotheses missed): 6%

The 6% misses were almost all novel fault types the agent hadn't seen
before. As the GraphRAG knowledge base accumulates more post-mortem
data, accuracy improves. The agent also explicitly escalates when
confidence is below 60%, so the 6% misses typically get escalated to
human SREs rather than acted on incorrectly."
```

**Q: "What about false positives? The agent says fiber cut but it's actually a config error."**

```
"The agent produces RANKED hypotheses with probabilities. It doesn't
give one answer. In your example, it would say: 'Primary: fiber cut
(91%). Secondary: config error (6%).' The human SRE reviews both.

The evidence-based output means each hypothesis cites the tool results
that support it. If the SRE disagrees with the primary hypothesis,
they can look at the evidence and decide whether the secondary is more
likely.

Additionally, the dispatch recommendation includes a VERIFY step:
'Before starting fiber repair, verify with OTDR test.' This ensures
the field tech confirms the diagnosis before committing to an
expensive repair."
```

---

### <a id="a-pitch"></a>THE 90-SECOND PITCH — FAULT ISOLATION

```
[0-15 sec]
"When a 5G tower goes down at AT&T, the on-call engineer plays detective
across 6 different systems for 25 minutes before they even know WHERE to
send a field tech — let alone what equipment to bring."

[15-40 sec]
"I designed a Network Fault Isolation Agent that investigates in under
90 seconds. It has 5 tools: alarm lookup, topology graph traversal,
neighbor status check, change management search, and performance KPI
analysis. The agent reasons through a decision tree: are neighbors also
down? If yes, it's a shared infrastructure failure. If no, it's a local
site issue. It correlates alarm timestamps, recent config changes, and
even construction permits near fiber routes."

[40-60 sec]
"The output is a ranked fault hypothesis with evidence and — critically
— a dispatch recommendation with the RIGHT equipment. If it's a fiber
cut, the field tech gets an OTDR tester and splicing gear. If it's a
config error, it's a remote fix with no dispatch needed. The difference
between 'go investigate' and 'go fix this specific thing at km 47' is
the difference between a 2-hour MTTR and a 4-hour MTTR."

[60-75 sec]
"Based on the Vodafone model, this would reduce MTTR by 50% and outages
by 30%. At AT&T's scale — 100,000+ cell sites — even a 10% MTTR
improvement saves $50M+ annually in SLA penalties."

[75-90 sec]
"What makes this work is telecom domain expertise combined with AI. The
agent doesn't just read alarms — it understands 3GPP alarm codes, BGP
topology, 5G core architecture, and fiber network physics. You need
both the telecom knowledge and the AI engineering to build this."
```


---


## PROJECT B: CAPACITY PLANNING AGENT
### Based on: Verizon / Deutsche Telekom Network Capacity AI

---

### <a id="b-problem"></a>THE PROBLEM — CAPACITY PLANNING AT SCALE

```
THE CHALLENGE:
  Telecom networks are PLANNED 6-18 months in advance.
  Building a new fiber route: 6-12 months (right-of-way, permits, construction).
  Adding a 100G wavelength: 1-3 months (equipment ordering, configuration, testing).
  Upgrading a cell site: 2-4 months (equipment, tower crew, RF planning).

  If you wait until capacity is exhausted to order upgrades, you're
  6 months too late. Customers experience degraded service. SLAs are
  breached. Competitors poach subscribers.

THE CURRENT PROCESS (Manual, Slow, Error-Prone):
  1. Capacity team pulls utilization reports monthly (Excel)
  2. Manually identifies routes above 70% utilization
  3. Cross-references with subscriber growth projections (another team)
  4. Checks event calendars (Diwali, IPL, elections → traffic spikes)
  5. Writes a capacity augmentation proposal
  6. Submits for budget approval (takes 4-6 weeks)
  7. If approved, orders equipment and schedules construction

  Total time from "we need more capacity" to "capacity added": 4-8 months.
  Often too late.

THE GOAL:
  An AI agent that continuously monitors utilization, forecasts when
  routes will hit capacity, correlates with growth and events, and
  produces actionable augmentation recommendations — weeks before
  exhaustion.

BASED ON:
  Verizon capacity planning AI: Automated 80% of capacity decisions,
  reduced planning cycle from months to days.
  Deutsche Telekom network analytics: Predictive capacity modeling
  with 92% forecasting accuracy.
```

---

### <a id="b-architecture"></a>SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│              CAPACITY PLANNING AGENT ARCHITECTURE                       │
│                                                                         │
│  ┌──────────┐  Scheduled   ┌──────────────┐                            │
│  │ Cron     │  weekly or   │ Capacity     │                            │
│  │ Trigger  │  on-demand   │ Planning     │                            │
│  │          │ ──────────>  │ Agent        │                            │
│  └──────────┘              │ (ReAct Loop) │                            │
│                            └──────┬───────┘                            │
│                                   │                                     │
│       ┌───────────────────────────┼────────────────────────────┐       │
│       │                           │                            │       │
│       ▼                           ▼                            ▼       │
│  ┌─────────┐          ┌──────────────┐          ┌──────────────────┐   │
│  │ TOOL 1  │          │ TOOL 2       │          │ TOOL 3           │   │
│  │ query_  │          │ get_growth_  │          │ get_events       │   │
│  │ traffic │          │ forecast     │          │                  │   │
│  │         │          │              │          │ Festivals,       │   │
│  │ 30-day  │          │ Subscriber   │          │ sports (IPL),    │   │
│  │ traffic │          │ growth       │          │ elections,       │   │
│  │ utilization│        │ projections  │          │ concerts,        │   │
│  │ (Prometheus│         │ for region   │          │ public holidays  │   │
│  │  /InfluxDB│)         │              │          │                  │   │
│  └─────────┘          └──────────────┘          └──────────────────┘   │
│                                                                        │
│  ┌─────────────────┐          ┌──────────────────────────────┐         │
│  │ TOOL 4          │          │ TOOL 5                       │         │
│  │ get_capacity    │          │ get_budget                   │         │
│  │                 │          │                              │         │
│  │ Current max     │          │ Available capex for          │         │
│  │ capacity,       │          │ network upgrades in region   │         │
│  │ equipment type, │          │ + ROI thresholds             │         │
│  │ upgrade options │          │                              │         │
│  └─────────────────┘          └──────────────────────────────┘         │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                  FORECASTING ENGINE                           │      │
│  │                                                              │      │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │      │
│  │  │ Linear       │  │ Seasonal     │  │ Event-adjusted   │   │      │
│  │  │ Trend        │  │ Decomposition│  │ Forecast         │   │      │
│  │  │ Extrapolation│  │ (weekly/     │  │ (spike modeling) │   │      │
│  │  │              │  │  monthly     │  │                  │   │      │
│  │  │ "Growth is   │  │  patterns)   │  │ "Diwali = +35%   │   │      │
│  │  │  +3%/month"  │  │              │  │  for 3 days"     │   │      │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │      │
│  │                                                              │      │
│  │  OUTPUT: Time-series forecast with confidence intervals     │      │
│  │  "Route will hit 85% utilization by October 15 (±7 days)"  │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                  RISK & ROI ENGINE                            │      │
│  │                                                              │      │
│  │  ┌──────────────────┐  ┌──────────────────┐                 │      │
│  │  │ SLA Risk Model   │  │ ROI Calculator   │                 │      │
│  │  │                  │  │                  │                 │      │
│  │  │ "If route over-  │  │ "Upgrade cost:   │                 │      │
│  │  │ flows for 3 hrs  │  │  $340K.          │                 │      │
│  │  │ during Diwali:   │  │  SLA penalty     │                 │      │
│  │  │ $2.3M penalty"   │  │  avoided: $2M   │                 │      │
│  │  │                  │  │  ROI: 488%"     │                 │      │
│  │  └──────────────────┘  └──────────────────┘                 │      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### <a id="b-tools"></a>THE 5 TOOLS — COMPLETE SPECIFICATIONS

#### Tool 1: query_traffic

```python
def query_traffic(route_id: str, time_range: str = "last_30_days",
                  granularity: str = "hourly") -> dict:
    """
    Query historical traffic utilization for a fiber route or link.

    Telecom-specific metrics:
      - Current utilization (% of capacity)
      - Peak utilization ( busiest hour per day)
      - 95th percentile utilization (industry-standard billing metric)
      - Directional split (east-bound vs west-bound)
      - Service breakdown (voice, data, video, enterprise)
      - Growth rate month-over-month

    Source: Performance Management System (InfluxDB / Prometheus)
            + NetFlow / sFlow data from routers

    Returns (compressed):
    {
        "route": "Fiber-MUM-AHM-12",
        "capacity_gbps": 100,
        "current_utilization_avg": 67.5,
        "current_utilization_peak": 82.1,
        "current_utilization_p95": 78.3,
        "growth_rate_monthly": 3.2,  # +3.2% per month
        "trend": "INCREASING",
        "30_day_pattern": {
            "weekday_avg": 65.2,
            "weekend_avg": 72.1,
            "peak_hour": "20:00-21:00",
            "peak_utilization": 82.1
        }
    }

    Cache: 6 hours (traffic data updates hourly, trends are stable)
    Timeout: 15 seconds
    """
```

#### Tool 2: get_growth_forecast

```python
def get_growth_forecast(region: str, months_ahead: int = 6) -> dict:
    """
    Get subscriber growth and data usage projections for a region.

    Sources:
      - CRM subscriber count (current + historical)
      - Market research (competitor activity, demographics)
      - Device upgrade cycles (more 5G phones = more data usage)
      - Enterprise pipeline (known deals that will add capacity demand)

    Returns:
    {
        "region": "Maharashtra West",
        "current_subscribers": 4_850_000,
        "projected_subscribers_6m": 5_320_000,
        "subscriber_growth_rate_monthly": 1.9,
        "data_usage_per_subscriber_gb": 18.5,  # currently
        "projected_usage_per_subscriber_6m": 24.2,  # +30% (5G adoption)
        "total_data_growth_monthly": 4.8,  # subs growth + usage growth
        "enterprise_pipeline": {
            "confirmed_deals": 3,  # new enterprise customers
            "projected_capacity_demand": "+12 Gbps",
            "onboarding_date": "2024-10-01"
        },
        "key_driver": "5G smartphone adoption driving per-user data up 30%"
    }

    Cache: 24 hours (growth projections update monthly)
    Timeout: 10 seconds
    """
```

#### Tool 3: get_events

```python
def get_events(region: str, date_range_months: int = 6) -> dict:
    """
    Get upcoming events that will cause traffic spikes.

    THIS IS THE MOST TELECOM-SPECIFIC TOOL.
    In India, events cause MASSIVE spikes:

    Events tracked:
      - Festivals: Diwali (+35-50% for 3-5 days), Holi, Eid, Ganesh Chaturthi
      - Sports: IPL (April-May, +20-40% during matches), Cricket World Cup
      - Elections: Voting day (+15-25%), Results day (+30%)
      - Concerts/Events: Large gatherings, tech conferences
      - Public Holidays: National holidays (domestic roaming patterns)
      - Weather events: Monsoon onset (changes usage patterns)
      - Breaking News: Major events (+25% surge, unpredictable)

    Returns:
    {
        "region": "Maharashtra West",
        "upcoming_events": [
            {
                "name": "Diwali Festival",
                "date": "2024-10-28 to 2024-11-03",
                "expected_traffic_spike": "+42%",
                "duration_days": 5,
                "historical_impact": "Last year: peak 89% utilization on Fiber-MUM-AHM",
                "risk_level": "HIGH"
            },
            {
                "name": "India vs Australia Cricket (Wankhede)",
                "date": "2024-09-15",
                "expected_traffic_spike": "+25%",
                "duration_hours": 8,
                "affected_routes": ["Fiber-MUM-CST-03", "Fiber-MUM-AHM-12"],
                "risk_level": "MEDIUM"
            },
            {
                "name": "Maharashtra State Elections",
                "date": "2024-10-15",
                "expected_spike": "+20%",
                "risk_level": "MEDIUM"
            }
        ],
        "peak_risk_event": {
            "event": "Diwali Festival",
            "projected_peak_utilization": "94% on Fiber-MUM-AHM-12",
            "without_upgrade": "ROUTE WILL OVERFLOW",
            "overflow_probability": 0.78
        }
    }

    Source: Event calendar API + historical correlation database
    Cache: 24 hours
    Timeout: 5 seconds
    """
```

#### Tool 4: get_capacity

```python
def get_capacity(route_id: str) -> dict:
    """
    Get current capacity configuration and available upgrade options.

    Returns:
    {
        "route": "Fiber-MUM-AHM-12",
        "current_capacity_gbps": 100,
        "fiber_strand_count": 96,
        "active_wavelengths": 2,  # 2 × 100G = 200G lit capacity
        "dark_fiber_available": true,  # unlit strands available
        "max_theoretical_capacity_gbps": 9600,  # 96 strands × 100G
        "upgrade_options": [
            {
                "option": "Add 100G wavelength",
                "additional_capacity_gbps": 100,
                "cost_usd": 45_000,
                "time_to_deploy_weeks": 4,
                "equipment": "100G DWDM transponder",
                "feasibility": "IMMEDIATE"  # dark fiber available
            },
            {
                "option": "Upgrade to 400G wavelength",
                "additional_capacity_gbps": 300,
                "cost_usd": 120_000,
                "time_to_deploy_weeks": 8,
                "equipment": "400G DWDM transponder + amplifiers",
                "feasibility": "REQUIRES AMPLIFIER UPGRADE"
            },
            {
                "option": "Add new fiber route (redundancy)",
                "additional_capacity_gbps": 9600,
                "cost_usd": 2_400_000,
                "time_to_deploy_months": 8,
                "feasibility": "LONG_TERM"
            }
        ],
        "recommended_option": "Add 100G wavelength (cost-effective, fast)"
    }

    Cache: 1 week (capacity configs change rarely)
    Timeout: 5 seconds
    """
```

#### Tool 5: get_budget

```python
def get_budget(region: str) -> dict:
    """
    Get available capex budget and ROI thresholds for capacity upgrades.

    Returns:
    {
        "region": "Maharashtra West",
        "fy_budget_remaining_usd": 4_200_000,
        "fy_spend_rate": "ON_TRACK",  # or "OVER" or "UNDER"
        "approval_thresholds": {
            "auto_approve_under": 50_000,     # Manager level
            "director_approval": "50K-250K",  # Director level
            "vp_approval": "250K-1M",         # VP level
            "cto_approval": "1M+"             # CTO level
        },
        "roi_thresholds": {
            "minimum_roi_percent": 150,
            "payback_period_max_months": 18,
            "sla_penalty_avoidance_weight": 3.0
        },
        "competing_priorities": [
            {"project": "Pune 5G expansion", "requested": 1.2M},
            {"project": "Nagpur backhaul upgrade", "requested": 800K}
        ]
    }

    Cache: 24 hours
    Timeout: 5 seconds
    """
```

---

### <a id="b-forecasting"></a>THE FORECASTING ENGINE

```python
class CapacityForecastEngine:
    """
    Combines traffic trends + subscriber growth + event modeling
    to forecast when a route will hit capacity.

    THREE FORECASTING COMPONENTS:

    1. BASE TREND (linear extrapolation):
       Current utilization: 67.5%
       Monthly growth rate: 3.2%
       Days until 85% (upgrade trigger): log(85/67.5) / log(1.032) ≈ 7 months
       → Base forecast: March 2025

    2. EVENT OVERLAY (seasonal spikes):
       Diwali (October): +42% for 5 days
       → During Diwali peak: utilization = 67.5% × 1.42 = 95.9%
       → OVERFLOW THRESHOLD (100%) during Diwali!

    3. ENTERPRISE DEMAND (step function):
       New enterprise deal onboarding October 1: +12 Gbps
       → On a 100G route, that's +12% utilization step
       → Post-onboarding base: 67.5% + 12% = 79.5%
       → With 3.2% monthly growth, hits 85% by December

    COMBINED FORECAST:
      "Without upgrade, this route will overflow during Diwali
       (October 28) with 94-96% utilization. Upgrade needed by
       September 15 to have 4 weeks of deployment buffer."
    """

    def forecast(self, traffic_data, growth_data, event_data,
                 capacity_data, months_ahead=6):

        current_util = traffic_data["current_utilization_avg"]
        monthly_growth = growth_data["data_growth_monthly"] / 100  # 4.8% → 0.048
        capacity_gbps = capacity_data["current_capacity_gbps"]

        # Month-by-month projection
        forecast = []
        for month in range(months_ahead):
            # Base projection
            projected_util = current_util * ((1 + monthly_growth) ** month)

            # Enterprise step (if onboarding this month)
            for deal in growth_data.get("enterprise_pipeline", {}).get("deals", []):
                if deal["onboarding_month"] == month:
                    step_gbps = deal["capacity_demand_gbps"]
                    projected_util += (step_gbps / capacity_gbps) * 100

            # Event spike (max event this month)
            max_spike = 0
            max_event = None
            for event in event_data.get("upcoming_events", []):
                if event["month"] == month:
                    spike = event.get("traffic_spike_percent", 0)
                    if spike > max_spike:
                        max_spike = spike / 100
                        max_event = event

            peak_util_with_event = projected_util * (1 + max_spike)

            forecast.append({
                "month": month,
                "base_utilization": round(projected_util, 1),
                "peak_with_events": round(peak_util_with_event, 1),
                "overflow_risk": peak_util_with_event >= 85,
                "critical_event": max_event["name"] if max_event else None,
                "days_until_85_percent": self._days_until_threshold(
                    projected_util, monthly_growth, 85
                ),
            })

        return forecast

    def _days_until_threshold(self, current, growth_rate, threshold):
        """Calculate days until utilization hits threshold."""
        import math
        if current >= threshold:
            return 0
        months = math.log(threshold / current) / math.log(1 + growth_rate)
        return int(months * 30.5)
```

---

### <a id="b-walkthrough"></a>REAL ANALYSIS WALKTHROUGH

```
INPUT: "Analyze capacity for Fiber-MUM-AHM-12. Do we need an upgrade before Diwali?"

╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 1: DATA GATHERING                                         ║
║  Model: GPT-4o-mini                                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  PARALLEL TOOL CALLS:                                                ║
║    query_traffic("Fiber-MUM-AHM-12", "last_90_days")                 ║
║    get_growth_forecast("Maharashtra West", months_ahead=6)           ║
║    get_events("Maharashtra West", 6)                                 ║
║    get_capacity("Fiber-MUM-AHM-12")                                  ║
║    get_budget("Maharashtra West")                                    ║
║                                                                      ║
║  RESULTS (compressed):                                               ║
║                                                                      ║
║  TRAFFIC:                                                            ║
║    Current: 67.5% avg, 82.1% peak                                    ║
║    Growth: +3.2%/month                                               ║
║    90-day trend: INCREASING (was 58% 3 months ago)                   ║
║                                                                      ║
║  GROWTH FORECAST:                                                    ║
║    Subscriber growth: +1.9%/month                                    ║
║    Data per subscriber: 18.5 GB → 24.2 GB in 6 months (+30%)        ║
║    Enterprise deal: +12 Gbps onboarding October 1                    ║
║    Combined data growth: +4.8%/month                                 ║
║                                                                      ║
║  EVENTS:                                                             ║
║    Diwali (Oct 28 - Nov 3): +42% spike, 5 days                       ║
║    Cricket match (Sep 15): +25%, 8 hours                             ║
║    Elections (Oct 15): +20%, 1 day                                   ║
║                                                                      ║
║  CAPACITY:                                                           ║
║    Current: 100 Gbps (2 × 100G wavelengths)                          ║
║    Dark fiber available: YES                                         ║
║    Upgrade: Add 100G wavelength → +100 Gbps, cost $45K, 4 weeks      ║
║                                                                      ║
║  BUDGET:                                                             ║
║    Remaining FY budget: $4.2M                                        ║
║    Auto-approve threshold: <$50K                                     ║
║    ROI minimum: 150%                                                 ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║  ITERATION 2: FORECASTING & ANALYSIS                                 ║
║  Model: GPT-4o (complex reasoning)                                   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  FORECAST TABLE:                                                     ║
║                                                                      ║
║  Month    Base Util   Peak (events)   Overflow?   Critical Event     ║
║  ─────    ────────   ─────────────   ─────────   ──────────────      ║
║  Aug      67.5%      67.5%           No          —                   ║
║  Sep      71.0%      88.8% ⚠️         YES (cricket) Cricket match     ║
║  Oct      74.4%      79.4% + 12% enterprise = 91.4% ⚠️  YES          ║
║            ────      Diwali peak: 91.4% × 1.42 = 129% 💀 OVERFLOW     ║
║  Nov      78.0%      110.8% 💀        YES (Diwali remnant)            ║
║  Dec      81.7%      81.7%           Approaching limit               ║
║  Jan      85.6% 💀   85.6%           YES (base traffic alone)        ║
║                                                                      ║
║  KEY FINDINGS:                                                       ║
║  1. September cricket match: 88.8% peak — risky but manageable       ║
║  2. October Diwali: projected 129% — CATASTROPHIC OVERFLOW            ║
║     The route literally cannot carry this much traffic.              ║
║     Customers will experience complete service denial.               ║
║  3. January: base traffic alone hits 85.6% — upgrade mandatory       ║
║                                                                      ║
║  CONCLUSION: Upgrade is needed BEFORE September 15 (cricket)         ║
║  and absolutely before October 1 (enterprise onboarding + Diwali).   ║
║  Target: Upgrade complete by August 31.                              ║
║  Order by: July 31 (4-week deploy time from equipment order).        ║
║  THAT'S NOW — order must be placed this week.                        ║
╚══════════════════════════════════════════════════════════════════════╝
                              │
                              ▼
╔══════════════════════════════════════════════════════════════════════╗
║  FINAL CAPACITY AUGMENTATION REPORT                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  {                                                                   ║
║    "route": "Fiber-MUM-AHM-12",                                     ║
║    "urgency": "CRITICAL",                                           ║
║    "action_required": "Order 100G wavelength upgrade THIS WEEK",     ║
║    "deadline": "August 31, 2024 (before September cricket)",        ║
║                                                                      ║
║    "forecast": {                                                     ║
║      "current_utilization": "67.5% avg, 82.1% peak",               ║
║      "without_upgrade": {                                            ║
║        "september_peak": "88.8% (cricket match) — RISKY",          ║
║        "october_diwali": "129% projected — CATASTROPHIC",          ║
║        "january_base": "85.6% — exceeds upgrade threshold",        ║
║        "overflow_events": 3                                          ║
║      },                                                              ║
║      "with_upgrade": {                                               ║
║        "new_capacity": "200 Gbps (100G → 200G)",                    ║
║        "post_upgrade_utilization": "33.8% avg — HEALTHY",          ║
║        "diwali_post_upgrade": "64.6% — COMFORTABLE",               ║
║        "january_post_upgrade": "42.8% — EXCELLENT",                ║
║        "years_of_headroom": "~3 years at current growth rate"       ║
║      }                                                               ║
║    },                                                                ║
║                                                                      ║
║    "upgrade_recommendation": {                                       ║
║      "option": "Add 100G DWDM wavelength",                          ║
║      "cost": "$45,000",                                             ║
║      "deploy_time": "4 weeks",                                       ║
║      "order_by": "July 31, 2024",                                   ║
║      "approval_level": "AUTO-APPROVE (under $50K threshold)",       ║
║      "equipment": "100G DWDM transponder (Cisco/Juniper/Nokia)",     ║
║      "dark_fiber": "Available — strand 47 (ready to light)",        ║
║      "installation": "Remote activation (no field visit needed)"    ║
║    },                                                                ║
║                                                                      ║
║    "roi_analysis": {                                                 ║
║      "upgrade_cost": "$45,000",                                     ║
║      "sla_penalty_if_no_upgrade": {                                  ║
║        "diwali_overflow_3_days": "$1,800,000",                      ║
║        "cricket_match_degradation": "$150,000",                     ║
║        "monthly_degradation_jan_onward": "$200,000/month",           ║
║        "total_6month_risk": "$3,150,000"                             ║
║      },                                                              ║
║      "roi": "6,900%",                                               ║
║      "payback_period": "< 1 month",                                  ║
║      "recommendation": "EXECUTE IMMEDIATELY"                        ║
║    },                                                                ║
║                                                                      ║
║    "risk_if_delayed": {                                              ║
║      "if_ordered_august_1": "Deploy by Sep 1. Misses cricket.       ║
║                               Diwali risk remains if delays.",      ║
║      "if_ordered_september_1": "Deploy by Oct 1. CRITICAL:          ║
║                                  Diwali overflow UNAVOIDABLE.",     ║
║      "if_not_upgraded": "Diwali overflow GUARANTEED.                ║
║                          15,000+ subscribers impacted.              ║
║                          Enterprise SLA breach for 3 customers."    ║
║    },                                                                ║
║                                                                      ║
║    "confidence": 0.92                                               ║
║  }                                                                   ║
║                                                                      ║
║  ANALYSIS TIME: 45 seconds                                           ║
║  ITERATIONS: 2                                                       ║
║  COST: $0.03                                                         ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

### <a id="b-risk"></a>RISK ANALYSIS & SLA MODELING

```python
class SLARiskModel:
    """
    Calculate SLA penalty risk based on capacity overflow projections.

    SLA STRUCTURE (typical telecom):
      Availability SLA: 99.95% monthly (4.3 hours downtime allowed)
      Throughput SLA: Commit Information Rate (CIR) guaranteed
      Latency SLA: < X ms p99

    Penalty structure (typical):
      Enterprise customers: $5,000-$50,000 per hour of SLA breach
      Consumer SLA: Service credits (1 day credit per hour of outage)
      Government/regulatory: Fines for emergency service (911/112) disruption

    The model calculates:
      Expected penalty = (overflow probability) × (hours affected) × (penalty rate)
    """

    def calculate_risk(self, forecast, sla_contracts, route_data):
        total_risk = 0
        risk_events = []

        for month in forecast:
            if month["peak_with_events"] >= 100:
                # OVERFLOW — service denial likely
                overflow_hours = self._estimate_overflow_hours(month)
                enterprise_penalty = overflow_hours * sla_contracts["enterprise_rate"]
                consumer_credits = overflow_hours * sla_contracts["consumer_rate"]

                risk_events.append({
                    "month": month["month"],
                    "event": month.get("critical_event", "base traffic"),
                    "overflow_hours_estimated": overflow_hours,
                    "enterprise_penalty": enterprise_penalty,
                    "consumer_credits": consumer_credits,
                    "regulatory_risk": "HIGH (911 service affected)",
                })
                total_risk += enterprise_penalty + consumer_credits

            elif month["peak_with_events"] >= 85:
                # APPROACHING LIMIT — degradation likely
                degradation_hours = self._estimate_degradation_hours(month)
                penalty = degradation_hours * sla_contracts["degradation_rate"]
                risk_events.append({
                    "month": month["month"],
                    "event": month.get("critical_event", "base traffic"),
                    "risk": "DEGRADATION",
                    "penalty": penalty,
                })
                total_risk += penalty

        return {
            "total_6month_risk_usd": total_risk,
            "risk_events": risk_events,
            "highest_risk_event": max(risk_events, key=lambda x: x.get("penalty", 0)),
        }
```

---

### <a id="b-qa"></a>INTERVIEW Q&As — CAPACITY PLANNING AGENT

**Q: "How is this different from existing capacity planning tools?"**

```
"Existing tools are REPORTING tools — they show you utilization dashboards
and flag routes above thresholds. They don't FORECAST or RECOMMEND.

The agent adds three things:
1. PREDICTIVE FORECASTING: Not just 'current utilization is 67%' but
   'projected to hit 85% by January, with Diwali causing overflow in October.'
2. CROSS-DOMAIN CORRELATION: Combines traffic data + subscriber growth +
   event calendar + enterprise pipeline + budget constraints. No existing
   tool does this.
3. ACTIONABLE RECOMMENDATIONS: 'Add 100G wavelength. Cost: $45K. ROI:
   6,900%. Order by July 31.' Not just 'this route is getting full.'
```

**Q: "How accurate is the forecasting?"**

```
"92% accuracy on 30-day forecasts, 85% on 90-day forecasts. I measure
accuracy by comparing projected utilization to actual utilization at the
forecast date.

The biggest source of error is UNPREDICTABLE events — a viral video causes
a traffic surge, or a competitor outage causes roaming overflow. These are
inherently unpredictable.

For predictable events (festivals, sports, elections), the model is highly
accurate because I have years of historical correlation data. Diwali
causes +35-50% every year with remarkable consistency.

The confidence interval widens with time: ±3% for 30 days, ±8% for 90 days.
I always include the confidence range in the forecast."
```

**Q: "What about 5G network slicing? Does that change capacity planning?"**

```
"Network slicing adds a dimension to capacity planning. Instead of one
pipe serving all traffic, 5G allows multiple virtual slices with
different QoS:
  - eMBB slice: high bandwidth (streaming, browsing)
  - URLLC slice: ultra-low latency (autonomous, industrial)
  - mMTC slice: massive IoT connections

The capacity agent needs to forecast per-SLICE utilization, not just
aggregate. A route might have 40% aggregate utilization but the URLLC
slice might be at 90% because it has a smaller allocation.

I'd extend the agent with slice-aware tools: query_slice_utilization(),
allocate_slice(), adjust_slice_quota(). The forecasting engine would
project each slice independently."
```

**Q: "How would you validate the agent's recommendations?"**

```
"Backtesting. I take historical capacity decisions — routes that were
upgraded in the past 2 years — and run the agent on the data that was
available at the time of the decision. Then I compare:
  - Did the agent recommend an upgrade when one was actually needed?
  - Did the agent's timeline match reality?
  - Did the agent predict the right capacity increase?

For routes that DIDN'T get upgraded but later had congestion, I check:
  - Did the agent predict the congestion?
  - How far in advance did it flag the risk?

This backtesting validates both the forecasting accuracy and the
recommendation quality. I'd run this quarterly to tune the model."
```

**Q: "What if the agent recommends an upgrade that turns out to be unnecessary?"**

```
"That's the false positive case — over-provisioning. It's expensive but
not catastrophic. The agent's ROI model includes the cost of unnecessary
upgrades in its calculations.

The key safeguard: the agent doesn't AUTO-ORDER. It recommends. A human
capacity planner reviews and approves. For upgrades under $50K (the auto-
approve threshold), the risk is low enough that false positives are
acceptable.

Over time, the agent's recommendation accuracy improves as it learns
from outcomes: 'I recommended a 100G upgrade in August. By December,
utilization was only 50%. I over-provisioned. Adjust my growth model
to be less aggressive.'"
```

---

### <a id="b-pitch"></a>THE 90-SECOND PITCH — CAPACITY PLANNING

```
[0-15 sec]
"Telecom capacity planning is done 6-18 months in advance. If you wait
until a fiber route is congested to order an upgrade, you're 4-8 months
too late. Customers experience degraded service, SLAs are breached, and
the SLA penalties can be in the millions."

[15-40 sec]
"I designed a Capacity Planning Agent that forecasts when routes will
hit capacity and recommends precise upgrades. It combines traffic
utilization data, subscriber growth projections, event calendars —
Diwali causes +42% spikes — enterprise deal pipelines, and budget
constraints. The forecasting engine projects month-by-month utilization
with event overlays."

[40-60 sec]
"The output is an actionable augmentation report. For example: 'Route
Fiber-MUM-AHM-12 will overflow during Diwali at 129% utilization.
Add a 100G wavelength by August 31. Cost: $45K. SLA penalty avoided:
$2.3M. ROI: 6,900%. Order this week.' It includes risk analysis:
'If delayed to September, Diwali overflow becomes unavoidable.'"

[60-75 sec]
"What makes this powerful is the cross-domain correlation. No single
system combines traffic data + subscriber growth + event calendars +
budget constraints. The agent pulls from all of them and produces a
unified forecast with financial impact."

[75-90 sec]
"Based on the Verizon model, this automates 80% of capacity decisions
and reduces planning cycles from months to days. At AT&T's scale,
preventing even one major SLA breach during a festival pays for the
entire system."
```
