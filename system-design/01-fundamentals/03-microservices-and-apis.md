# Microservices & APIs: Distributed Systems Architecture

> **The goal of this guide:** Understand monolith vs microservices tradeoffs, master
> API design (REST, GraphQL, gRPC), learn about API gateways and service discovery,
> and reason about sync vs async inter-service communication.

---

## Table of Contents

1. [Monolith vs Microservices](#1-monolith-vs-microservices)
2. [API Design: REST, GraphQL, gRPC](#2-api-design-rest-graphql-grpc)
3. [API Gateway](#3-api-gateway)
4. [Service Discovery](#4-service-discovery)
5. [Inter-Service Communication: Sync vs Async](#5-inter-service-communication-sync-vs-async)
6. [Event-Driven Architecture](#6-event-driven-architecture)
7. [Interview Q&A](#7-interview-qa)

---

## 1. Monolith vs Microservices

### Real-World Analogy: Mega-Store vs Specialty Shops 🏬🏪

**Monolith:** One giant mega-store (like Walmart) where every department — groceries,
electronics, pharmacy, clothing — is under one roof. If the power goes out, the
**entire store shuts down**. If you want to renovate the electronics section, you
have to close the whole store.

**Microservices:** A street of **specialty shops** — a bakery, an electronics store,
a pharmacy. Each runs independently. If the bakery's oven breaks, the pharmacy stays
open. You can renovate one shop without touching the others.

```
   MONOLITH:                              MICROSERVICES:
   ┌─────────────────────────────┐        ┌────────┐ ┌────────┐ ┌────────┐
   │  ┌─────┐  ┌─────┐  ┌─────┐ │        │ User   │ │ Order  │ │ Payment│
   │  │User │  │Order│  │Pay  │ │        │ Service│ │ Service│ │ Service│
   │  │Svc  │  │Svc  │  │Svc  │ │        │  🖥️    │ │  🖥️    │ │  🖥️    │
   │  └─────┘  └─────┘  └─────┘ │        └────────┘ └────────┘ └────────┘
   │  All in ONE codebase       │           Each is its own deployable unit
   │  ONE deployment            │           Independent scaling & deploys
   └─────────────────────────────┘           Communicate via APIs/messages
```

### Monolith: The Starting Point

A monolith is a **single application** containing all features. Early in a product's
life, this is usually the **right choice**.

| Pros ✅                                  | Cons ❌                                    |
|------------------------------------------|--------------------------------------------|
| Simple to build, test, and deploy        | Small change = redeploy **everything**     |
| Easy local development                   | **One bug can crash the whole app**        |
| In-process calls (fast, no network)      | Hard to scale just one part independently  |
| Single tech stack                        | Codebase becomes a giant tangled mess      |

### Microservices: The Scale Play

Each microservice is an **independently deployable** unit that owns its own data and
business logic. They communicate over the network.

| Pros ✅                                  | Cons ❌                                    |
|------------------------------------------|--------------------------------------------|
| Independent scaling (scale only what's hot)| **Distributed system complexity**        |
| Independent deployments (ship faster)    | Network calls are slower + can fail        |
| Team autonomy (own their service)        | Harder debugging across services           |
| Tech stack flexibility per service       | Data consistency across services is hard   |

### When Should You Move from Monolith to Microservices?

> **Almost never start with microservices.** Start with a monolith. Extract
> microservices **only when** you hit specific pain points:

```
   START HERE                 MIGRATE WHEN...
   ┌──────────────┐           ┌──────────────────────────────────────┐
   │              │           │ • The team grows beyond ~8 devs       │
   │  MONOLITH    │  ──────>  │ • Deployments are blocked by coupling │
   │              │           │ • Parts need independent scaling       │
   │              │           │ • Different parts need different tech  │
   └──────────────┘           └──────────────────────────────────────┘
```

> ⚠️ **Martin Fowler's advice:** "You almost always should start with a monolith."
> Premature microservices create massive complexity for little benefit.

---

## 2. API Design: REST, GraphQL, gRPC

### Real-World Analogy: Ordering at a Restaurant 🍽️

- **REST:** Like ordering from a fixed menu. "I'll have the /menu/burgers/item/42."
  You get exactly what's listed, nothing more, nothing less.
- **GraphQL:** Like a buffet where you say, "Give me the burger patty, cheese, and
  lettuce — but hold the bun and pickles." You get **exactly** what you ask for.
- **gRPC:** Like a private kitchen where chefs pass dishes through a high-speed
  service window. Fast, structured, but only for internal staff (not customers).

### REST (Representational State Transfer)

REST uses standard HTTP methods on **resources** identified by URLs.

```
   HTTP METHOD    URL                    ACTION
   ─────────────────────────────────────────────────────
   GET            /users/42              Fetch user #42
   POST           /users                 Create a new user
   PUT            /users/42              Update user #42 (full replace)
   PATCH          /users/42              Update user #42 (partial)
   DELETE         /users/42              Delete user #42
   GET            /users/42/orders       Fetch user #42's orders
```

**Characteristics:**
- Uses standard HTTP verbs (GET, POST, PUT, DELETE)
- Stateless — each request contains everything needed
- Returns JSON (usually)
- Cacheable via HTTP caching headers

**Pros:** Simple, universal, human-readable, great for public APIs.
**Cons:** **Over-fetching** (getting more data than needed) and **under-fetching**
(needing multiple requests to assemble a view).

```
   REST OVER-FETCHING:
   Request:  GET /users/42
   Response: { "id": 42, "name": "Alice", "bio": "...500 words...",
               "address": "...", "phone": "...", "50 other fields" }
   ↑ You only wanted the name, but got the entire user object!

   REST UNDER-FETCHING:
   To show a user's profile with their orders:
   Request 1: GET /users/42           ← get user info
   Request 2: GET /users/42/orders    ← get orders
   Request 3: GET /users/42/orders/101/items  ← get order items
   ↑ 3 round trips! (the "N+1 problem")
```

### GraphQL

A query language where the **client specifies exactly** what data it wants. The
server returns precisely that — no more, no less.

```
   GRAPHQL QUERY:                        GRAPHQL RESPONSE:
   query {                               {
     user(id: 42) {                        "user": {
       name                                  "name": "Alice",
       orders {                              "orders": [
         product                               { "product": "Laptop" },
         amount                                { "product": "Mouse", "amount": 25 }
       ]                                     ]
     }                                       }
   }                                       }
                                           }
   ↑ Client asked for name + order products. Got exactly that in ONE request!
```

**Pros:** No over/under-fetching. One endpoint. Great for mobile (less data).
**Cons:** More complex server setup. Harder to cache (single POST endpoint). N+1
query risk on the server side.

### gRPC

A high-performance RPC framework using **Protocol Buffers (protobuf)** for
serialization and **HTTP/2** for transport.

```
   gRPC SERVICE DEFINITION (protobuf):
   service UserService {
     rpc GetUser(GetUserRequest) returns (User);       // unary call
     rpc ListUsers(ListRequest) returns (stream User); // server streaming
   }

   CLIENT CALL:
   User user = userService.GetUser({id: 42});  // compiled, type-safe
```

**Pros:** Extremely fast (binary protocol), strongly typed, supports streaming,
built-in code generation for many languages.
**Cons:** Harder to debug (binary, not human-readable), less browser-friendly.

### Comparison Table

| Feature          | REST              | GraphQL           | gRPC                |
|------------------|-------------------|-------------------|---------------------|
| **Format**       | JSON/text         | JSON/text         | Protobuf (binary)   |
| **Speed**        | Medium            | Medium            | **Fast** 🔥         |
| **Flexibility**  | Fixed endpoints   | **Client decides**| Fixed contracts     |
| **Caching**      | **Easy** (HTTP)   | Hard              | Hard                |
| **Browser**      | **Great**         | **Great**         | Poor (needs gRPC-Web)|
| **Best for**     | Public APIs       | Mobile, complex UIs| Internal service-to-service |

> 💡 **Common pattern:** Use REST for **public-facing APIs**, gRPC for
> **internal service-to-service** communication, and GraphQL for **complex
> frontend data needs**.

---

## 3. API Gateway

### Real-World Analogy: The Restaurant Host Stand 🎩

In a large restaurant, the **host** greets you, checks your reservation
(authentication), routes you to the right section (routing), tells you about specials
(response transformation), and may limit how fast orders come into the kitchen (rate
limiting). The host doesn't cook — they **manage the flow**.

### What Is an API Gateway?

An API Gateway is the **single entry point** for all client requests. It sits in front
of your microservices and handles cross-cutting concerns:

```
                          ┌──────────────────────────────────┐
                          │          API GATEWAY             │
   ┌──────┐  ───────────> │  • Authentication               │
   │Client│   request     │  • Rate limiting                │
   └──────┘               │  • Routing to services           │
                          │  • Request/response transform    │
                          │  • SSL termination               │
                          │  • Response caching              │
                          └──┬─────┬─────┬─────┬─────────────┘
                             │     │     │     │
                          ┌──▼─┐ ┌─▼──┐ ┌─▼──┐ ┌▼───┐
                          │User│ │Order│ │Pay │ │Notif│
                          │Svc │ │Svc │ │Svc │ │Svc │
                          └────┘ └────┘ └────┘ └────┘
```

### What the Gateway Does

| Responsibility       | Description                                     |
|----------------------|-------------------------------------------------|
| **Routing**          | Forward /users → UserService, /orders → OrderService |
| **Authentication**   | Verify API keys/tokens once, not in every service|
| **Rate Limiting**    | Throttle abusive clients                        |
| **Load Balancing**   | Distribute across instances of a service        |
| **Response Caching** | Cache responses to reduce backend load          |
| **Protocol Translation** | Convert external REST to internal gRPC       |

### Pros & Cons

| Pros ✅                              | Cons ❌                                    |
|--------------------------------------|--------------------------------------------|
| Centralized cross-cutting concerns   | Gateway becomes a **SPOF** (needs HA)      |
| Clients talk to one endpoint         | Added latency (extra hop)                  |
| Services stay focused on business logic | New infrastructure to manage            |

> Popular gateways: Kong, AWS API Gateway, NGINX, Envoy, Traefik, Apigee.

---

## 4. Service Discovery

### Real-World Analogy: A Company Directory 📞

In a large company, you don't memorize everyone's phone number. You look them up in
the **company directory**. People change desks, new people join, some leave — the
directory is always current.

### The Problem

In microservices, services are **dynamic**: they start up, scale, move, and die.
Their IP addresses constantly change. How does the Order Service find the Payment
Service if Payment's IP changes every time it scales up?

### Service Discovery: The Solution

A **service registry** is a live directory of all services and their current
locations.

```
   ┌─────────────────────── SERVICE REGISTRY ────────────────────────┐
   │                                                                  │
   │  Service Name         │ Instances (IP:Port)                      │
   │  ─────────────────────┼───────────────────────────────────────── │
   │  user-service         │ 10.0.1.5:8080, 10.0.1.6:8080             │
   │  order-service        │ 10.0.1.10:9090                           │
   │  payment-service      │ 10.0.1.20:443, 10.0.1.21:443, 10.0.1.22 │
   │                                                                  │
   └──────────────────────────────────────────────────────────────────┘
        ▲                                          │
        │ register                                 │ lookup
        │ "I'm payment-service at 10.0.1.20:443"  │ "Where is payment-service?"
        │                                          ▼
   ┌────┴──────┐                          ┌───────────────┐
   │ Payment   │                          │ Order Service  │
   │ Service   │                          │ (needs to call │
   │           │                          │  payment)      │
   └───────────┘                          └───────────────┘
```

### Two Discovery Models

| Model               | How it works                                    | Example         |
|---------------------|-------------------------------------------------|-----------------|
| **Client-side**     | Client queries the registry, picks an instance  | Netflix Eureka  |
| **Server-side**     | A proxy (like Envoy) queries for the client     | Kubernetes + Istio|

### How It Works (Lifecycle)

```
   1. Payment Service starts ──> registers itself in the registry
                                  "payment-service @ 10.0.1.20:443"

   2. Order Service needs to call Payment ──> queries registry
                                  "Where is payment-service?"
                                  Registry: "10.0.1.20:443, 10.0.1.21:443"

   3. Order Service calls one of the returned addresses

   4. Payment Service dies ──> heartbeat stops ──> registry removes it
```

> Popular tools: Consul, etcd, Zookeeper, Kubernetes DNS, Netflix Eureka.

---

## 5. Inter-Service Communication: Sync vs Async

### Real-World Analogy: Phone Call vs Text Message 📱

- **Synchronous (HTTP/gRPC):** Like a **phone call**. You call, wait for them to
  answer, and you're **blocked** until they respond. If they don't pick up, you're
  stuck waiting.
- **Asynchronous (Message Queue):** Like a **text message**. You send it and go about
  your day. They respond whenever they're ready. You're **not blocked**.

### Synchronous Communication

```
   SYNC (HTTP / gRPC):

   Order Service                    Payment Service
   ┌──────────┐  POST /charge       ┌──────────────┐
   │          │ ──────────────────> │              │
   │ WAITING  │   (blocked)         │ Processing...│
   │ ⏳⏳⏳   │ <────────────────── │              │
   │          │   200 OK            │              │
   └──────────┘                     └──────────────┘
   ↑ Order Service is stuck waiting. If Payment is slow or down, Order is stuck too.
```

| Pros ✅                              | Cons ❌                                    |
|--------------------------------------|--------------------------------------------|
| Simple request/response              | **Caller is blocked** during the call      |
| Immediate feedback                   | Cascading failures if a service is down    |
| Easy to reason about                 | Tight **temporal coupling** between services|

### Asynchronous Communication

```
   ASYNC (Message Queue):

   Order Service          Message Queue          Payment Service
   ┌──────────┐          ┌──────────────┐       ┌──────────────┐
   │          │  send()  │              │       │              │
   │          │ ───────> │ [msg][msg]   │ ────> │              │
   │          │          │      [msg]   │       │ (processes   │
   │  DONE!   │          │              │ <──── │  whenever    │
   │  ✅ free │          │              │       │  ready)      │
   └──────────┘          └──────────────┘       └──────────────┘
   ↑ Order Service sends the message and immediately moves on. No waiting!
```

| Pros ✅                              | Cons ❌                                    |
|--------------------------------------|--------------------------------------------|
| Caller is **not blocked**            | No immediate response (eventual)           |
| Decoupled — services are independent | Harder to debug (no direct call stack)     |
| **Buffering** — queue absorbs spikes | Eventual consistency                       |
| Survives downstream outages          | Message ordering/deduplication complexity  |

### When to Use Which?

| Use Sync when...                         | Use Async when...                        |
|------------------------------------------|------------------------------------------|
| You need an **immediate response**       | The action can happen **later**          |
| The operation is part of a critical path | You want to **decouple** services         |
| Simple request/response semantics        | You need to **absorb traffic spikes**    |
|                                          | Multiple services need the same event    |

---

## 6. Event-Driven Architecture

### Real-World Analogy: A Newspaper Subscription 📰

You don't call the newspaper every morning asking "Is there news today?" Instead,
you **subscribe**, and they **deliver** the paper whenever it's published. Many
people can subscribe to the same newspaper without the publisher knowing or caring.

### What Is Event-Driven Architecture?

Instead of services calling each other directly, services **emit events** ("something
happened") and other services **react** to those events. The emitter doesn't know
(or care) who's listening.

```
   TRADITIONAL (Direct Calls):           EVENT-DRIVEN (Pub/Sub):

   Order ──> Payment                     Order ──> "OrderCreated" ──> [Event Bus]
        ──> Inventory                                  │       │       │
        ──> Notification                       ┌───────┘       │       └───────┐
        ──> Analytics                          ▼               ▼               ▼
                                               Payment      Inventory      Analytics
   Order must know about ALL                   (reacts)      (reacts)       (reacts)
   downstream services. Tight coupling!
                                           Order doesn't know who listens.
                                           Add a new service? Just subscribe!
```

### Pub/Sub Model

```
                      ┌─────────────────────┐
   Publisher ───────> │    EVENT BUS /       │ ───────> Subscriber A (Payment)
   (Order Service)    │    MESSAGE BROKER    │ ───────> Subscriber B (Inventory)
                      │                      │ ───────> Subscriber C (Notification)
                      └─────────────────────┘ ───────> Subscriber D (Analytics)

   Publisher emits: "OrderCreated { orderId: 101, userId: 42, total: $99 }"
   ALL subscribers receive it and react independently.
```

### Benefits of Event-Driven Architecture

- **Loose coupling:** Publisher doesn't know about subscribers
- **Easy to add consumers:** New service? Just subscribe to existing events
- **Scalability:** Event bus absorbs spikes; consumers process at their own pace
- **Resilience:** If a subscriber is down, events can be replayed later

### Challenges

- **Eventual consistency:** Things happen eventually, not immediately
- **Debugging is hard:** No single call chain to trace
- **Event schema evolution:** Changing event structure can break consumers
- **Duplicate processing:** Must handle idempotency (process same event twice safely)

> Popular event buses/brokers: Kafka, AWS EventBridge, RabbitMQ, Google Pub/Sub.

---

## 7. Interview Q&A

### Q: When should you use microservices instead of a monolith?

Start with a monolith. Move to microservices when: teams grow beyond ~8 people,
deployments are blocked by coupling, specific services need independent scaling, or
different parts need different technology stacks. Premature microservices create
distributed-system complexity without clear benefits.

### Q: REST vs GraphQL vs gRPC — when do you use each?

Use **REST** for public-facing APIs (simple, universal, cacheable). Use **GraphQL**
when clients need flexible data fetching (especially mobile apps with complex UIs
that would require multiple REST calls). Use **gRPC** for internal service-to-service
communication where performance matters (binary protocol, HTTP/2, streaming).

### Q: What does an API Gateway do?

It's the single entry point that handles cross-cutting concerns: authentication,
routing, rate limiting, SSL termination, response caching, and protocol translation
(e.g., external REST → internal gRPC). This keeps individual services focused on
business logic.

### Q: How does service discovery work?

Services register themselves in a **service registry** (e.g., Consul, Eureka) with
their current IP and port. Other services query the registry to find them. Services
send **heartbeats**; if heartbeats stop, the registry removes the service. This
handles the dynamic nature of services starting, scaling, and dying.

### Q: Sync vs async communication — how do you decide?

Use **sync** (HTTP/gRPC) when you need an immediate response (e.g., payment
authorization — you need to know if the card was charged before proceeding). Use
**async** (message queues) when the action can happen later (e.g., sending a
confirmation email — the order is already placed, the email can be sent whenever).

### Q: What is event-driven architecture?

Services emit events (e.g., "OrderCreated") to an event bus, and other services
subscribe and react independently. The publisher doesn't know about subscribers,
achieving loose coupling. Benefits: easy to add new consumers, absorbs traffic spikes,
resilient. Challenges: eventual consistency, harder debugging, idempotency.

### Q: What are the tradeoffs of microservices?

**Benefits:** independent scaling, independent deployments, team autonomy, tech
flexibility. **Costs:** distributed system complexity, network failures, harder
debugging, data consistency challenges, operational overhead (monitoring, service
discovery, tracing). The benefits outweigh the costs only at sufficient scale.

### Q: How do you handle a service failure in a microservices architecture?

1. **Retry** with exponential backoff (transient failures)
2. **Circuit breaker** — stop calling a failing service, fail fast
3. **Fallback** — return cached/default data instead of failing
4. **Queue** — for async communication, buffer in a message queue
5. **Graceful degradation** — show partial results rather than full failure

### Q: How do microservices share data?

Ideally, **they don't**. Each service owns its own database (no shared DB). To share
data, services either: call each other via APIs (sync), emit events that others
consume (async), or duplicate necessary data into their own store via event sourcing.
Sharing a single database defeats the purpose of microservices.

---

## Quick Reference Cheat Sheet

```
┌──────────────────────────┬──────────────────────────────────────────────┐
│ Concept                  │ One-liner                                    │
├──────────────────────────┼──────────────────────────────────────────────┤
│ Monolith                 │ Single app, single deploy (start here)       │
│ Microservices            │ Independent services, independent deploys    │
│ REST                     │ HTTP verbs on resources, JSON (public APIs)  │
│ GraphQL                  │ Client specifies exact data needed           │
│ gRPC                     │ Fast binary RPC for internal comms           │
│ API Gateway              │ Single entry point: auth, routing, limits    │
│ Service Discovery        │ Registry of where services live (IPs)        │
│ Sync Communication       │ Direct call, blocked until response          │
│ Async Communication      │ Message queue, fire-and-forget              │
│ Event-Driven             │ Emit events, subscribers react independently │
│ Pub/Sub                  │ One publisher, many independent subscribers  │
└──────────────────────────┴──────────────────────────────────────────────┘
```

---

**Previous:** [02 — Databases & Caching](02-databases-and-caching.md)
**Next:** [04 — Reliability & Monitoring →](04-reliability-and-monitoring.md)
