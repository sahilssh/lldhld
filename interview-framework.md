# 🎯 System Design & Object-Oriented Design Interview Framework

A structured, battle-tested playbook for cracking **Low-Level Design (LLD / Machine Coding)** and **High-Level Design (HLD / Distributed Systems)** interviews at top tech companies (Google, Meta, Amazon, Uber, Microsoft, Stripe).

---

## ⏱️ 45-Minute Interview Blueprint

```
+---------------------------------------------------------------------------------+
|                                 LLD (45 Mins)                                   |
+-------------------+--------------------+--------------------+-------------------+
| 00-05 min: Scope  | 05-15 min: Model   | 15-35 min: Code    | 35-45 min: Edge   |
| Requirements &    | Class Diagram &    | Clean Code &       | Cases, Concurrency|
| Constraints       | Design Patterns    | Extensibility      | & Refactoring     |
+-------------------+--------------------+--------------------+-------------------+

+---------------------------------------------------------------------------------+
|                                 HLD (45 Mins)                                   |
+-------------------+--------------------+--------------------+-------------------+
| 00-05 min: Scope  | 05-12 min: Math &  | 12-30 min: Core    | 30-45 min: Deep   |
| Requirements &    | Scale, API Design, | Diagram, Storage,  | Dive, Bottlenecks,|
| Trade-offs        | DB Schemas         | Data Flow          | Failures & HA     |
+-------------------+--------------------+--------------------+-------------------+
```

---

## 📐 Part 1: LLD / Machine Coding Framework

### Step 1: Clarify Scope & Functional Requirements (0 - 5 min)
* Never jump straight to coding. Clarify rules, boundaries, and what is out of scope.
* Identify the primary actors (e.g., Customer, Admin, System, Worker).
* Formulate 3-5 core user actions / use cases.

### Step 2: Define Core Entities & Relationships (5 - 15 min)
* Identify nouns in the requirements $\rightarrow$ these become your Classes/Entities.
* Identify verbs in the requirements $\rightarrow$ these become Methods/Behaviors.
* Choose appropriate design patterns:
  - Creational (Factory, Builder, Singleton)
  - Structural (Adapter, Decorator, Facade)
  - Behavioral (Strategy, Observer, State, Command)
* Sketch a quick class diagram (Mermaid / Whiteboard).

### Step 3: Implement Clean, Modular Code (15 - 35 min)
* Apply **SOLID** principles:
  - **S**: Single Responsibility Principle
  - **O**: Open/Closed Principle (use Strategy/Polymorphism instead of large `if/else` or `switch`)
  - **L**: Liskov Substitution Principle
  - **I**: Interface Segregation Principle
  - **D**: Dependency Inversion Principle (inject interfaces, not concrete classes)
* Separate concerns:
  1. Models / Entities
  2. Service / Orchestrator / Controller layer
  3. Repositories / In-memory Stores
  4. Strategy / Factory implementations

### Step 4: Concurrency, Edge Cases & Verification (35 - 45 min)
* Identify shared mutable state:
  - Protect critical sections using mutexes / locks / read-write locks / atomic primitives.
  - Guard against race conditions (e.g., double booking, concurrent payments).
* Walk through an end-to-end dry run with a simple `main()` driver script.

---

## 🌐 Part 2: HLD / System Design Framework

### Step 1: Requirements Clarification (0 - 5 min)
* **Functional Requirements (FR)**:
  - What does the user do? (e.g., Shorten URL, redirect, view analytics).
  - List 3-4 primary user stories.
* **Non-Functional Requirements (NFR)**:
  - Latency targets (e.g., P99 < 50ms for reads, < 200ms for writes).
  - Availability (e.g., 99.99% "four nines" $\approx$ 52 minutes downtime/year).
  - Consistency model (Strong vs Eventual).
  - Scale expectations (Daily Active Users, read/write ratio).

### Step 2: Back-of-the-Envelope Calculations (5 - 12 min)
* **Traffic (QPS)**:
  $$\text{Daily Requests} = \text{DAU} \times \text{Requests per user}$$
  $$\text{Average QPS} = \frac{\text{Daily Requests}}{86,400} \approx \frac{\text{Daily Requests}}{10^5}$$
  $$\text{Peak QPS} = \text{Average QPS} \times 2 \text{ to } 5$$
* **Storage**:
  $$\text{Storage/Day} = \text{Writes/Day} \times \text{Size per record}$$
  $$\text{Storage over 5 Years} = \text{Storage/Day} \times 365 \times 5$$
* **Bandwidth / Memory (RAM)**:
  - 80/20 Rule: 20% of content generates 80% of read traffic. Cache top 20% daily read volume in Redis/Memcached.

### Step 3: API Design & Data Models (12 - 20 min)
* Write explicit RESTful or gRPC endpoints:
  - `POST /v1/urls` $\rightarrow$ `{ "longUrl": string }`
  - `GET /{shortCode}` $\rightarrow$ HTTP 301 / 302 Redirect
* Draft high-level database schema:
  - Primary keys, foreign keys, secondary indexes.
  - SQL (Relational, ACID, Complex joins) vs NoSQL (Key-Value, Document, Wide-Column, Graph).

### Step 4: High-Level Architecture & End-to-End Flow (20 - 32 min)
* Draw the client-to-storage data flow:
  1. DNS $\rightarrow$ CDN (Cloudflare/CloudFront)
  2. Load Balancer (Nginx / ALB with Consistent Hashing or Round Robin)
  3. API Gateway (Rate Limiting, Auth, TLS termination)
  4. Microservices / Stateless Application Servers
  5. Caching Layer (Redis Cluster / Memcached)
  6. Persistence Layer (Master-Replica DB, Sharded clusters)
  7. Async Processing (Kafka / RabbitMQ + Workers)

### Step 5: Deep Dives, Bottlenecks & Resilience (32 - 45 min)
* Address failure modes:
  - What happens if the primary database dies? (Automated failover, replica promotion).
  - What happens if Redis crashes? (Cache stampede mitigation, circuit breakers).
  - Network partitions? (CAP theorem trade-offs).
* Data Partitioning / Sharding strategy (Hash-based vs Range-based, Consistent Hashing).
* Observability: Distributed tracing (OpenTelemetry/Jaeger), Metrics (Prometheus), Logs (ELK).

---

## 🧮 Numbers Every System Designer Must Know

### Latency Numbers (Jeff Dean Cheat Sheet)

| Operation | Latency (approx) | Real-world Equivalent |
|---|---|---|
| L1 Cache reference | 0.5 - 1 ns | 1 Heartbeat |
| Branch mispredict | 3 - 5 ns | |
| L2 Cache reference | 7 ns | |
| Mutex Lock / Unlock | 25 ns | |
| Main Memory (RAM) reference | 100 ns | |
| Read 1 MB sequentially from memory | 3,000 ns (3 µs) | |
| SSD Random Read | 16,000 ns (16 µs) | |
| Read 1 MB sequentially from SSD | 50,000 ns (50 µs) | |
| Datacenter Round-Trip (RTT) | 500,000 ns (500 µs) | Half a millisecond |
| HDD Random Seek | 10,000,000 ns (10 ms) | 20x slower than SSD |
| Read 1 MB sequentially from HDD | 20,000,000 ns (20 ms) | |
| Cross-continent RTT (CA $\rightarrow$ NL) | 150,000,000 ns (150 ms) | Easily noticeable |

### Storage & Data Sizing Multipliers

| Unit | Decimal (SI) | Binary (IEC) | Approximate Bits / Bytes |
|---|---|---|---|
| **1 KB / KiB** | $10^3$ bytes | $2^{10} = 1,024$ bytes | $\approx 1$ thousand bytes |
| **1 MB / MiB** | $10^6$ bytes | $2^{20} \approx 1.05 \times 10^6$ bytes | $\approx 1$ million bytes |
| **1 GB / GiB** | $10^9$ bytes | $2^{30} \approx 1.07 \times 10^9$ bytes | $\approx 1$ billion bytes |
| **1 TB / TiB** | $10^{12}$ bytes | $2^{40} \approx 1.1 \times 10^{12}$ bytes | $\approx 1$ trillion bytes |
| **1 PB / PiB** | $10^{15}$ bytes | $2^{50} \approx 1.13 \times 10^{15}$ bytes | $\approx 1$ quadrillion bytes |

---

## 🚫 Common Interview Anti-Patterns

1. **Jumping straight to architecture without requirements**: Spending 20 minutes designing Kafka pipelines when the system only handles 5 requests per second.
2. **Ignoring the Read/Write Ratio**: A 100:1 read-heavy system requires heavy caching and replica scaling, while a 1:1 write-heavy system needs append-only logs and LSM-tree storage (Cassandra/Scylla).
3. **Keyword Bingo**: Mentioning Kubernetes, GraphQL, Kafka, and Redis without explaining *why* they solve the specific bottleneck.
4. **Neglecting Data Consistency**: Claiming a financial transaction system uses "eventual consistency" without explaining how double spending or balances are reconciled.
5. **No Single Point of Failure (SPOF) Analysis**: Failing to review if a single database node, load balancer, or cache server can bring down the entire system.
