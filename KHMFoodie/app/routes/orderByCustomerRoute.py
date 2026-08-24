from flask import Blueprint
from flask_login import login_required
from app.controllers.orderByCustomerController import OrderByCustomerController

orderCustomer_bp = Blueprint("orderCustomer_bp", __name__)
orderCustomer_bp.add_url_rule("/", view_func=login_required(OrderByCustomerController.index))
orderCustomer_bp.add_url_rule("/<int:order_id>", view_func=login_required(OrderByCustomerController.order_detail_page))
