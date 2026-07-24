# System Design: Twitter/X News Feed

> **Analogy:** Newspaper delivery. There are two ways to get the paper to a million subscribers: (1) **Push** — the printing press prints a million copies the moment news is written and delivers them proactively, or (2) **Pull** — each subscriber walks to a library and asks "what's new?" when they open their door. Twitter must decide which (or both) to use — and handle the Oprah-with-50M-followers problem.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Requirements](#2-requirements)
3. [Back-of-Envelope Estimation](#3-back-of-envelope-estimation)
4. [API Design](#4-api-design)
5. [Data Model](#5-data-model)
6. [Core Challenge: Feed Generation](#6-core-challenge-feed-generation)
7. [Pull vs Push vs Hybrid](#7-pull-vs-push-vs-hybrid)
8. [Architecture Diagram](#8-architecture-diagram)
9. [Cache Strategy](#9-cache-strategy)
10. [Bottlenecks & Trade-offs](#10-bottlenecks--trade-offs)
11. [Scaling Considerations](#11-scaling-considerations)
12. [Interview Q&A](#12-interview-qa)

---

## 1. Problem Statement

Design Twitter/X's **home timeline** — the feed of tweets a user sees from the people they follow. The system must handle:
- 300M+ monthly active users.
- Celebrities with 50M+ followers (e.g., Oprah, Obama).
- Sub-second feed load time.
- Near-real-time tweet propagation (a celebrity tweet appears in feeds within seconds).

**Core flow:**
```
Alice tweets "Hello!" → System must place this tweet into the feed of all of Alice's followers.
Bob (follows Alice) opens app → sees "Hello!" near the top of his feed.
```

---

## 2. Requirements

### Functional Requirements
- Users can post tweets (text, images, video).
- Users can follow / unfollow other users.
- Home timeline: see tweets from people you follow, reverse-chronological (or ranked).
- Retweets, replies, likes.
- User profile timeline: all tweets by a single user.

### Non-Functional Requirements
- **Low latency** — timeline load <500ms (p99).
- **High availability** — feed must load even if some subsystems fail.
- **Near real-time** — tweets appear in feeds within ~5 seconds.
- **Scale** — handle celebrity fan-out of 50M+ followers.

### Out of Scope
- Search, trends, notifications, direct messages (separate systems).

---

## 3. Back-of-Envelope Estimation

| Metric | Value |
|--------|-------|
| Monthly Active Users (MAU) | 300 million |
| Daily Active Users (DAU) | ~150 million |
| New tweets / day | 500 million |
| Avg followees per user | 200 |
| Avg followers per user | 200 |
| Celebrity followers | up to 50M+ |
| Timeline reads / day | ~1.5 billion (each DAU opens ~10×) |
| Feed reads QPS | ~17,000/sec (avg), ~50,000/sec (peak) |
| Tweet size | ~500 bytes (text + metadata) |
| Storage / day | 500M × 500B ≈ 250 GB/day |
| Storage / 10 yrs | ~900 TB (tweets only) |

**Key insight:** Feed reads (17K QPS) >> tweet writes (~6K QPS). But writes have a **fan-out multiplier** — each tweet is copied to many feeds.

---

## 4. API Design

### 4.1 Post Tweet
```
POST /api/v1/tweet
Body: { "text": "Hello!", "media": [url1, url2] }
→ 201 { "tweet_id": "t123", "created_at": "..." }
```

### 4.2 Get Home Timeline
```
GET /api/v1/feed/home?cursor=<token>&limit=20
→ 200 { "tweets": [...], "next_cursor": "..." }
```

### 4.3 Get User Timeline
```
GET /api/v1/feed/profile?user_id=42&cursor=<token>&limit=20
```

### 4.4 Follow / Unfollow
```
POST   /api/v1/follow   { "user_id": 42 }
DELETE /api/v1/follow/42
```

---

## 5. Data Model

### 5.1 Tweet Store (sharded by tweet_id)
```sql
CREATE TABLE tweets (
    tweet_id    BIGINT PRIMARY KEY,       -- snowflake ID
    user_id     BIGINT NOT NULL,
    text        VARCHAR(280),
    media_urls  JSONB,
    type        VARCHAR(20),              -- 'tweet', 'retweet', 'reply'
    ref_tweet_id BIGINT,                  -- for retweets/replies
    created_at  TIMESTAMPTZ NOT NULL,
    like_count  INT DEFAULT 0,
    retweet_count INT DEFAULT 0
);
```

### 5.2 User / Follow Graph (social graph store)
```
Table: users
  user_id PK, username, display_name, bio, created_at

Table: follows          -- "follower follows followee"
  follower_id  → followee_id   (composite PK)
```

For the follow graph, a **graph database** (e.g., Neo4j) or a wide-column store (Cassandra) is ideal. At Twitter scale, custom solutions (e.g., Twitter's FlockDB) are used.

### 5.3 Timeline Store (pre-computed feeds)
```
Redis sorted set per user:
  key: feed:user:{user_id}
  value: ZSET of tweet_id → created_at_score
  (keeps last ~1000 tweets per feed)
```

---

## 6. Core Challenge: Feed Generation

This is the heart of the problem. When Alice tweets, her tweet must reach all her followers' feeds. There are two fundamental strategies and a hybrid:

### 6.1 Pull Model (Fanout-on-Read)
> When Bob opens his feed, **query all of Bob's followees**, fetch their recent tweets, merge, sort, and return.

```
Bob opens feed →
  SELECT * FROM tweets WHERE user_id IN (Alice, Carol, Dave, ...)
    AND created_at > last_seen ORDER BY created_at DESC LIMIT 20
```

| Pros | Cons |
|------|------|
| Simple writes (just store the tweet) | **Expensive reads** — query 200 followees each time |
| No celebrity fan-out problem | High read latency |
| Always fresh | Hard to do ranking/personalization across sources |

### 6.2 Push Model (Fanout-on-Write)
> When Alice tweets, **immediately push** the tweet into every follower's pre-computed feed.

```
Alice tweets →
  for each follower of Alice:
      Redis.ZADD(feed:{follower}, now, tweet_id)
```

| Pros | Cons |
|------|------|
| **Cheap reads** — just read the pre-computed feed | **Celebrity problem** — Oprah's 50M followers = 50M writes per tweet |
| Sub-ms read latency | Stale feed if fan-out lags |
| Easy to rank/personalize offline | Write amplification |

### 6.3 The Celebrity Problem
If Oprah (50M followers) tweets, the push model must do **50 million Redis writes**. At 1µs each that's 50 seconds — and if she tweets 10×/day, that's 500M fan-out writes/day from her alone. This is the key bottleneck.

---

## 7. Pull vs Push vs Hybrid

### 7.1 Hybrid Model (What Twitter Actually Uses)
> **Push for normal users, pull for celebrities.**

```
When Alice tweets:
  1. Is Alice a "celebrity" (>100K followers)?
     NO  → Push to all followers' feeds (fanout-on-write)
     YES → Skip push. Her followers will pull her tweets on read.
```

For a user opening their feed:
```
  1. Read pre-computed feed from Redis (covers normal followees)
  2. Pull recent tweets from any celebrities they follow (fanout-on-read)
  3. Merge + sort by recency/rank
```

This caps fan-out cost while keeping read latency low.

### 7.2 Decision Matrix
```
                    │ Pull (read-time)     │ Push (write-time)
  ──────────────────┼──────────────────────┼─────────────────────
  Normal user tweets│   (not used)         │  ✅ Cheap read
  Celebrity tweets  │   ✅ Avoid 50M writes│   (too expensive)
  Read latency      │   Higher             │  ✅ Near-zero
  Write cost        │  ✅ Low              │   Higher (amplified)
```

---

## 8. Architecture Diagram

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                              Client App                               │
  └───────────────┬───────────────────────────────────┬──────────────────┘
            POST tweet                            GET feed
                  │                                   │
                  ▼                                   ▼
           ┌────────────┐                      ┌────────────┐
           │ API Gateway │                     │ API Gateway │
           └──────┬─────┘                      └──────┬─────┘
                  │                                   │
                  ▼                                   ▼
           ┌─────────────────┐               ┌──────────────────┐
           │  Tweet Write     │               │  Timeline Service │
           │  Service         │               │  (Feed Reader)    │
           └──────┬──────────┘               └────────┬─────────┘
                  │                                   │
                  ▼                                   │
           ┌──────────────┐                           │
           │ Fanout       │                           │
           │ Service      │                           │
           └──┬───────┬───┘                           │
              │       │                               │
      normal? │       │ celebrity?                    │
              ▼       ▼                               │
    ┌──────────────┐  ┌──────────────┐                │
    │ Push to      │  │ (skip push,  │                │
    │ Redis feeds  │  │  pull later) │                │
    │ of followers │  └──────────────┘                │
    └──────┬───────┘                                   │
           │                                           │
           ▼                                           ▼
    ┌──────────────────────────────────────────────────────┐
    │                    Redis Cluster                      │
    │    feed:user:{id}  →  ZSET(tweet_id → score)         │
    │    (pre-computed home timelines, ~1000 tweets each)   │
    └──────────────────────────┬───────────────────────────┘
                               │ (cache miss / pull for celebs)
                               ▼
    ┌──────────────────────────────────────────────────────┐
    │              Tweet Store (Sharded DB)                 │
    │   tweets table, sharded by tweet_id, with replicas    │
    └──────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────┐
    │              Follow Graph Service                     │
    │   Cassandra / FlockDB: follower → followee edges      │
    │   Used by Fanout Service to find followers            │
    └──────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────┐
    │              Async / Ranking Pipeline                 │
    │   Tweets → Kafka → ML ranking service                 │
    │   (computes "top tweets" for engagement-ordered feed) │
    └──────────────────────────────────────────────────────┘
```

---

## 9. Cache Strategy

The timeline is the hottest data. Multi-layer caching:

| Layer | Store | Contents | TTL |
|-------|-------|----------|-----|
| L1 | Client app | Last feed fetch | refresh on pull |
| L2 | CDN / edge | API responses for popular feeds | 5s |
| L3 | Redis | Pre-computed feed ZSETs per user | Eviction at ~1000 tweets |
| L4 | Tweet object cache | `tweet_id → full tweet` (memcached) | hours |
| L5 | DB | Source of truth | permanent |

**Feed ZSET structure:**
```
ZADD feed:user:42  1625000005  tweet:555
ZADD feed:user:42  1625000003  tweet:554
ZADD feed:user:42  1625000001  tweet:553
ZRANGE feed:user:42 0 19 REV    ← get top 20 most recent
```

---

## 10. Bottlenecks & Trade-offs

| Bottleneck | Impact | Mitigation |
|------------|--------|------------|
| Celebrity fan-out (50M writes) | Clogs fan-out queue, delays normal tweets | Hybrid model: celebrities skip push |
| Fan-out queue backlog | Tweets delayed to followers | Autoscale fanout workers; separate queues per user tier |
| Hot Redis shard (popular users' feeds read constantly) | Saturated shard | Read replicas; client-side caching |
| Stale pre-computed feeds | Deleted/blocked tweets still appear | Tombstones; lazy invalidation |
| Tweet delete propagation | Must remove from all cached feeds | Async tombstone propagation to feeds |
| "Zombie tweets" from deactivated users | Feed pollution | Filter at read time using user state |

---

## 11. Scaling Considerations

1. **Shard the tweet store** by `tweet_id` (snowflake IDs embed timestamp → time-ordered).
2. **Shard Redis** by `user_id` so a user's feed lives on one node.
3. **Separate fanout queues** by priority: celebrity tweets on a dedicated (slower) queue so they don't block normal users.
4. **Pre-compute "ready" feeds** for active users during off-peak (warm the cache).
5. **Eventual consistency for edge cases**: if a user follows a new person, their old tweets don't retroactively appear — fetch on demand and backfill.

---

## 12. Interview Q&A

**Q: Walk me through what happens when Oprah tweets.**
A: The Fanout Service detects she's a celebrity (>100K followers). Instead of pushing to 50M feeds, it **skips the push** and only stores the tweet in the Tweet Store. When any of her followers opens their feed, the Timeline Service **pulls** her recent tweets on-demand and merges them with their pre-computed feed. This avoids 50M write operations.

**Q: What's the trade-off between pull and push?**
A: **Push** optimizes reads (pre-computed, instant) but amplifies writes (especially for celebrities). **Pull** optimizes writes (just store once) but makes reads expensive (query all followees). The hybrid uses push for normal users and pull for celebrities, getting the best of both.

**Q: How do you handle the "user just followed someone new" case?**
A: In a pure push model, the new followee's past tweets don't appear (they were pushed before the follow). Options: (a) **pull their last N tweets** on follow and backfill the feed, (b) accept that only future tweets appear. Twitter does a hybrid — backfills recent tweets on follow.

**Q: How do you delete a tweet from all feeds?**
A: You can't efficiently scan millions of feeds. Instead: (1) store the tweet as **deleted** (tombstone) in the Tweet Store, (2) when reading the feed, **filter out** tombstoned tweet IDs at read time. Eventually a background job compacts feeds to remove them.

**Q: How do you rank tweets (not reverse-chronological)?**
A: Use a separate **ranking pipeline**: tweet events → Kafka → ML model scores each tweet per user based on engagement signals (affinity, recency, popularity). Overwrite the Redis ZSET score with the rank score instead of timestamp.

**Q: What if the fan-out service goes down?**
A: Tweets queue up in Kafka. Once the service recovers, it drains the queue. Users may see slightly stale feeds (no new tweets) but the system doesn't lose data. **Reads still work** from the last-known-good feed.

**Q: How do you handle retweets and replies in the feed?**
A: Store them as tweets with a `type` and `ref_tweet_id`. The fan-out logic is identical — push the retweet/reply to followers. At read time, the client hydrates the referenced tweet (or embeds it if the retweet has no added text).

**Q: How would you design the user profile timeline (all tweets by one user)?**
A: This is simpler — just `SELECT * FROM tweets WHERE user_id = ? ORDER BY created_at DESC`. No fan-out needed. Cache the top 20 in Redis per user.

**Q: Why Snowflake IDs?**
A: Snowflake IDs encode `(timestamp, worker_id, sequence)` → globally unique, time-ordered, and generated without a central DB auto-increment. Time-ordering lets us sort feeds by ID alone.

**Q: How do you keep feed reads fast when a user follows 5,000 people?**
A: The pre-computed feed ZSET already merges all 5,000 sources — reading is O(20) regardless of follow count. The cost moves to write-time fan-out (5,000 people push to this user's feed). If that's too much, cap feed length and evict old tweets.

---

## Summary

The Twitter news feed is fundamentally about the **push-pull trade-off**. The winning production strategy is a **hybrid**: fan-out-on-write for normal users (cheap reads) and fan-out-on-read for celebrities (avoids millions of writes per celebrity tweet). The system is backed by **pre-computed feed caches in Redis**, a **sharded tweet store**, and a **follow graph service**. Ranking, retweets, and deletes are layered on top as read-time concerns.
