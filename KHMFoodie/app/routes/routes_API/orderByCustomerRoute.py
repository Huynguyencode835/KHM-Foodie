from flask import Blueprint
from flask_login import login_required
from app.controllers.orderByCustomerController import OrderByCustomerController

orderCustomer_api = Blueprint("orderCustomer_api", __name__)
controller = OrderByCustomerController()

orderCustomer_api.add_url_rule("/", view_func=login_required(controller.loadOrders), methods=["GET"])
orderCustomer_api.add_url_rule("/<int:order_id>", view_func=login_required(controller.get_order_detail_customer), methods=["GET"])


