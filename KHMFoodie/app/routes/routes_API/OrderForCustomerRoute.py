from flask import Blueprint
from flask_login import login_required
from app.controllers.OrderForCustomerController import OrderForCustomerController

orderCustomer_api = Blueprint("orderCustomer_api", __name__)
controller = OrderForCustomerController()

orderCustomer_api.add_url_rule("/", view_func=login_required(controller.loadOrders), methods=["GET"])
orderCustomer_api.add_url_rule("/<int:order_id>", view_func=login_required(controller.get_order_detail_customer), methods=["GET"])
orderCustomer_api.add_url_rule("/create", view_func=login_required(controller.create_order), methods=["POST"])
orderCustomer_api.add_url_rule("/<int:order_id>/expire", view_func=login_required(controller.expire_order), methods=["POST"])


