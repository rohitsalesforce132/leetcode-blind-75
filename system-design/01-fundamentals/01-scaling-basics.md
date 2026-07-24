# Scaling Basics: From 1 User to Millions

> **The goal of this guide:** Understand how a web application grows from a single
> server serving one user to a globally distributed system serving millions — and
> be able to talk about every step of that journey in a system design interview.

---

## Table of Contents

1. [The Journey: One Server to Millions](#1-the-journey-one-server-to-millions)
2. [Vertical Scaling (Scaling Up)](#2-vertical-scaling-scaling-up)
3. [Horizontal Scaling (Scaling Out)](#3-horizontal-scaling-scaling-out)
4. [Load Balancers](#4-load-balancers)
5. [Stateful vs Stateless Servers](#5-stateful-vs-stateless-servers)
6. [Auto-Scaling Groups](#6-auto-scaling-groups)
7. [Content Delivery Networks (CDNs)](#7-content-delivery-networks-cdns)
8. [Putting It All Together](#8-putting-it-all-together)
9. [Interview Q&A](#9-interview-qa)

---

## 1. The Journey: One Server to Millions

### Real-World Analogy: The Restaurant 🍽️

Imagine you open a small restaurant. On day one, you have **one waiter** who takes
orders, cooks food, serves customers, and collects payment. That waiter *is* your
single server.

```
    [Customer]  ----request---->  [🧑‍🍳 ONE WAITER = ONE SERVER]
                                         (does everything)
```

- **A few customers?** The waiter handles it fine.
- **10 customers at once?** The waiter gets overwhelmed. Lines form.
- **100 customers?** Disaster. People leave hungry.

As demand grows, you make a series of decisions — and **each decision maps directly
to a system design concept**. Let's walk through them.

### The Scaling Ladder

```
 Step 1: Single Server           Step 2: Vertical Scaling         Step 3: Horizontal Scaling
 ┌──────────────┐                ┌──────────────┐                ┌──────────────────────┐
 │  User → 1 🖥️ │   ───────>    │  User → 1 💪🖥️│   ───────>    │  User → LB → 🖥️ 🖥️ 🖥️│
 │  (tiny)      │                │  (bigger box) │                │  (many machines)     │
 └──────────────┘                └──────────────┘                └──────────────────────┘
```

Every real-world product (Netflix, Uber, Airbnb) climbed this same ladder. Let's
examine each rung.

---

## 2. Vertical Scaling (Scaling Up)

### What Is It?

**Vertical scaling** means buying a *bigger, more powerful machine*. You add more
CPU, more RAM, faster disks — but you still have **one machine**.

```
   BEFORE (scale up)                      AFTER (scale up)
   ┌───────────────┐                      ┌───────────────────┐
   │  Server       │                      │  Server           │
   │  4 vCPU       │      upgrade ──>     │  64 vCPU          │
   │  8 GB RAM     │                      │  512 GB RAM       │
   │  100 GB SSD   │                      │  4 TB NVMe        │
   └───────────────┘                      └───────────────────┘
```

### Analogy: A Stronger Waiter 💪

Instead of hiring more waiters, you **send your one waiter to the gym**. Now he's
bigger and faster — he can carry more plates. But he's still *one person*.

### Pros & Cons

| Pros ✅                              | Cons ❌                                    |
|--------------------------------------|--------------------------------------------|
| Dead simple — no code changes needed | There's a **hard limit** (hardware ceiling)|
| No distribution complexity           | **Single point of failure** — it dies, everything dies |
| Cheaper at small scale               | Downtime required to upgrade               |

> ⚠️ **Interview tip:** Vertical scaling has a ceiling. You can't keep buying a
> bigger machine forever. Eventually, you *must* go horizontal.

---

## 3. Horizontal Scaling (Scaling Out)

### What Is It?

**Horizontal scaling** means adding **more machines** (nodes/servers) that work
together behind a load balancer. Each machine is identical.

```
                       ┌──────────────┐
                       │   Server A   │
   ┌──────────┐        │  🖥️          │
   │  Users   │ ─────> │              │
   │ 🧑🧑🧑🧑🧑  │        └──────────────┘
   │          │        ┌──────────────┐
   └──────────┘        │   Server B   │
                       │  🖥️          │
                       │              │
                       └──────────────┘
                       ┌──────────────┐
                       │   Server C   │
                       │  🖥️          │
                       └──────────────┘
```

### Analogy: Hiring More Waiters 👥👬👭

When the restaurant gets busy, you **hire more waiters**. Now there are 10 waiters
sharing the work. If one calls in sick, the others keep serving. The restaurant
stays open.

This is the key difference:

| Feature            | Vertical (Scale Up)       | Horizontal (Scale Out)      |
|--------------------|---------------------------|-----------------------------|
| Strategy           | Bigger machine            | More machines               |
| Limit              | Hardware ceiling          | Practically unlimited       |
| Failure resilience | Single point of failure   | If one dies, others survive |
| Complexity         | Low                       | Higher (coordination needed)|
| Code changes?      | Usually none              | Servers must be stateless   |

### The Catch: Statelessness

> To scale horizontally, your servers **must be stateless**. (We explain why in §5.)

---

## 4. Load Balancers

### What Is It?

A **load balancer (LB)** is a traffic cop that sits in front of your server pool and
**distributes incoming requests** across them. No user talks to a server directly —
they talk to the LB.

```
                          ┌──────────────────────────────────────────────┐
                          │              LOAD BALANCER                   │
                          │       (distributes traffic evenly)           │
                          └──────┬──────────┬──────────┬────────────────┘
                                 │          │          │
                          ┌──────▼──┐  ┌────▼───┐  ┌──▼───────┐
                          │Server A │  │Server B│  │Server C  │
                          │  🖥️     │  │  🖥️    │  │  🖥️      │
                          └─────────┘  └────────┘  └──────────┘
```

### Analogy: The Restaurant Host 🪑

The host at the front door doesn't cook — they **seat customers evenly** across all
available waiters so no single waiter gets overwhelmed. If a waiter goes on break,
the host stops sending new customers to them.

### Load Balancing Algorithms

| Algorithm         | How it works                                   | Good for                |
|-------------------|------------------------------------------------|-------------------------|
| **Round Robin**   | Send to A, then B, then C, then A…             | Equal-power servers     |
| **Least Connections** | Send to the server with fewest active requests | Unequal request loads   |
| **IP Hash**       | Hash the client IP → always same server        | Session "stickiness"    |
| **Random**        | Pick a server at random                         | Simple baselines        |

### Health Checks

The LB periodically pings each server ("Are you alive?"). If a server stops
responding, the LB **removes it from the pool** and stops sending traffic to it.

```
   LB:  "Server B, are you ok?" ──> [no response] ──> ❌ Remove B from rotation
         "Server A, are you ok?" ──> "Yes!"         ──> ✅ Keep A in rotation
```

> 💡 **Interview tip:** The LB is what makes horizontal scaling *possible*. Without
> it, users would have to know about individual servers, which defeats the purpose.

---

## 5. Stateful vs Stateless Servers

### Stateless (the scalable choice)

A **stateless server** doesn't remember anything about previous requests. Every
request contains **all the information needed** to process it. The server treats
every request as brand new.

### Stateful (the hard-to-scale choice)

A **stateful server** remembers information about a user across requests — e.g., a
shopping cart stored in the server's memory, or a login session.

### Analogy: The Waiter's Memory 🧠

- **Stateless waiter:** "Please tell me your order number with every request." Every
  time you speak to him, you remind him who you are. Any waiter can serve you.
- **Stateful waiter:** Remembers your order from earlier. If you get a *different*
  waiter, that waiter has no idea what you ordered. 😬

### Why This Matters for Scaling

```
   STATEFUL (BAD for scaling):
   ┌─────────┐    User logs in →    ┌──────────────┐
   │  User A │ ──────────────────> │  Server B    │   "I remember you!"
   │         │    Next request ──> │  Server C    │   "Who are you?! 💥"
   └─────────┘                     └──────────────┘
   ↑ Server C doesn't have A's session — request fails!

   STATELESS (GOOD for scaling):
   ┌─────────┐    Request + token → ┌──────────────┐
   │  User A │ ──────────────────> │  Any Server  │   "Token proves who you
   │         │                     │  🖥️          │    are. I can serve you!"
   └─────────┘                     └──────────────┘
   ↑ Any server can serve any request. Session lives in a shared store (e.g., Redis).
```

**The rule:** Move state *out* of the application servers and into a shared store
(database, Redis, JWT tokens). Then your app servers become interchangeable and
infinitely scalable.

| Aspect            | Stateless                       | Stateful                      |
|-------------------|---------------------------------|-------------------------------|
| Memory            | None per user                   | Remembers user sessions       |
| Scalability       | ⭐⭐⭐⭐⭐ Easy to scale          | ⭐⭐ Hard — must pin users    |
| Failure handling  | Any server can take over        | If server dies, session lost  |
| Example           | REST API with JWT tokens         | Traditional session in memory |

---

## 6. Auto-Scaling Groups

### What Is It?

An **auto-scaling group (ASG)** automatically **adds or removes servers** based on
current demand. Traffic spikes → spin up more servers. Traffic drops → shut them
down to save money.

### Analogy: On-Call Waiters 📞

The restaurant manager watches the dining room. At 7 PM (dinner rush), he calls in
extra waiters. At 3 AM (empty), he sends most of them home and keeps just one on
duty.

```
   HIGH TRAFFIC (auto-scale UP)            LOW TRAFFIC (auto-scale DOWN)
   ┌─────────────┐                         ┌─────────────┐
   │ CPU: 92% 🔴 │  ──> spin up 3 servers  │ CPU: 8% 🟢  │  ──> shut down 2 servers
   │ "Add more!" │                         │ "Too many!" │
   └─────────────┘                         └─────────────┘

         🖥️🖥️🖥️🖥️🖥️🖥️🖥️  (7 servers)              🖥️🖥️🖥️ (3 servers)
```

### Key Concepts

- **Scaling policies:** Rules like "if CPU > 70% for 5 minutes, add 2 servers"
- **Min/Max bounds:** e.g., "always keep at least 3, never more than 20"
- **Cooldown periods:** Wait a bit between scaling actions to avoid thrashing
- **Predictive scaling:** Use historical data to pre-scale before known spikes

> 💡 Cloud examples: AWS Auto Scaling Groups, GCP Managed Instance Groups, Azure VMSS.

---

## 7. Content Delivery Networks (CDNs)

### What Is It?

A **CDN** is a globally distributed network of servers that caches **static
content** (images, videos, CSS, JS) close to users. Instead of fetching a file from
your single data center in Virginia, a user in Tokyo fetches it from a Tokyo CDN
server — **dramatically faster**.

### Analogy: Restaurant Chains 🏢

Instead of one restaurant in New York serving the whole world, you open
**branches everywhere**. A customer in Tokyo eats at the Tokyo branch — no need to
fly to New York. The food is the same, but it arrives instantly.

```
   WITHOUT A CDN:
   ┌────────┐                        ┌──────────────────┐
   │ User   │  ── request ──────────>│ Origin Server    │
   │ Tokyo  │  <── 250ms latency ───│ (Virginia, USA)  │
   └────────┘                        └──────────────────┘
   ☹️ SLOW (halfway around the world)

   WITH A CDN:
   ┌────────┐     ┌───────────┐
   │ User   │ ──> │ CDN Edge  │   (Tokyo — has the file cached!)
   │ Tokyo  │ <── │ Tokyo     │
   └────────┘     └───────────┘
   😃 FAST (10ms, served locally)
```

### How a CDN Works (Cache Miss vs Hit)

```
   1. User requests /images/logo.png
   2. CDN checks: "Do I have it?"
      ├── YES (Cache HIT)  ──> Serve immediately (fast)
      └── NO  (Cache MISS) ──> Fetch from origin, cache copy, serve
```

### What Goes in a CDN?

| Cache it ✅                    | Don't cache ❌                  |
|--------------------------------|---------------------------------|
| Images, videos, audio          | Personalized user data          |
| CSS, JavaScript, fonts         | Shopping cart contents          |
| Static HTML pages              | Real-time dashboards            |
| Large file downloads           | Search results                  |

> Popular CDNs: Cloudflare, AWS CloudFront, Akamai, Fastly, Google Cloud CDN.

---

## 8. Putting It All Together

Here's the full evolution from one server to a scaled architecture:

```
   STAGE 1: Single Server              STAGE 2: + Load Balancer
   ┌──────┐                            ┌──────┐     ┌─────┐     ┌────────┐
   │ User │ ──> ┌──────────┐           │ User │ ──> │ LB  │ ──> │Servers │
   │      │     │ Server   │           │      │     └─────┘     │  A B C │
   └──────┘     │ 🖥️       │           └──────┘                 └────────┘
                │ (app+db) │           (horizontal scaling)
                └──────────┘

   STAGE 3: + CDN + Cache + DB Replica
   ┌──────┐     ┌─────┐     ┌────────┐
   │ User │ ──> │ CDN │ ──> │ LB     │
   │      │     └─────┘     └───┬────┘
   └──────┘                     │
                          ┌─────▼─────┐
                          │  App      │  ──> ┌──────────┐
                          │  Servers  │      │  Cache   │
                          │  (ASG)    │      │ (Redis)  │
                          └───────────┘      └──────────┘
                                │                  │ (miss)
                                ▼                  ▼
                          ┌──────────┐      ┌───────────┐
                          │ DB Read  │ <──> │ DB Master │
                          │ Replicas │      │ (writes)  │
                          └──────────┘      └───────────┘
```

### The Golden Rules of Scaling

1. **Go stateless** — move state into shared stores (Redis, databases).
2. **Scale horizontally** — add machines, not just bigger ones.
3. **Cache aggressively** — don't recompute what hasn't changed.
4. **Put static content in a CDN** — serve it close to users.
5. **Load balance everything** — never expose a single server.
6. **Auto-scale** — match capacity to demand automatically.

---

## 9. Interview Q&A

### Q: What's the difference between vertical and horizontal scaling?

**Vertical scaling** upgrades a single machine (more CPU/RAM). **Horizontal scaling**
adds more machines. Vertical is simpler but has a ceiling and a single point of
failure. Horizontal is more complex but scales further and is more resilient.

### Q: Why must servers be stateless to scale horizontally?

If a server stores session state (e.g., a user's login) in memory, then that user is
"pinned" to that server. The load balancer must always route them there. If that
server dies, the session is lost. Stateless servers let the LB send any request to
any server — enabling true horizontal scaling and easy failover.

### Q: When would you use a CDN, and what would you cache?

Use a CDN for **static, cacheable content** (images, videos, CSS, JS, static HTML)
to reduce latency for geographically distant users. **Don't** cache personalized or
real-time data (shopping carts, live dashboards).

### Q: How does a load balancer decide which server to use?

Common strategies: **round robin** (A→B→C→A), **least connections** (fewest active
requests), **IP hash** (same user → same server), and **weighted** (proportional to
server capacity). The LB also runs **health checks** to remove dead servers.

### Q: What is auto-scaling, and what metrics trigger it?

Auto-scaling automatically adds or removes servers based on demand. Triggers include
**CPU utilization**, **memory usage**, **request count**, **queue depth**, and
**response latency**. You set min/max bounds and cooldown periods to prevent thrashing.

### Q: Walk me through how you'd scale a system from 1 to 1 million users.

1. Start with a single server (app + DB).
2. **Separate app and database** onto different machines.
3. Add a **load balancer** and run **multiple app servers** (horizontal scaling).
4. Make app servers **stateless** (move sessions to Redis).
5. Add a **read replica** to handle heavy read traffic.
6. Add a **cache** (Redis/Memcached) for hot data.
7. Put **static assets behind a CDN**.
8. **Shard the database** when it outgrows a single machine.
9. **Auto-scale** the app tier based on traffic.
10. Go **multi-region** for global users and disaster recovery.

### Q: What's a single point of failure (SPOF), and how do you eliminate it?

A SPOF is any component whose failure brings down the whole system — e.g., a single
server, a single database, or a single load balancer. Eliminate SPOFs with
**redundancy**: multiple servers behind a load balancer, database replicas, and
multi-AZ or multi-region deployments.

### Q: Sticky sessions — good or bad?

Sticky sessions (the LB pins a user to one server) let you get away with stateful
servers temporarily, but they **hurt scalability and reliability**. If that server
dies, the session is lost. Prefer **stateless design** with shared session storage.

---

## Quick Reference Cheat Sheet

```
┌─────────────────────────────┬───────────────────────────────────────────┐
│ Concept                     │ One-liner                                 │
├─────────────────────────────┼───────────────────────────────────────────┤
│ Vertical Scaling            │ Bigger machine (scale up)                 │
│ Horizontal Scaling          │ More machines (scale out)                 │
│ Load Balancer               │ Distributes traffic across servers        │
│ Stateless                   │ Server remembers nothing between requests │
│ Auto-Scaling Group          │ Adds/removes servers based on demand      │
│ CDN                         │ Caches static content near users globally │
│ Single Point of Failure     │ One component whose death kills everything│
│ Read Replica                │ Copy of DB for read-heavy traffic         │
└─────────────────────────────┴───────────────────────────────────────────┘
```

---

**Next:** [02 — Databases & Caching →](02-databases-and-caching.md)
