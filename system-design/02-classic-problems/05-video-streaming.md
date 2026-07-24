# Design a Video Streaming System (YouTube / Netflix)

> **Analogy:** A TV broadcast tower. The show is pre-recorded, encoded into different quality levels, and broadcast through relay towers (CDNs). Each viewer picks up the signal closest to them.

---

## 1. Requirements

### Functional Requirements
- Users can upload videos
- Users can stream videos in various resolutions (240p to 4K)
- Users can search, browse, and see recommendations
- Video player adapts quality based on bandwidth
- Support for live streaming (bonus)

### Non-Functional Requirements
- **Scale:** 1B+ users, 500 hours uploaded/minute, billions of views/day
- **Latency:** < 2s start-up time (time-to-first-frame)
- **Availability:** 99.99% (video must always play)
- **Bandwidth:** Massive egress (video streaming is the most bandwidth-intensive app on the internet)

---

## 2. Estimation

| Metric | Value |
|--------|-------|
| Videos uploaded per minute | 500 hours |
| Avg video size (after encoding) | 500 MB |
| Daily upload storage | 500 hrs × 60 min × 500 MB ≈ 900 TB/day |
| Views per day | 5 billion |
| Avg view duration | 10 minutes |
| Daily egress (bandwidth out) | Massive (estimated petabytes/day) |

**Key insight:** This system is READ-heavy and BANDWIDTH-heavy, not write-heavy.

---

## 3. High-Level Architecture

The system has two distinct halves: **Upload/Processing** and **Streaming/Delivery**.

### Upload & Processing Pipeline

```
┌───────┐   Upload    ┌──────────────┐    Transcode     ┌─────────────┐
│Creator│ ─────────>  │ Upload Service│ ──────────────> │ Transcoder   │
│       │             │ (API Gateway) │                  │ Farm (GPU)   │
└───────┘             └───────┬──────┘                  └──────┬──────┘
                              │                                 │
                              ▼                                 ▼
                      ┌──────────────┐              ┌───────────────────┐
                      │ Raw Video    │              │ Encoded Segments   │
                      │ Storage (S3) │              │ (240p, 480p, 720p, │
                      └──────────────┘              │  1080p, 4K)        │
                                                    └─────────┬─────────┘
                                                              │
                                                              ▼
                                                    ┌───────────────────┐
                                                    │ CDN (Edge Nodes)   │
                                                    │ (worldwide)        │
                                                    └───────────────────┘
```

### Streaming / Delivery

```
┌───────┐    Request video     ┌──────────────┐     Cache hit?    ┌─────────┐
│Viewer │ ──────────────────>  │  CDN Edge    │ ───────────────>  │  Video  │
│       │                      │  (nearest)   │                   │ plays!  │
│       │ <───── Video data ── │              │                   └─────────┘
└───────┘                      └──────┬───────┘
                                      │ Cache miss?
                                      ▼
                               ┌──────────────┐
                               │ Origin (S3)  │
                               │ Storage      │
                               └──────────────┘
```

---

## 4. Video Transcoding — The Core Challenge

When a creator uploads a video, it needs to be processed:

```
Step 1: Upload raw video to S3
    │
Step 2: Trigger transcode job (via message queue)
    │
Step 3: Transcoder creates multiple quality levels:
    ├── 240p  (low quality, tiny file, slow connections)
    ├── 360p
    ├── 480p
    ├── 720p  (HD)
    ├── 1080p (Full HD)
    └── 4K    (Ultra HD, only for premium/TV)
    │
Step 4: Each quality level is split into SEGMENTS (2-10 second chunks)
    │
Step 5: Generate manifest file (playlist) — lists all segments
    │
Step 6: Push all segments to CDN
```

### HLS / DASH Streaming (Adaptive Bitrate)

```
┌───────┐                            ┌─────────┐
│ Player│ <── manifest.m3u8 ──────── │  CDN    │
│       │     (lists qualities)      │         │
│       │                            │         │
│       │ ── "give me 720p chunk 1" ──>        │
│       │ <── video data ────────────         │
│       │                                    │
│ (bandwidth drops)                          │
│       │ ── "give me 480p chunk 2" ──>        │
│       │ <── lower quality data ─────        │
│       │                                    │
│ (bandwidth recovers)                       │
│       │ ── "give me 720p chunk 3" ──>        │
└───────┘                            └─────────┘
```

The player continuously monitors bandwidth. If it drops, it requests lower-quality chunks (no buffering). If it rises, it upgrades. This is called **Adaptive Bitrate Streaming (ABR)**.

---

## 5. Why CDN is Critical

```
WITHOUT CDN:
┌──────┐                      ┌────────────┐
│User in│ ─── 4000 miles ───> │ Origin (US)│  → SLOW (high latency)
│India  │ <── video data ──── │ Server     │  → Bandwidth bottleneck
└──────┘                      └────────────┘

WITH CDN:
┌──────┐         ┌────────────┐
│User in│ ── 50 ──> │ CDN Edge   │  → FAST (cached locally)
│India  │ <── miles│ Node (Mumbai)│  → Reduced origin load
└──────┘         └────────────┘
```

CDN caches video segments at edge locations worldwide. 95%+ of video views are served from CDN cache, never hitting the origin.

### CDN Cache Strategy
- Popular videos: Pre-cached at ALL edge nodes (push proactively)
- Medium popularity: Cached on first request (pull)
- Rare videos: Only at regional hubs, fetched on demand

---

## 6. Database Design

### Metadata Database (Relational — PostgreSQL)

```sql
TABLE videos (
    video_id          UUID PRIMARY KEY,
    creator_id        UUID,
    title             VARCHAR(200),
    description       TEXT,
    upload_status     VARCHAR(20),    -- 'processing', 'ready', 'failed'
    duration_seconds  INT,
    view_count        BIGINT,
    like_count        BIGINT,
    created_at        TIMESTAMP
)

TABLE video_urls (
    video_id          UUID,
    resolution        VARCHAR(10),    -- '240p', '480p', '720p', '1080p', '4K'
    manifest_url      VARCHAR(500),   -- HLS manifest URL on CDN
    PRIMARY KEY (video_id, resolution)
)
```

### Thumbnail Storage
- Auto-generate thumbnails from video frames (at transcode time)
- Store in object storage (S3)
- Serve through CDN

---

## 7. Search & Discovery

```
                    ┌──────────────────┐
User searches ─────>│  Search Service   │
                    │  (Elasticsearch)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ 1. Text search    │
                    │    (title, tags,  │
                    │     description)  │
                    │                   │
                    │ 2. Ranking        │
                    │    (views, recency│
                    │     relevance)    │
                    │                   │
                    │ 3. Personalize    │
                    │    (watch history)│
                    └───────────────────┘
```

---

## 8. Scaling Challenges

### Challenge 1: 500 Hours Uploaded Per Minute

Each upload triggers transcode jobs for 5+ quality levels.

**Solution:** Worker farm with auto-scaling, fed by message queue.
```
[Upload Queue] → Worker 1, Worker 2, ..., Worker N
                   (each uses FFmpeg for transcoding)
                   (auto-scale based on queue depth)
```

### Challenge 2: The "Viral Video" Problem

A new video suddenly gets 10M views in 1 hour.

**Solution:** Multi-tier caching.
```
Tier 1: Edge CDN (closest to user)
Tier 2: Regional CDN hub
Tier 3: Origin (S3)

If a video goes viral, it gets pushed to Tier 1 automatically
by the CDN's predictive caching algorithms.
```

### Challenge 3: Live Streaming

```
Live stream ≠ pre-recorded. Transcoding must happen IN REAL-TIME.

┌────────┐   RTMP stream   ┌───────────────┐   HLS segments   ┌─────┐
│Creator │ ──────────────> │ Ingest Server │ ──────────────> │ CDN │ ──> Viewers
│        │                  │ (transcodes   │                   └─────┘
│        │                  │  in real-time)│
└────────┘                  └───────────────┘

Latency budget: 5-15 seconds end-to-end for live
```

---

## 9. Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Video start-up time | > 3 seconds |
| Rebuffer rate (buffering %) | > 1% of play time |
| Transcode queue depth | > 10,000 pending |
| CDN cache hit ratio | < 90% |
| Upload failure rate | > 0.1% |
| Origin server load | > 80% CPU |

---

## Interview Q&A

**Q: Why not just store the video as one big file and let the user download it?**
A: Two reasons. (1) Progressive download wastes bandwidth — if the user watches 10 seconds and leaves, we downloaded the entire file. (2) Adaptive bitrate requires segmented video — you can't switch quality mid-download with a single file. HLS/DASH solves both by splitting into small chunks.

**Q: How do you handle different devices and network conditions?**
A: Adaptive Bitrate Streaming (ABR). The player monitors available bandwidth and buffer level. On fast WiFi, it fetches 1080p chunks. On slow 3G, it drops to 240p. The switch is seamless — no buffering.

**Q: Why not store videos in a database?**
A: Databases are for structured data with query needs. Video files are binary blobs. Object storage (S3) is designed for this: cheap, durable (11 nines), and integrates with CDN. Store metadata in DB, binary in S3.

**Q: How do you handle DRM (Digital Rights Management)?**
A: Use encrypted HLS (AES-128 or FairPlay/WidePlay). Segments are encrypted. Only authorized players with the decryption key can play them. The key is distributed via a secure license server.

**Q: Estimate the bandwidth cost. Is it sustainable?**
A: At Netflix scale (~250M subscribers, ~3 hours/day each), at 3 Mbps average, that's about 1.2 petabytes/second globally. This is why CDNs are essential — without edge caching, the origin bandwidth cost would be astronomical. Netflix uses its own CDN appliances (Open Connect) placed inside ISPs to minimize transit costs.
