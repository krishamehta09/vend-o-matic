from django.test import TestCase
from .services import VendingMachine
from .services import machine

class VendingMachineTests(TestCase):

    def setUp(self):
        self.machine = VendingMachine()

    def test_initial_inventory(self):
        self.assertEqual(self.machine.get_inventory(), [5, 5, 5])

    def test_insert_quarter(self):
        self.assertEqual(self.machine.insert_coin(1), 1)

    def test_reject_invalid_coin(self):
        with self.assertRaises(ValueError):
            self.machine.insert_coin(5)

    def test_purchase_with_exact_payment(self):
        self.machine.insert_coin(1)
        self.machine.insert_coin(1)

        result = self.machine.purchase(1)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["coins_returned"], 0)
        self.assertEqual(result["quantity"], 4)

    def test_purchase_with_extra_coin(self):
        self.machine.insert_coin(1)
        self.machine.insert_coin(1)
        self.machine.insert_coin(1)

        result = self.machine.purchase(1)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["coins_returned"], 1)
        self.assertEqual(result["quantity"], 4)

    def test_insufficient_funds(self):
        self.machine.insert_coin(1)

        result = self.machine.purchase(1)

        self.assertEqual(result["status"], "insufficient_funds")
        self.assertEqual(result["coins_returned"], 1)
        self.assertEqual(result["quantity"], 5)

    def test_out_of_stock(self):
        for _ in range(5):
            self.machine.insert_coin(1)
            self.machine.insert_coin(1)
            self.machine.purchase(1)

        self.machine.insert_coin(1)
        self.machine.insert_coin(1)

        result = self.machine.purchase(1)

        self.assertEqual(result["status"], "out_of_stock")
        self.assertEqual(result["quantity"], 0)

    def test_return_coins(self):
        self.machine.insert_coin(1)
        self.machine.insert_coin(1)

        returned = self.machine.return_coins()

        self.assertEqual(returned, 2)
        self.assertEqual(self.machine.return_coins(), 0)


class VendingAPITests(TestCase):

    def setUp(self):
        machine.inventory = {
            1: 5,
            2: 5,
            3: 5,
        }
        machine.coins = 0

    def test_insert_coin(self):
        response = self.client.put(
            "/",
            data='{"coin": 1}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["X-Coins"], "1")

    def test_return_coins(self):
        self.client.put(
            "/",
            data='{"coin": 1}',
            content_type="application/json",
        )
        self.client.put(
            "/",
            data='{"coin": 1}',
            content_type="application/json",
        )

        response = self.client.delete("/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["X-Coins"], "2")

    def test_get_inventory(self):
        response = self.client.get("/inventory")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [5, 5, 5])

    def test_get_single_item_inventory(self):
        response = self.client.get("/inventory/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 5)

    def test_purchase_with_exact_payment(self):
        self.client.put("/", data='{"coin": 1}', content_type="application/json")
        self.client.put("/", data='{"coin": 1}', content_type="application/json")

        response = self.client.put("/inventory/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"quantity": 1})
        self.assertEqual(response["X-Coins"], "0")
        self.assertEqual(response["X-Inventory-Remaining"], "4")

    def test_invalid_coin(self):
        response = self.client.put(
            "/",
            data='{"coin": true}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
    def test_insufficient_funds(self):
        self.client.put(
            "/",
            data='{"coin": 1}',
            content_type="application/json",
        )

        response = self.client.put("/inventory/1")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["X-Coins"], "1")

    def test_out_of_stock(self):
        machine.inventory[1] = 0
        machine.coins = 2

        response = self.client.put("/inventory/1")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["X-Coins"], "2")

    def test_invalid_item_id(self):
        response = self.client.get("/inventory/99")

        self.assertEqual(response.status_code, 404)

    def test_invalid_json(self):
        response = self.client.put(
            "/",
            data="not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_missing_coin_field(self):
        response = self.client.put(
            "/",
            data="{}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_string_coin_value(self):
        response = self.client.put(
            "/",
            data='{"coin": "1"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
    def test_multiple_coin_insertions(self):
        for _ in range(3):
            response = self.client.put(
                "/",
                data='{"coin": 1}',
                content_type="application/json",
            )

            self.assertEqual(response.status_code, 204)
            self.assertEqual(response["X-Coins"], "1")

        # Three quarters inserted: two used, one returned.
        response = self.client.put("/inventory/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"quantity": 1})
        self.assertEqual(response["X-Coins"], "1")
        self.assertEqual(response["X-Inventory-Remaining"], "4")

    def test_purchase_with_no_coins(self):
        response = self.client.put("/inventory/1")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["X-Coins"], "0")

    def test_fifth_purchase_succeeds_and_sixth_fails(self):
        # Purchase all five units.
        for _ in range(5):
            self.client.put(
                "/",
                data='{"coin": 1}',
                content_type="application/json",
            )
            self.client.put(
                "/",
                data='{"coin": 1}',
                content_type="application/json",
            )

            response = self.client.put("/inventory/1")
            self.assertEqual(response.status_code, 200)

        # The sixth purchase should fail because the item is out of stock.
        self.client.put(
            "/",
            data='{"coin": 1}',
            content_type="application/json",
        )
        self.client.put(
            "/",
            data='{"coin": 1}',
            content_type="application/json",
        )

        response = self.client.put("/inventory/1")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["X-Coins"], "2")

    def test_out_of_stock_inventory_remains_zero(self):
        machine.inventory[1] = 0
        machine.coins = 2

        response = self.client.put("/inventory/1")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["X-Coins"], "2")

        inventory_response = self.client.get("/inventory/1")
        self.assertEqual(inventory_response.json(), 0)