from flask import Blueprint
from flask_login import login_required
from app.controllers.cartController import CartController

cart_api = Blueprint("cart_api", __name__)

cart_api.add_url_rule(
    "/<int:restaurant_id>",
    view_func=login_required(CartController.get_cart),
    methods=["GET"]
)
cart_api.add_url_rule(
    "/<int:restaurant_id>/items",
    view_func=login_required(CartController.add_item),
    methods=["POST"]
)
cart_api.add_url_rule(
    "/<int:restaurant_id>/items/<int:cart_item_id>",
    view_func=login_required(CartController.update_item),
    methods=["PATCH"]
)
cart_api.add_url_rule(
    "/<int:restaurant_id>/items/<int:cart_item_id>",
    view_func=login_required(CartController.remove_item),
    methods=["DELETE"]
)
cart_api.add_url_rule(
    "/<int:restaurant_id>/clear",
    view_func=login_required(CartController.clear_cart),
    methods=["DELETE"]
)
