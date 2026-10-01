# 🧱 SOLID Principles & Modern Object-Oriented Design

A comprehensive guide to writing robust, maintainable, and extensible code using the 5 core **SOLID** design principles and modern OOP patterns.

---

## 🏛️ Quick Summary Cheat Sheet

| Principle | Core Meaning | Violation Symptom | Resolution / Pattern |
|---|---|---|---|
| **S** - Single Responsibility | A class should have one, and only one, reason to change. | "God" classes, mixing business logic with persistence and UI. | Extract separate service, repository, and formatter classes. |
| **O** - Open / Closed | Open for extension, closed for modification. | Giant `switch` / `if-else` blocks whenever a new type is added. | Strategy Pattern, Polymorphism, Abstract classes / Interfaces. |
| **L** - Liskov Substitution | Subtypes must be substitutable for their base types without breaking behavior. | Subclass throws `NotSupportedException` or overrides with empty body. | Favor Composition over Inheritance; split base class into smaller interfaces. |
| **I** - Interface Segregation | Clients should not be forced to depend upon interfaces they do not use. | "Fat" interfaces where implementations leave methods unimplemented. | Role interfaces; split into granular, focused contracts. |
| **D** - Dependency Inversion | High-level modules should depend on abstractions, not concrete details. | Instantiating concrete dependencies with `new ConcreteService()` inside classes. | Dependency Injection (Constructor Injection), Interface Abstractions. |

---

## 1. Single Responsibility Principle (SRP)

> **"A class should have one, and only one, reason to change."**

### ❌ Violation Example
An `Invoice` class that calculates totals, formats HTML, and writes to MySQL.
```python
class BadInvoice:
    def __init__(self, items: list[dict]):
        self.items = items

    def calculate_total(self) -> float:
        return sum(item["price"] * item["quantity"] for item in self.items)

    def print_invoice_html(self) -> str:
        # Presentation logic inside business entity!
        return f"<div>Invoice Total: ${self.calculate_total()}</div>"

    def save_to_database(self) -> None:
        # Persistence logic coupled directly to domain model!
        import sqlite3
        conn = sqlite3.connect("invoices.db")
        # INSERT INTO invoices ...
```

### ✅ Clean Architecture Fix
Separate business logic, rendering/presentation, and persistence:
```python
from dataclasses import dataclass

@dataclass
class LineItem:
    description: str
    price: float
    quantity: int

class Invoice:
    """Pure domain entity responsible only for invoice calculations."""
    def __init__(self, items: list[LineItem]):
        self.items = items

    def calculate_total(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

class InvoiceHtmlPresenter:
    """Responsible only for HTML rendering."""
    def render(self, invoice: Invoice) -> str:
        return f"<div class='invoice-box'>Total: ${invoice.calculate_total():.2f}</div>"

class InvoiceRepository:
    """Responsible only for persistence."""
    def save(self, invoice: Invoice) -> None:
        # Execute database insert
        pass
```

---

## 2. Open / Closed Principle (OCP)

> **"Software entities should be open for extension, but closed for modification."**

### ❌ Violation Example
Hardcoded discount calculations requiring code modifications for every new customer tier:
```python
class DiscountCalculator:
    def calculate_discount(self, customer_type: str, amount: float) -> float:
        if customer_type == "REGULAR":
            return amount * 0.05
        elif customer_type == "VIP":
            return amount * 0.20
        elif customer_type == "SUPER_VIP":  # Had to modify class to add this!
            return amount * 0.35
        return 0.0
```

### ✅ Clean Architecture Fix (Strategy Pattern)
```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass

class RegularDiscount(DiscountStrategy):
    def calculate(self, amount: float) -> float:
        return amount * 0.05

class VIPDiscount(DiscountStrategy):
    def calculate(self, amount: float) -> float:
        return amount * 0.20

class SuperVIPDiscount(DiscountStrategy):
    """Added without modifying existing classes!"""
    def calculate(self, amount: float) -> float:
        return amount * 0.35

class CheckoutService:
    def __init__(self, discount_strategy: DiscountStrategy):
        self._strategy = discount_strategy

    def calculate_final_price(self, amount: float) -> float:
        return amount - self._strategy.calculate(amount)
```

---

## 3. Liskov Substitution Principle (LSP)

> **"Subtypes must be substitutable for their base types without altering the correctness of the program."**

### ❌ Classic Violation: Square Inheriting from Rectangle
```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_width(self, width: float):
        self._width = width

    def set_height(self, height: float):
        self._height = height

    def area(self) -> float:
        return self._width * self._height

class Square(Rectangle):
    """Violates LSP: Changing width also mutates height, breaking caller expectations!"""
    def set_width(self, width: float):
        self._width = width
        self._height = width

    def set_height(self, height: float):
        self._width = height
        self._height = height

def verify_rectangle_area(r: Rectangle):
    r.set_width(5)
    r.set_height(4)
    # Expected area: 20
    # If Square is passed, area is 16! Test fails, LSP violated.
    assert r.area() == 20, f"Expected 20, got {r.area()}"
```

### ✅ Clean Architecture Fix
A Square is not functionally substitutable for a mutable Rectangle. Decouple into a common `Shape` interface:
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side * self.side
```

---

## 4. Interface Segregation Principle (ISP)

> **"Clients should not be forced to depend upon interfaces they do not use."**

### ❌ Violation Example: The "Fat" Interface
```python
class Worker(ABC):
    @abstractmethod
    def work(self): pass

    @abstractmethod
    def eat_lunch(self): pass

    @abstractmethod
    def sleep(self): pass

class RobotWorker(Worker):
    def work(self):
        print("Working 24/7...")

    def eat_lunch(self):
        raise NotImplementedError("Robots do not eat!")

    def sleep(self):
        raise NotImplementedError("Robots do not sleep!")
```

### ✅ Clean Architecture Fix
Split into narrow, role-focused interfaces:
```python
class Workable(ABC):
    @abstractmethod
    def work(self): pass

class Feedable(ABC):
    @abstractmethod
    def eat(self): pass

class HumanWorker(Workable, Feedable):
    def work(self):
        print("Human working")

    def eat(self):
        print("Human eating lunch")

class RobotWorker(Workable):
    def work(self):
        print("Robot operating autonomously")
```

---

## 5. Dependency Inversion Principle (DIP)

> **"High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions."**

### ❌ Violation Example
High-level `NotificationManager` directly couples to low-level `TwilioSmsClient`:
```python
class TwilioSmsClient:
    def send_sms(self, phone: str, text: str):
        print(f"Sending Twilio SMS to {phone}: {text}")

class NotificationManager:
    def __init__(self):
        # Direct dependency on low-level concrete implementation!
        self.sms_client = TwilioSmsClient()

    def notify(self, user_phone: str, message: str):
        self.sms_client.send_sms(user_phone, message)
```

### ✅ Clean Architecture Fix
Introduce a notification abstraction and inject dependencies:
```python
from abc import ABC, abstractmethod

class MessageSender(ABC):
    @abstractmethod
    def send(self, recipient: str, body: str) -> None:
        pass

class TwilioSmsSender(MessageSender):
    def send(self, recipient: str, body: str) -> None:
        print(f"[Twilio SMS] Sending to {recipient}: {body}")

class SendGridEmailSender(MessageSender):
    def send(self, recipient: str, body: str) -> None:
        print(f"[SendGrid Email] Sending to {recipient}: {body}")

class NotificationManager:
    """High-level module depends strictly on MessageSender abstraction."""
    def __init__(self, sender: MessageSender):
        self._sender = sender

    def notify(self, recipient: str, message: str) -> None:
        self._sender.send(recipient, message)

# Usage: easily swapped at runtime or during unit testing
sms_manager = NotificationManager(TwilioSmsSender())
email_manager = NotificationManager(SendGridEmailSender())
```
