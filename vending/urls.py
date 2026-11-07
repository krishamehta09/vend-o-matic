
from django.urls import path
from . import views

urlpatterns = [
    path("", views.coin_endpoint, name="coin_endpoint"),
    path("inventory", views.inventory_endpoint, name="inventory"),
    path(
        "inventory/<int:item_id>",
        views.item_endpoint,
        name="item",
    ),
]
