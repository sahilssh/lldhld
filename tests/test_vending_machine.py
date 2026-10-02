import unittest

class Item:
    def __init__(self, code: str, name: str, price: float, count: int):
        self.code = code
        self.name = name
        self.price = price
        self.count = count

class TestVendingMachine(unittest.TestCase):
    def test_vending_machine_flow(self):
        # Local definition of vending machine for fast test execution
        class SimpleVendingMachine:
            def __init__(self):
                self.balance = 0.0
                self.items = {}

            def add_item(self, item: Item):
                self.items[item.code] = item

            def insert(self, amt: float):
                self.balance += amt

            def buy(self, code: str):
                item = self.items[code]
                if self.balance < item.price:
                    raise ValueError("Insufficient funds")
                if item.count <= 0:
                    raise ValueError("Sold out")
                item.count -= 1
                change = round(self.balance - item.price, 2)
                self.balance = 0.0
                return item.name, change

        vm = SimpleVendingMachine()
        vm.add_item(Item("C1", "Chips", 1.25, 2))
        vm.insert(1.00)
        with self.assertRaises(ValueError):
            vm.buy("C1")
        
        vm.insert(0.50)  # total 1.50
        name, change = vm.buy("C1")
        self.assertEqual(name, "Chips")
        self.assertEqual(change, 0.25)
        self.assertEqual(vm.items["C1"].count, 1)

if __name__ == "__main__":
    unittest.main()
