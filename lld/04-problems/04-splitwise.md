# 💸 Low-Level Design: Splitwise (Expense Sharing App)

Splitwise allows groups of friends to split expenses, track individual balances, and simplify net settlements.

---

## 1. Functional Requirements
1. **User & Groups**: Users can form groups or split non-group expenses.
2. **Split Types**:
   - `EQUAL`: Split amount equally among $N$ participants.
   - `EXACT`: Specify exact amounts per participant.
   - `PERCENT`: Specify percentage share per participant (must sum to 100%).
3. **Balance Sheet**: Show what User A owes User B and vice-versa.
4. **Debt Simplification**: Minimize total transactions needed to settle all balances.

---

## 2. Object Model & Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

class SplitType(Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENT = "PERCENT"

class User:
    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

class Split:
    def __init__(self, user: User, amount: float = 0.0):
        self.user = user
        self.amount = amount

class Expense(ABC):
    def __init__(self, expense_id: str, amount: float, paid_by: User, splits: list[Split]):
        self.expense_id = expense_id
        self.amount = amount
        self.paid_by = paid_by
        self.splits = splits

    @abstractmethod
    def validate(self) -> bool:
        pass

class EqualExpense(Expense):
    def validate(self) -> bool:
        return len(self.splits) > 0

class ExactExpense(Expense):
    def validate(self) -> bool:
        total = sum(s.amount for s in self.splits)
        return abs(total - self.amount) < 0.01

class ExpenseService:
    @staticmethod
    def create_expense(expense_id: str, amount: float, paid_by: User,
                       split_type: SplitType, splits: list[Split]) -> Expense:
        if split_type == SplitType.EQUAL:
            split_amount = round(amount / len(splits), 2)
            for s in splits:
                s.amount = split_amount
            # Handle rounding delta on first user
            delta = amount - (split_amount * len(splits))
            splits[0].amount += delta
            return EqualExpense(expense_id, amount, paid_by, splits)
        elif split_type == SplitType.EXACT:
            return ExactExpense(expense_id, amount, paid_by, splits)
        raise NotImplementedError(f"SplitType {split_type} not yet implemented")

class SplitwiseManager:
    def __init__(self):
        self.users: dict[str, User] = {}
        # balances[user_a][user_b] = amount user_a owes user_b
        self.balances: dict[str, dict[str, float]] = {}

    def register_user(self, user: User):
        self.users[user.user_id] = user
        self.balances[user.user_id] = {}

    def add_expense(self, expense: Expense):
        if not expense.validate():
            raise ValueError("Invalid expense distribution")

        paid_by = expense.paid_by.user_id
        for split in expense.splits:
            owed_by = split.user.user_id
            if paid_by == owed_by:
                continue
            
            # Update pairwise balance
            current_balance = self.balances[owed_by].get(paid_by, 0.0)
            self.balances[owed_by][paid_by] = current_balance + split.amount

    def show_balances(self):
        print("\n--- Current Balance Sheets ---")
        has_balances = False
        for user_a, debts in self.balances.items():
            for user_b, amount in debts.items():
                if amount > 0:
                    has_balances = True
                    print(f"{self.users[user_a].name} owes {self.users[user_b].name}: ${amount:.2f}")
        if not has_balances:
            print("All settled up!")
```

---

## 3. Debt Simplification Algorithm (Min Cash Flow)

Instead of $O(N^2)$ cross-payments, calculate the net balance for each person ($\text{credits} - \text{debits}$) and settle the greatest debtor with the greatest creditor greedily:

```python
def simplify_debts(net_balances: dict[str, float]) -> list[tuple[str, str, float]]:
    """
    Given net balances (positive = creditor, negative = debtor),
    returns the minimum number of transactions to clear all debts.
    """
    transactions = []
    
    # Filter out zero balances
    debtors = [[u, -bal] for u, bal in net_balances.items() if bal < -0.01]
    creditors = [[u, bal] for u, bal in net_balances.items() if bal > 0.01]

    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor, debt_amount = debtors[i]
        creditor, credit_amount = creditors[j]
        
        settle_amt = min(debt_amount, credit_amount)
        transactions.append((debtor, creditor, round(settle_amt, 2)))

        debtors[i][1] -= settle_amt
        creditors[j][1] -= settle_amt

        if debtors[i][1] < 0.01:
            i += 1
        if creditors[j][1] < 0.01:
            j += 1

    return transactions
```
