
import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services import machine


def parse_json_body(request):
    """Parse and validate a JSON request body."""
    if request.content_type != "application/json":
        raise ValueError("Content-Type must be application/json")

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid JSON")

    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")

    return data


@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def coin_endpoint(request):
    """Insert or return quarters."""

    if request.method == "PUT":
        try:
            data = parse_json_body(request)

            if type(data.get("coin")) is not int or data["coin"] != 1:
                raise ValueError("Only one US quarter is accepted")

            machine.insert_coin(data["coin"])

        except ValueError as error:
            return JsonResponse(
                {"error": str(error)},
                status=400
            )

        response = HttpResponse(status=204)
        response["X-Coins"] = "1"
        return response

    returned = machine.return_coins()

    response = HttpResponse(status=204)
    response["X-Coins"] = str(returned)
    return response


@require_http_methods(["GET"])
def inventory_endpoint(request):
    """Return the remaining quantities of all beverages."""

    return JsonResponse(
        machine.get_inventory(),
        safe=False,
        status=200
    )


@require_http_methods(["GET"])
def item_inventory_endpoint(request, item_id):
    """Return the quantity of a specific beverage."""

    quantity = machine.get_item_quantity(item_id)

    if quantity is None:
        return JsonResponse(
            {"error": "Beverage not found"},
            status=404
        )

    return JsonResponse(quantity, safe=False, status=200)


@csrf_exempt
@require_http_methods(["PUT"])
def purchase_endpoint(request, item_id):
    """Purchase exactly one beverage."""

    result = machine.purchase(item_id)

    if result["status"] == "invalid_item":
        return JsonResponse(
            {"error": "Beverage not found"},
            status=404
        )

    if result["status"] == "out_of_stock":
        response = HttpResponse(status=404)
        response["X-Coins"] = str(result["coins_returned"])
        return response

    if result["status"] == "insufficient_funds":
        response = HttpResponse(status=403)
        response["X-Coins"] = str(result["coins_returned"])
        return response

    response = JsonResponse({
        "quantity": 1
    }, status=200)

    response["X-Coins"] = str(result["coins_returned"])
    response["X-Inventory-Remaining"] = str(result["quantity"])

    return response
@csrf_exempt
@require_http_methods(["GET", "PUT"])
def item_endpoint(request, item_id):
    if request.method == "GET":
        return item_inventory_endpoint(request, item_id)

    return purchase_endpoint(request, item_id)