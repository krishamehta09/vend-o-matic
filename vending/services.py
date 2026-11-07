
from threading import Lock


class VendingMachine:

    ITEM_PRICE = 2

    def __init__(self):
        self.inventory = {
            1: 5,
            2: 5,
            3: 5,
        }
        self.coins = 0
        self.lock = Lock()

    def insert_coin(self, coin):
        if type(coin) is not int or coin != 1:
            raise ValueError("Only US quarters are accepted.")

        with self.lock:
            self.coins += 1
            return self.coins

    def return_coins(self):
        with self.lock:
            returned = self.coins
            self.coins = 0
            return returned

    def get_inventory(self):
        with self.lock:
            return [
                self.inventory[item_id]
                for item_id in sorted(self.inventory)
            ]

    def get_item_quantity(self, item_id):
        with self.lock:
            return self.inventory.get(item_id)

    def purchase(self, item_id):
        with self.lock:
            if item_id not in self.inventory:
                return {
                    "status": "invalid_item",
                    "coins_returned": 0,
                    "quantity": None,
                }

            if self.inventory[item_id] == 0:
                returned = self.coins
                self.coins = 0
                return {
                    "status": "out_of_stock",
                    "coins_returned": returned,
                    "quantity": 0,
                }

            if self.coins < self.ITEM_PRICE:
                returned = self.coins
                self.coins = 0
                return {
                    "status": "insufficient_funds",
                    "coins_returned": returned,
                    "quantity": self.inventory[item_id],
                }

            self.inventory[item_id] -= 1

            change = self.coins - self.ITEM_PRICE
            self.coins = 0

            return {
                "status": "success",
                "coins_returned": change,
                "quantity": self.inventory[item_id],
            }


machine = VendingMachine()
