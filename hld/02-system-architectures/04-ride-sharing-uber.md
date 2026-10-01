# 🚕 High-Level Design: Ride-Sharing Service (Uber / Lyft)

A high-scale distributed system for real-time geospatial location tracking, supply-demand matching, dynamic pricing, and trip management.

---

## 1. System Requirements & Scale

### Functional Requirements
1. **Driver Tracking**: Active drivers stream GPS coordinates every 3-5 seconds.
2. **Nearby Supply**: Riders can view real-time cars around their current location.
3. **Ride Matching**: Match a rider requesting a trip with the optimal nearby driver.
4. **Trip Lifecycle**: Complete state transitions from request to destination drop-off.

### Non-Functional Requirements
* **Low Latency**: Location updates processed in $< 500\text{ms}$.
* **Consistency**: Guaranteed single-driver booking (no double-dispatch).

---

## 2. Geospatial Indexing Comparison

| Technology | Geometry | Pros | Cons |
|---|---|---|---|
| **PostGIS (R-Tree)** | Bounding Boxes | Standard SQL, rich geospatial operations | Hard to scale for millions of real-time coordinate updates/sec |
| **Geohash** | Rectangular Bounding | Base32 encoded strings, easy prefix search | Irregular neighbor distances at boundary seams |
| **Google S2** | QuadTree on Sphere ($30$ levels) | Excellent geometric accuracy, fast 64-bit integer cell IDs | Complex math for non-standard polygons |
| **Uber H3** | **Hexagonal Hierarchical Grid** | **Equal distance to all 6 neighbors**, invariant smoothing | Standard production choice for ride-hailing |

---

## 3. High-Level Architecture

```mermaid
flowchart TD
    Driver([Active Drivers])
    Rider([Riders])
    LB[Load Balancer]
    LocService[Location Ingestion Service]
    RedisGeo[(Redis In-Memory Spatial / H3 Index)]
    MatchEngine[Trip Dispatch & Matching Engine]
    TripDB[(PostgreSQL Trip DB)]
    Kafka[[Kafka Event Stream]]

    Driver -->|GPS Ping (3s)| LB
    LB --> LocService
    LocService --> RedisGeo
    LocService --> Kafka

    Rider -->|Request Ride| MatchEngine
    MatchEngine -->|Find Nearest Hexagon Cells| RedisGeo
    MatchEngine -->|Create Trip (Pending)| TripDB
    MatchEngine -.->|Dispatch Ride Offer| Driver
```

---

## 4. Ride Dispatch & Concurrency Control

To prevent two riders from booking the same driver at the same millisecond:

```python
def dispatch_driver_to_ride(redis_client, driver_id: str, ride_id: str) -> bool:
    """
    Atomic lease lock using Redis:
    Locks the driver for a 15-second response window.
    """
    lock_key = f"driver_lock:{driver_id}"
    # SET NX PX acquires lock only if key does not exist, expiring after 15,000 ms
    acquired = redis_client.set(lock_key, ride_id, nx=True, px=15000)
    return bool(acquired)
```

If the assigned driver declines or the 15-second timer expires without acceptance, the match engine releases the lock and cascades the offer to the second closest driver in the neighboring H3 hexagon cells.
