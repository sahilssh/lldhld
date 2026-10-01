# 🧱 Structural Design Patterns

Structural patterns explain how to assemble objects and classes into larger structures while keeping these structures flexible and efficient.

---

## 1. Adapter Pattern

Allows objects with incompatible interfaces to collaborate by converting the interface of one object so that another object can understand it.

### Practical Scenario: Third-Party Payment Gateway Integration
```python
from abc import ABC, abstractmethod

# Target Interface expected by our checkout system
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount_in_cents: int) -> bool:
        pass

# Existing / Legacy or Third-Party incompatible service
class LegacyStripeService:
    def charge_usd_dollars(self, dollars: float, customer_id: str) -> dict:
        print(f"LegacyStripe: Charged ${dollars:.2f} for user {customer_id}")
        return {"status": "SUCCESS", "code": 200}

# Object Adapter
class StripePaymentAdapter(PaymentGateway):
    def __init__(self, stripe_service: LegacyStripeService, customer_id: str):
        self._stripe = stripe_service
        self._customer_id = customer_id

    def pay(self, amount_in_cents: int) -> bool:
        # Translate cents to dollars
        dollars = amount_in_cents / 100.0
        response = self._stripe.charge_usd_dollars(dollars, self._customer_id)
        return response.get("status") == "SUCCESS"

# Client Code
def checkout(gateway: PaymentGateway, total_cents: int):
    success = gateway.pay(total_cents)
    print("Checkout result:", "Success" if success else "Failed")

adapter = StripePaymentAdapter(LegacyStripeService(), customer_id="usr_9821")
checkout(adapter, 4999)  # Charges $49.99
```

---

## 2. Decorator Pattern

Attaches new behaviors to objects dynamically by placing these objects inside special wrapper objects that contain the behaviors.

### Practical Scenario: Notification Delivery Pipeline
```python
from abc import ABC, abstractmethod

# Component Interface
class Notifier(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

# Concrete Base Component
class BaseEmailNotifier(Notifier):
    def send(self, message: str) -> None:
        print(f"[Email] Sending: {message}")

# Base Decorator
class NotifierDecorator(Notifier):
    def __init__(self, wrappee: Notifier):
        self._wrappee = wrappee

    def send(self, message: str) -> None:
        self._wrappee.send(message)

# Concrete Decorators
class SMSDecorator(NotifierDecorator):
    def send(self, message: str) -> None:
        super().send(message)
        print(f"[SMS] Sending: {message}")

class SlackDecorator(NotifierDecorator):
    def send(self, message: str) -> None:
        super().send(message)
        print(f"[Slack Channel] Sending: {message}")

# Usage: dynamically chain notification channels
pipeline = SlackDecorator(SMSDecorator(BaseEmailNotifier()))
pipeline.send("Deployment failed in production!")
# Output:
# [Email] Sending: Deployment failed in production!
# [SMS] Sending: Deployment failed in production!
# [Slack Channel] Sending: Deployment failed in production!
```

---

## 3. Facade Pattern

Provides a simplified, high-level interface to a complex set of classes, library, or subsystem.

### Practical Scenario: Home Theater / Video Streaming Transcoder
```python
class AudioDecoder:
    def decode(self, file: str): print(f"Decoding audio track from {file}")

class VideoDecoder:
    def decode(self, file: str): print(f"Decoding video frames from {file}")

class SubtitleParser:
    def parse(self, sub_file: str): print(f"Parsing subtitles from {sub_file}")

class VideoRenderer:
    def render(self): print("Rendering synchronized audio and video")

# Facade
class MediaPlaybackFacade:
    def __init__(self):
        self.audio = AudioDecoder()
        self.video = VideoDecoder()
        self.subtitles = SubtitleParser()
        self.renderer = VideoRenderer()

    def play_movie(self, movie_file: str, subtitle_file: str):
        print(f"--- Starting Playback: {movie_file} ---")
        self.audio.decode(movie_file)
        self.video.decode(movie_file)
        self.subtitles.parse(subtitle_file)
        self.renderer.render()

# Client interacts with a clean one-liner
facade = MediaPlaybackFacade()
facade.play_movie("interstellar.mkv", "interstellar_en.srt")
```

---

## 4. Proxy Pattern

Provides a placeholder or surrogate for another object to control access to it (e.g., Virtual Proxy, Protection/Auth Proxy, Caching Proxy).

### Practical Scenario: Caching & Auth Proxy
```python
from abc import ABC, abstractmethod
import time

class QueryExecutor(ABC):
    @abstractmethod
    def execute(self, sql: str) -> list[str]:
        pass

class RealQueryExecutor(QueryExecutor):
    def execute(self, sql: str) -> list[str]:
        print(f"Executing expensive DB query: '{sql}'")
        time.sleep(0.5)  # Simulate DB latency
        return [f"row1 for {sql}", f"row2 for {sql}"]

class CachingQueryProxy(QueryExecutor):
    def __init__(self, real_executor: QueryExecutor):
        self._real_executor = real_executor
        self._cache: dict[str, list[str]] = {}

    def execute(self, sql: str) -> list[str]:
        if sql in self._cache:
            print(f"[CACHE HIT] Returning cached result for '{sql}'")
            return self._cache[sql]
        
        result = self._real_executor.execute(sql)
        self._cache[sql] = result
        return result

# Usage
db_service = CachingQueryProxy(RealQueryExecutor())
db_service.execute("SELECT * FROM users")  # Miss -> queries DB
db_service.execute("SELECT * FROM users")  # Hit  -> instant from cache
```

---

## 5. Composite Pattern

Composes objects into tree structures to represent part-whole hierarchies. Enables clients to treat individual objects and compositions of objects uniformly.

```python
from abc import ABC, abstractmethod

class FileSystemItem(ABC):
    @abstractmethod
    def get_size(self) -> int:
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> None:
        pass

class File(FileSystemItem):
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size

    def get_size(self) -> int:
        return self.size

    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"📄 {self.name} ({self.size} KB)")

class Directory(FileSystemItem):
    def __init__(self, name: str):
        self.name = name
        self.children: list[FileSystemItem] = []

    def add(self, item: FileSystemItem):
        self.children.append(item)

    def get_size(self) -> int:
        return sum(child.get_size() for child in self.children)

    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"📁 {self.name}/ ({self.get_size()} KB total)")
        for child in self.children:
            child.display(indent + 1)

# Building a composite tree
root = Directory("root")
etc = Directory("etc")
etc.add(File("config.yaml", 15))
root.add(etc)
root.add(File("app.log", 120))

root.display()
```
