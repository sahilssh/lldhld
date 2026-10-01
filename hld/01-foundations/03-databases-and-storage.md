# 💾 Databases, Storage Engines & Distributed Data

Choosing the right database architecture is often the make-or-break decision in High-Level System Design.

---

## 1. Relational (SQL) vs. NoSQL

| Category | Typical Technologies | Data Model | Strengths | Weaknesses | Best Use Cases |
|---|---|---|---|---|---|
| **RDBMS (SQL)** | PostgreSQL, MySQL, CockroachDB | Tabular, Normalized, Foreign Keys | Strict ACID transactions, complex JOINs, structured schema | Difficult to scale writes horizontally beyond single machine | Financial ledgers, user accounts, orders, inventory |
| **Key-Value** | Redis, DynamoDB, Memcached | Key $\rightarrow$ Opaque blob/string | Sub-millisecond latency, massive scale, simple query pattern | No complex querying, indexing, or cross-key joins | User sessions, shopping carts, rate limiting |
| **Document** | MongoDB, Couchbase | JSON / BSON hierarchies | Flexible schema, fast reads for nested documents | Eventual consistency, higher storage overhead | CMS, user profiles, product catalogs |
| **Wide-Column** | Cassandra, ScyllaDB, HBase | Partition Key + Clustering Columns | Linearly scalable writes, append-optimized, no SPOF | Limited query flexibility (must design schema around queries) | Time-series metrics, chat history, IoT sensor logs |
| **Graph** | Neo4j, Amazon Neptune | Nodes, Edges, Properties | Ultra-fast traversal of deep relationships ($O(1)$ pointer hops) | Hard to partition horizontally across multiple servers | Social networks, fraud detection graphs, recommendation engines |

---

## 2. CAP Theorem vs. PACELC Theorem

### CAP Theorem
In a distributed data store experiencing a **Network Partition ($P$)**, you can choose either:
* **Consistency ($C$)**: Every read receives the most recent write or errors out (e.g., CP systems: HBase, Zookeeper, Etcd).
* **Availability ($A$)**: Every non-failing node returns a response, but it may contain stale data (e.g., AP systems: Cassandra, DynamoDB, CouchDB).

### PACELC Theorem (Extends CAP)
If there is a **Partition ($P$)**, trade off **Availability ($A$)** vs **Consistency ($C$)**; **Else ($E$)**, trade off **Latency ($L$)** vs **Consistency ($C$)**.

* **PC/EC**: Sybase, Bigtable (Consistency prioritized both during normal operations and during network partitions).
* **PA/EL**: Dynamo, Cassandra (Availability during partitions, low Latency during normal operations).

---

## 3. Storage Engines: B+ Tree vs. LSM Tree

```
+--------------------------------------------------------------------------------+
| B+ Tree (Read-Optimized)           | LSM Tree (Write-Optimized)                |
| Used by: Postgres, MySQL (InnoDB)  | Used by: Cassandra, RocksDB, LevelDB     |
+------------------------------------+-------------------------------------------+
| • In-place updates on fixed pages  | • Writes go to in-memory Memtable + WAL   |
| • Fast random reads: O(log N)      | • Flushed to disk as immutable SSTables   |
| • Higher write amplification       | • Background Compaction merges sorted runs|
| • Heavy random disk seeks          | • Ultra-fast sequential writes            |
+--------------------------------------------------------------------------------+
```

---

## 4. Database Sharding & Partitioning

When data exceeds the capacity of a single physical server, horizontal partitioning (sharding) divides the database into distinct subsets.

### Sharding Strategies:
1. **Range-Based Sharding**:
   - Shard by ranges (e.g., Users A-G $\rightarrow$ Shard 1, H-N $\rightarrow$ Shard 2).
   - *Risk*: Hotspots (e.g., massive activity on surnames starting with 'S').
2. **Hash-Based Sharding**:
   - $\text{Shard ID} = \text{Hash}(\text{Key}) \pmod N$
   - Distributes keys evenly across shards.
   - *Drawback*: Resharding when adding nodes requires moving almost all keys unless using **Consistent Hashing**.
3. **Directory-Based Sharding**:
   - A centralized lookup service maps keys to their designated database nodes.

---

## 5. Replication & Leaderless Quorums

To ensure strong consistency in leaderless systems (e.g., DynamoDB, Cassandra), quorum configurations must satisfy:

$$R + W > N$$

Where:
* $N$ = Total number of replicas storing the partition.
* $W$ = Number of replicas that must acknowledge a write before success.
* $R$ = Number of replicas that must be queried during a read.

If $R + W > N$, the read quorum and write quorum are guaranteed to overlap on at least one replica holding the latest version.
