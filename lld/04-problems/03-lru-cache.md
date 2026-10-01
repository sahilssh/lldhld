# 🗄️ Low-Level Design: LRU Cache (Least Recently Used)

The LRU Cache is one of the most frequently asked data structure / machine coding questions. It must support `get(key)` and `put(key, value)` in **$O(1)$ time complexity**.

---

## 🏗️ Architecture: Hash Map + Doubly Linked List

* **Hash Map**: Provides $O(1)$ lookup from key $\rightarrow$ node pointer.
* **Doubly Linked List**: Provides $O(1)$ removal and insertion of nodes at both ends.
  - **Head**: Most Recently Used (MRU).
  - **Tail**: Least Recently Used (LRU) $\rightarrow$ evicted when capacity is exceeded.
* **Sentinel (Dummy) Head & Tail**: Eliminates edge cases (null checks for head/tail updates).

```mermaid
flowchart LR
    Head["Head (Dummy)"] <--> MRU["Node 3 (MRU)"] <--> Mid["Node 1"] <--> LRU["Node 2 (LRU)"] <--> Tail["Tail (Dummy)"]
```

---

## 💻 Full Implementation (Python)

```python
class Node:
    __slots__ = ('key', 'val', 'prev', 'next')
    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[int, Node] = {}
        
        # Sentinel dummy nodes
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Unlink node from doubly linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_front(self, node: Node) -> None:
        """Insert node right after dummy head (mark as MRU)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        # Move node to front because it was recently accessed
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._add_to_front(node)
            return

        # New key: check capacity
        if len(self.cache) >= self.capacity:
            # Evict LRU node (node right before tail)
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]

        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_front(new_node)

# --- Verification ---
if __name__ == "__main__":
    lru = LRUCache(2)
    lru.put(1, 100)
    lru.put(2, 200)
    print("Get 1:", lru.get(1))      # Returns 100 (1 is now MRU)
    lru.put(3, 300)                  # Evicts key 2
    print("Get 2:", lru.get(2))      # Returns -1 (not found)
    print("Get 3:", lru.get(3))      # Returns 300
```
