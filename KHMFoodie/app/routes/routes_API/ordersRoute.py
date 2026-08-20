from flask import Blueprint

from app.controllers.orderController import OrderController
from app.middleware import role_required
from app.models.model import UserRole

orders_api = Blueprint("orders_api", __name__)

orders_api.add_url_rule(
    "/board",
    view_func=role_required(UserRole.RESTAURANT)(OrderController.board_more),
    methods=["GET"]
)