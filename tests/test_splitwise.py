import unittest

def simplify_debts(net_balances: dict[str, float]) -> list[tuple[str, str, float]]:
    debtors = [[u, -bal] for u, bal in net_balances.items() if bal < -0.01]
    creditors = [[u, bal] for u, bal in net_balances.items() if bal > 0.01]

    transactions = []
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

class TestSplitwiseDebtSimplification(unittest.TestCase):
    def test_debt_simplification(self):
        # A owes B $20, B owes C $20 -> net: A: -20, B: 0, C: +20
        # Optimal: A pays C $20 directly (1 transaction instead of 2)
        balances = {"A": -20.0, "B": 0.0, "C": 20.0}
        txns = simplify_debts(balances)
        self.assertEqual(len(txns), 1)
        self.assertEqual(txns[0], ("A", "C", 20.0))

if __name__ == "__main__":
    unittest.main()
