# 🧠 Behavioral Design Patterns

Behavioral design patterns identify common communication patterns between objects, increasing flexibility in carrying out interaction algorithms.

---

## 1. Strategy Pattern

Defines a family of algorithms, encapsulates each one, and makes them interchangeable at runtime without modifying the client.

```python
from abc import ABC, abstractmethod

# Route Finding Strategy Interface
class RoutingStrategy(ABC):
    @abstractmethod
    def calculate_route(self, origin: str, destination: str) -> dict:
        pass

class DrivingStrategy(RoutingStrategy):
    def calculate_route(self, origin: str, destination: str) -> dict:
        return {"mode": "drive", "time_mins": 25, "distance_km": 15}

class TransitStrategy(RoutingStrategy):
    def calculate_route(self, origin: str, destination: str) -> dict:
        return {"mode": "transit", "time_mins": 40, "distance_km": 18}

class WalkingStrategy(RoutingStrategy):
    def calculate_route(self, origin: str, destination: str) -> dict:
        return {"mode": "walk", "time_mins": 110, "distance_km": 10}

# Context
class Navigator:
    def __init__(self, strategy: RoutingStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: RoutingStrategy):
        self._strategy = strategy

    def navigate(self, start: str, end: str):
        result = self._strategy.calculate_route(start, end)
        print(f"Route ({result['mode']}): {result['time_mins']} mins, {result['distance_km']} km")

# Client code
nav = Navigator(DrivingStrategy())
nav.navigate("Times Square", "Brooklyn Bridge")
nav.set_strategy(TransitStrategy())
nav.navigate("Times Square", "Brooklyn Bridge")
```

---

## 2. Observer Pattern

Defines a subscription mechanism to notify multiple objects about any events that happen to the object they are observing.

```python
from abc import ABC, abstractmethod

# Subscriber Interface
class PriceObserver(ABC):
    @abstractmethod
    def on_price_update(self, symbol: str, price: float) -> None:
        pass

# Publisher / Subject
class CryptoTicker:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self._price = 0.0
        self._subscribers: list[PriceObserver] = []

    def subscribe(self, observer: PriceObserver):
        self._subscribers.append(observer)

    def unsubscribe(self, observer: PriceObserver):
        self._subscribers.remove(observer)

    def update_price(self, new_price: float):
        self._price = new_price
        self._notify()

    def _notify(self):
        for observer in self._subscribers:
            observer.on_price_update(self.symbol, self._price)

# Concrete Subscribers
class MobileAlertService(PriceObserver):
    def on_price_update(self, symbol: str, price: float) -> None:
        print(f"📱 Mobile Push: {symbol} is now ${price:.2f}")

class TradingBot(PriceObserver):
    def on_price_update(self, symbol: str, price: float) -> None:
        if price < 50000:
            print(f"🤖 Bot Action: Buy order triggered for {symbol} at ${price:.2f}")

# Usage
btc = CryptoTicker("BTC-USD")
btc.subscribe(MobileAlertService())
btc.subscribe(TradingBot())
btc.update_price(49200.00)
```

---

## 3. State Pattern

Allows an object to alter its behavior when its internal state changes. The object will appear to change its class.

```python
from abc import ABC, abstractmethod

# State Interface
class VendingMachineState(ABC):
    @abstractmethod
    def insert_coin(self, machine: "VendingMachine"): pass
    @abstractmethod
    def select_item(self, machine: "VendingMachine"): pass
    @abstractmethod
    def dispense(self, machine: "VendingMachine"): pass

class IdleState(VendingMachineState):
    def insert_coin(self, machine: "VendingMachine"):
        print("Coin accepted.")
        machine.set_state(machine.has_coin_state)

    def select_item(self, machine: "VendingMachine"):
        print("Please insert coin first.")

    def dispense(self, machine: "VendingMachine"):
        print("No payment made.")

class HasCoinState(VendingMachineState):
    def insert_coin(self, machine: "VendingMachine"):
        print("Coin already inserted.")

    def select_item(self, machine: "VendingMachine"):
        print("Item selected.")
        machine.set_state(machine.dispensing_state)

    def dispense(self, machine: "VendingMachine"):
        print("Please select item first.")

class DispensingState(VendingMachineState):
    def insert_coin(self, machine: "VendingMachine"):
        print("Please wait, dispensing item.")

    def select_item(self, machine: "VendingMachine"):
        print("Already dispensing.")

    def dispense(self, machine: "VendingMachine"):
        print("Item dispensed! Enjoy.")
        machine.set_state(machine.idle_state)

class VendingMachine:
    def __init__(self):
        self.idle_state = IdleState()
        self.has_coin_state = HasCoinState()
        self.dispensing_state = DispensingState()
        self.current_state: VendingMachineState = self.idle_state

    def set_state(self, state: VendingMachineState):
        self.current_state = state

    def insert_coin(self): self.current_state.insert_coin(self)
    def select_item(self): self.current_state.select_item(self)
    def dispense(self): self.current_state.dispense(self)

# Flow
vm = VendingMachine()
vm.insert_coin()
vm.select_item()
vm.dispense()
```

---

## 4. Chain of Responsibility Pattern

Passes requests along a chain of handlers. Upon receiving a request, each handler decides either to process the request or to pass it to the next handler in the chain.

```python
from abc import ABC, abstractmethod
from typing import Optional

class HttpRequest:
    def __init__(self, token: str, is_admin: bool, body: str):
        self.token = token
        self.is_admin = is_admin
        self.body = body

class MiddlewareHandler(ABC):
    def __init__(self):
        self._next_handler: Optional["MiddlewareHandler"] = None

    def set_next(self, handler: "MiddlewareHandler") -> "MiddlewareHandler":
        self._next_handler = handler
        return handler

    def handle(self, request: HttpRequest) -> bool:
        if self._next_handler:
            return self._next_handler.handle(request)
        return True

class AuthenticationHandler(MiddlewareHandler):
    def handle(self, request: HttpRequest) -> bool:
        if not request.token or request.token != "valid_secret_token":
            print("❌ Auth failed: Invalid token")
            return False
        print("✅ Auth passed")
        return super().handle(request)

class AuthorizationHandler(MiddlewareHandler):
    def handle(self, request: HttpRequest) -> bool:
        if not request.is_admin:
            print("❌ Forbidden: Admin access required")
            return False
        print("✅ Authorization passed")
        return super().handle(request)

class PayloadSanitizationHandler(MiddlewareHandler):
    def handle(self, request: HttpRequest) -> bool:
        if "<script>" in request.body:
            print("❌ XSS Attack detected in payload")
            return False
        print("✅ Payload sanitized")
        return super().handle(request)

# Build pipeline chain
pipeline = AuthenticationHandler()
pipeline.set_next(AuthorizationHandler()).set_next(PayloadSanitizationHandler())

# Test request
req = HttpRequest(token="valid_secret_token", is_admin=True, body="Hello World")
pipeline.handle(req)
```

---

## 5. Command Pattern

Turns a request into a stand-alone object containing all information about the request. Enables parameterizing methods with different requests, delaying or queuing execution, and supporting undoable operations.

```python
from abc import ABC, abstractmethod

# Command Interface
class Command(ABC):
    @abstractmethod
    def execute(self): pass
    @abstractmethod
    def undo(self): pass

# Receiver
class TextEditor:
    def __init__(self):
        self.content = ""

    def append(self, text: str):
        self.content += text

    def delete_last(self, length: int):
        self.content = self.content[:-length]

# Concrete Command
class InsertTextCommand(Command):
    def __init__(self, editor: TextEditor, text_to_insert: str):
        self.editor = editor
        self.text_to_insert = text_to_insert

    def execute(self):
        self.editor.append(self.text_to_insert)

    def undo(self):
        self.editor.delete_last(len(self.text_to_insert))

# Invoker with History
class CommandInvoker:
    def __init__(self):
        self._history: list[Command] = []

    def execute_command(self, cmd: Command):
        cmd.execute()
        self._history.append(cmd)

    def undo(self):
        if self._history:
            cmd = self._history.pop()
            cmd.undo()

# Test
editor = TextEditor()
invoker = CommandInvoker()

invoker.execute_command(InsertTextCommand(editor, "Hello "))
invoker.execute_command(InsertTextCommand(editor, "World!"))
print("Current text:", editor.content)  # Hello World!

invoker.undo()
print("After undo:", editor.content)    # Hello 
```
