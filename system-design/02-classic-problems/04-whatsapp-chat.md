# Design a Real-Time Chat System (WhatsApp / Messenger)

> **Analogy:** Think of a walkie-talkie (real-time push) combined with voicemail (store messages when recipient is offline).

---

## 1. Requirements

### Functional Requirements
- Users can send/receive text messages in 1-on-1 chats
- Users can create group chats (up to 100 members)
- Messages must be delivered in order
- System shows online/offline status (presence)
- Read receipts (blue ticks ✓✓)
- Message history (last 90 days)

### Non-Functional Requirements
- **Latency:** < 200ms for message delivery
- **Availability:** 99.9% uptime
- **Scale:** 500M DAU, 50B messages/day
- **Consistency:** Messages must be ordered per conversation

---

## 2. Back-of-Envelope Estimation

| Metric | Value |
|--------|-------|
| Daily Active Users | 500M |
| Messages per day | 50B |
| Messages per second (avg) | ~580K |
| Messages per second (peak) | ~1.5M |
| Message size (avg) | 200 bytes (text only) |
| Storage per day | 50B × 200B = 10 TB/day |
| Storage for 90 days | 900 TB |
| Connection (concurrent) | 50M (10% of DAU online at any time) |

---

## 3. High-Level Architecture

```
┌────────┐      ┌──────────────┐      ┌──────────────────┐
│ Mobile │ <──> │  WebSocket   │ <──> │  Chat Service    │
│  App   │      │  Gateway     │      │  (stateless)     │
└────────┘      │  (500 conn/  │      └────────┬─────────┘
                │   instance)  │               │
                └──────────────┘               │
                           ↑                   ↓
                    ┌──────┴───────┐   ┌───────┴────────┐
                    │  Presence    │   │ Message Store  │
                    │  Service     │   │ (Cassandra)    │
                    │  (Redis)     │   └────────────────┘
                    └──────────────┘
```

### Why WebSockets?

```
HTTP Polling: Client asks "any new messages?" every 2 seconds
              → Wastes battery + bandwidth (most polls return nothing)

WebSocket: Persistent connection. Server pushes instantly when message arrives
           → Real-time, low latency, low battery
```

---

## 4. Message Flow — Step by Step

### Sender → Server → Recipient

```
User A types "Hello" and presses send
    │
    ▼
┌──────────┐    WebSocket     ┌───────────────┐
│  App A   │ ──────────────>  │ Chat Service  │
└──────────┘                  └───────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
             ┌──────────┐    ┌──────────┐    ┌──────────────┐
             │ Assign   │    │ Store in │    │ Check if     │
             │ Message  │    │ DB with  │    │ User B is    │
             │ ID +     │    │ timestamp│    │ online       │
             │ sequence │    │          │    │              │
             └──────────┘    └──────────┘    └──────┬───────┘
                                                    │
                                           ┌────────┴────────┐
                                           │                 │
                                        ONLINE            OFFLINE
                                           │                 │
                                           ▼                 ▼
                                    Push via WS       Store as unread
                                    to User B         Deliver on reconnect
```

### Sequence Numbering (Message Ordering)

Each conversation has a monotonically increasing sequence number:
```
Conversation 123:
  msg_id: 1, seq: 1, "Hello"      ← first message
  msg_id: 2, seq: 2, "How are you?"
  msg_id: 3, seq: 3, "Good, you?"
```

Client ACKs each sequence number. If seq 2 is missing, client requests retransmit.

---

## 5. Database Schema

### Message Table (Cassandra — wide-column store)

```
TABLE messages (
    conversation_id   UUID,      ← Partition key
    message_id        TIMEUUID,  ← Clustering key (time-ordered)
    sender_id         UUID,
    content           TEXT,
    status            TEXT,       ← sent/delivered/read
    created_at        TIMESTAMP,
    PRIMARY KEY (conversation_id, message_id)
)
```

**Why Cassandra?**
- Writes optimized (messages are write-heavy)
- Linear scalability
- Partitioned by conversation_id → all messages in a chat on same node

### Conversation Table

```
TABLE conversations (
    conversation_id   UUID,
    type              TEXT,       ← 'direct' or 'group'
    participants      SET<UUID>,
    last_message_at   TIMESTAMP,
    PRIMARY KEY (conversation_id)
)
```

---

## 6. Presence (Online/Offline Status)

```
┌────────┐    Heartbeat every 30s    ┌─────────────────┐
│  App   │ ────────────────────────> │ Presence Service│
│ (User  │                           │ (Redis)         │
│  A)    │                           │                 │
└────────┘                           │ key: user_A     │
                                     │ val: "online"   │
                                     │ TTL: 35s        │
                                     └─────────────────┘
```

- User sends heartbeat every 30 seconds
- Redis stores `user_id → "online"` with TTL of 35 seconds
- If heartbeat stops, key expires → user goes "offline"
- Friends query presence service to see User A's status

---

## 7. Group Chats

Challenge: Message to a group of 100 must reach all 100 members.

```
Sender sends to Group Chat
    │
    ▼
Chat Service stores message ONCE (not 100 copies)
    │
    ▼
Fanout Service: writes a notification entry to each member's inbox
    │
    ▼
Each member's app pulls from their inbox (or gets WS push)
```

**Optimization:** Don't push to offline members. They'll fetch on reconnect.

---

## 8. Read Receipts (Blue Ticks)

```
User B opens and reads the message
    │
    ▼
App B sends: { conversation_id, last_read_seq: 5 }
    │
    ▼
Chat Service updates message status to "read"
    │
    ▼
Notify User A: "User B read your messages up to seq 5"
```

---

## 9. Scaling Considerations

| Component | Scale Strategy |
|-----------|---------------|
| WebSocket Gateways | Horizontal scaling behind load balancer. 50K-500K connections per gateway. |
| Chat Service | Stateless → auto-scale behind LB |
| Message DB (Cassandra) | Partition by conversation_id. Add nodes for more capacity. |
| Presence (Redis) | Redis cluster, shard by user_id |
| Offline push (notifications) | Use FCM (Android) / APNs (iOS) for push notifications |

### Connection Management at Scale

50M concurrent connections is the hard part:
- Each WS connection uses ~50-100KB of memory
- 50M connections × 100KB = 5 TB of RAM total
- Spread across many WebSocket gateway instances
- Use epoll/kqueue (efficient I/O multiplexing) — one thread handles thousands of connections

---

## 10. Bottlenecks & Solutions

| Bottleneck | Solution |
|-----------|----------|
| Single WebSocket gateway crash | Multiple gateways + load balancer. Client reconnects to another. |
| Database write throughput | Cassandra with proper partitioning. Batch writes. |
| Celebrity group chat (10K members) | Separate handling: don't fanout immediately. Use pull model for large groups. |
| Global presence (500M keys) | Shard Redis. Only track "interesting" presences (friends, not all users). |

---

## Interview Q&A

**Q: WebSocket vs Server-Sent Events (SSE) vs Long Polling?**
A: WebSocket is bidirectional (both send and receive). SSE is one-way (server→client only). Long polling is the oldest hack — client polls, server holds the response open. For chat, WebSocket is ideal because we need both directions.

**Q: How do you handle message ordering across a distributed system?**
A: Use sequence numbers per conversation. The server assigns sequence numbers. If the client detects a gap, it requests the missing messages. This is called "gap detection and retransmission."

**Q: What if the user is offline? How do they get their messages?**
A: Messages are stored in the DB. When the user reconnects, they fetch all messages since their last sequence number. Additionally, we can send a push notification (FCM/APNs) to alert them.

**Q: How do you handle the "last message seen" timestamp?**
A: Store the last-read sequence number per user per conversation. When a user opens a chat, update this number. The difference between total messages and last-read = unread count.

**Q: How much storage do you need for media (photos, videos)?**
A: Object storage (S3). Store metadata in DB, binary in S3. Pre-generate thumbnails. Use CDN for downloads. Add a presigned URL with expiry for uploads.
