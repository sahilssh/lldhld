# 🏗️ Creational Design Patterns

Creational patterns abstract the instantiation process, decoupling a system from how its objects are created, composed, and represented.

---

## 1. Singleton Pattern

Ensures a class has **only one instance** and provides a **global point of access** to it.

### Thread-Safe Double-Checked Locking (Python)
```python
import threading

class DatabaseConnectionPool:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:  # Double check
                    cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, dsn: str = "postgresql://localhost:5432/db"):
        if self._initialized:
            return
        self.dsn = dsn
        self._initialized = True
        print(f"Initialized connection pool for {dsn}")
```

### When to use & Caveats
* **Use for**: Thread pools, caches, configuration managers, hardware access (logger, printer spooler).
* **Pitfalls**: Difficult to unit test (global mutable state), violates Single Responsibility Principle.

---

## 2. Factory Method & Abstract Factory

### Factory Method
Defines an interface for creating an object, but lets subclasses decide which class to instantiate.

```python
from abc import ABC, abstractmethod

# Product Interface
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

class StripeProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        print(f"Charging ${amount} via Stripe API")
        return True

class PayPalProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        print(f"Charging ${amount} via PayPal API")
        return True

# Creator Factory
class PaymentProcessorFactory:
    @staticmethod
    def create(method: str) -> PaymentProcessor:
        match method.lower():
            case "stripe":
                return StripeProcessor()
            case "paypal":
                return PayPalProcessor()
            case _:
                raise ValueError(f"Unsupported payment gateway: {method}")
```

### Abstract Factory
Provides an interface for creating **families of related or dependent objects** without specifying their concrete classes.

```python
# Abstract Products
class Button(ABC):
    @abstractmethod
    def render(self): pass

class Checkbox(ABC):
    @abstractmethod
    def toggle(self): pass

# Concrete Products - Dark Mode
class DarkButton(Button):
    def render(self): return "Rendering Dark Mode Button"

class DarkCheckbox(Checkbox):
    def toggle(self): return "Toggled Dark Checkbox"

# Concrete Products - Light Mode
class LightButton(Button):
    def render(self): return "Rendering Light Mode Button"

class LightCheckbox(Checkbox):
    def toggle(self): return "Toggled Light Checkbox"

# Abstract Factory
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: pass
    @abstractmethod
    def create_checkbox(self) -> Checkbox: pass

class DarkThemeFactory(GUIFactory):
    def create_button(self) -> Button: return DarkButton()
    def create_checkbox(self) -> Checkbox: return DarkCheckbox()

class LightThemeFactory(GUIFactory):
    def create_button(self) -> Button: return LightButton()
    def create_checkbox(self) -> Checkbox: return LightCheckbox()
```

---

## 3. Builder Pattern

Separates the construction of a complex object from its representation, allowing the same construction process to create various representations.

```python
from typing import Optional

class HttpRequest:
    def __init__(self):
        self.url: Optional[str] = None
        self.method: str = "GET"
        self.headers: dict[str, str] = {}
        self.query_params: dict[str, str] = {}
        self.body: Optional[str] = None
        self.timeout_ms: int = 5000

    def __repr__(self):
        return f"HttpRequest(method={self.method}, url={self.url}, headers={self.headers})"

class HttpRequestBuilder:
    def __init__(self):
        self._request = HttpRequest()

    def set_url(self, url: str) -> "HttpRequestBuilder":
        self._request.url = url
        return self

    def set_method(self, method: str) -> "HttpRequestBuilder":
        self._request.method = method.upper()
        return self

    def add_header(self, key: str, value: str) -> "HttpRequestBuilder":
        self._request.headers[key] = value
        return self

    def set_body(self, body: str) -> "HttpRequestBuilder":
        self._request.body = body
        return self

    def build(self) -> HttpRequest:
        if not self._request.url:
            raise ValueError("URL must be specified before building HttpRequest")
        return self._request

# Fluent Usage
request = (
    HttpRequestBuilder()
    .set_url("https://api.github.com/users")
    .set_method("POST")
    .add_header("Authorization", "Bearer token123")
    .add_header("Content-Type", "application/json")
    .set_body('{"username": "octocat"}')
    .build()
)
```

---

## 4. Prototype Pattern

Specifies the kind of objects to create using a prototypical instance, creating new objects by copying this prototype (shallow or deep copy).

```python
import copy

class GameUnit:
    def __init__(self, name: str, health: int, weapon: dict):
        self.name = name
        self.health = health
        self.weapon = weapon

    def clone(self) -> "GameUnit":
        # Deepcopy ensures nested mutable objects (e.g. weapon dict) are not shared
        return copy.deepcopy(self)

# Prototype Registry
archer_proto = GameUnit("Archer", 100, {"type": "Bow", "damage": 25})
warrior_proto = GameUnit("Warrior", 250, {"type": "Sword", "damage": 40})

# Fast cloning without re-running heavy constructor logic
unit1 = archer_proto.clone()
unit2 = archer_proto.clone()
```
