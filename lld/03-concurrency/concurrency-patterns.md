# ⚡ Concurrency & Multi-Threading Patterns

Concurrency is critical in Low-Level Design interviews. Writing thread-safe object models requires understanding shared state, synchronization primitives, race conditions, and deadlock prevention.

---

## 🔒 1. Synchronization Primitives Cheat Sheet

| Primitive | Purpose | Use Case |
|---|---|---|
| **Mutex / Lock** | Mutual exclusion: only one thread executes the critical section at a time. | Modifying shared counters, state transitions, balance updates. |
| **RLock (Reentrant Lock)** | Allows the thread holding the lock to acquire it again without blocking. | Recursive function calls or nested methods accessing locked state. |
| **Semaphore** | Controls access to a shared resource with a finite capacity $N$. | Database connection pool, limiting concurrent outbound API calls. |
| **Read-Write Lock (RWLock)** | Multiple concurrent readers OR one exclusive writer. | Read-heavy caches, routing tables, configuration trees. |
| **Condition Variable** | Allows threads to wait until a specific boolean condition becomes true. | Producer-Consumer bounded buffers, task queues. |

---

## 🏭 2. Thread-Safe Producer-Consumer (Bounded Buffer)

Implemented using `threading.Condition` to eliminate busy-waiting:

```python
import threading
import time
from collections import deque

class BoundedBlockingQueue:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = deque()
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)

    def enqueue(self, item: any) -> None:
        with self.not_full:
            while len(self.queue) >= self.capacity:
                # Buffer is full, wait until a consumer removes an item
                self.not_full.wait()
            
            self.queue.append(item)
            # Notify waiting consumers that an item is now available
            self.not_empty.notify()

    def dequeue(self) -> any:
        with self.not_empty:
            while len(self.queue) == 0:
                # Buffer is empty, wait until a producer adds an item
                self.not_empty.wait()
            
            item = self.queue.popleft()
            # Notify waiting producers that space is now available
            self.not_full.notify()
            return item
```

---

## 🪢 3. Deadlocks & The 4 Coffman Conditions

A deadlock occurs when two or more threads are unable to proceed because each is waiting for the other to release a resource.

### The 4 Conditions Required for Deadlock:
1. **Mutual Exclusion**: Resources cannot be shared simultaneously.
2. **Hold and Wait**: A thread holds at least one resource and waits to acquire additional resources held by others.
3. **No Preemption**: Resources cannot be forcibly confiscated from a thread.
4. **Circular Wait**: Thread A waits for Thread B, which waits for Thread A ($T_1 \rightarrow T_2 \rightarrow \dots \rightarrow T_1$).

### Deadlock Prevention: Strict Lock Ordering

```python
import threading

class Account:
    def __init__(self, account_id: int, balance: float):
        self.id = account_id
        self.balance = balance
        self.lock = threading.Lock()

def transfer(source: Account, target: Account, amount: float):
    # DEADLOCK VULNERABLE:
    # If thread 1 transfers A -> B and thread 2 transfers B -> A simultaneously!
    # source.lock.acquire()
    # target.lock.acquire()

    # SOLUTION: Acquire locks in a globally consistent order (e.g. by ID)
    first_lock = source.lock if source.id < target.id else target.lock
    second_lock = target.lock if source.id < target.id else source.lock

    with first_lock:
        with second_lock:
            if source.balance >= amount:
                source.balance -= amount
                target.balance += amount
                print(f"Transferred ${amount} from {source.id} to {target.id}")
            else:
                print("Insufficient funds")
```

---

## ⚙️ 4. Thread Pool Pattern

A pool of worker threads that continuously pull tasks from a queue and execute them without the overhead of creating and destroying threads repeatedly.

```python
import threading
from queue import Queue
from typing import Callable

class WorkerThread(threading.Thread):
    def __init__(self, task_queue: Queue):
        super().__init__(daemon=True)
        self.task_queue = task_queue

    def run(self):
        while True:
            func, args, kwargs = self.task_queue.get()
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"Error executing task: {e}")
            finally:
                self.task_queue.task_done()

class SimpleThreadPool:
    def __init__(self, num_workers: int):
        self.task_queue = Queue()
        self.workers = [WorkerThread(self.task_queue) for _ in range(num_workers)]
        for worker in self.workers:
            worker.start()

    def submit(self, func: Callable, *args, **kwargs):
        self.task_queue.put((func, args, kwargs))

    def wait_completion(self):
        self.task_queue.join()
```
