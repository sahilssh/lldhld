# 💬 High-Level Design: Distributed Real-Time Chat System (WhatsApp / Slack)

A real-time messaging platform supporting 1-on-1 chats, group channels, online presence, and offline push notifications at massive scale.

---

## 1. System Requirements

### Functional Requirements
1. **1-on-1 Real-Time Messaging**: Low-latency delivery between two active users.
2. **Group Chats**: Up to 1,000 members per group.
3. **Online Presence**: Real-time display of user online / offline status.
4. **Message History & Sync**: Multi-device synchronization and historical message retrieval.
5. **Offline Delivery**: Push notifications when recipients are disconnected.

### Non-Functional Requirements
* **Low Latency**: P99 message transmission $< 100\text{ms}$.
* **High Availability**: 99.99% uptime.
* **Message Delivery Guarantee**: At-least-once delivery with client-side deduplication.

---

## 2. End-to-End System Architecture

```mermaid
flowchart TD
    ClientA([User A])
    ClientB([User B])
    WS_Gateway[WebSocket Gateway Cluster]
    RedisSession[(Redis Session Store)]
    ChatService[Chat Microservice]
    Kafka[[Kafka Message Broker]]
    Cassandra[(Cassandra Message Store)]
    Presence[Presence Service]
    PushService[Push Notification Worker (FCM/APNs)]

    ClientA <-->|WebSocket Stream| WS_Gateway
    ClientB <-->|WebSocket Stream| WS_Gateway

    WS_Gateway <--> RedisSession
    WS_Gateway --> ChatService
    ChatService --> Kafka
    Kafka --> Cassandra
    Kafka --> PushService

    ClientA -.->|Heartbeat Ping| Presence
    Presence <--> RedisSession
```

---

## 3. Real-Time Connection & Message Routing

1. **Persistent Connection**: Clients maintain an open, stateful **WebSocket** connection with a `WebSocket Gateway` node.
2. **Session Registry (Redis)**:
   - When User A connects to `WS-Node-4`, write:
     `SET user_session:user_A "WS-Node-4" EX 300`
3. **Routing Message from User A to User B**:
   - User A sends payload over WebSocket to `WS-Node-4`.
   - `WS-Node-4` queries Redis for User B's current gateway node.
   - If User B is connected to `WS-Node-9`, forward the message via internal gRPC or Redis Pub/Sub to `WS-Node-9`, which pushes it down to User B.
   - If User B has no active session, enqueue the event to the **Push Notification Service (FCM/APNs)**.

---

## 4. Message Storage Schema (Cassandra / ScyllaDB)

Wide-column stores excel at write-heavy append-only chat history with sequential reads:

```sql
CREATE TABLE channel_messages (
    channel_id UUID,
    message_id TIMEUUID,
    sender_id UUID,
    content TEXT,
    created_at TIMESTAMP,
    PRIMARY KEY (channel_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```

* **Partition Key (`channel_id`)**: Distributes distinct chat rooms or 1-on-1 pairs evenly across nodes.
* **Clustering Column (`message_id` as TIMEUUID)**: Automatically orders messages chronologically, enabling efficient pagination:
  ```sql
  SELECT * FROM channel_messages 
  WHERE channel_id = ? AND message_id < ? 
  LIMIT 50;
  ```

---

## 5. User Presence Service (Online / Offline Status)

* To avoid flooding servers with disconnection events upon momentary WiFi drops, clients send periodic **heartbeat pings** every 5 seconds.
* The Presence Service updates Redis:
  `SET presence:user_A "online" EX 15`
* If no heartbeat arrives within 15 seconds, the key expires, transitioning the user to "offline".
