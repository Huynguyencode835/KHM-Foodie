from flask import Blueprint
from flask_login import login_required

from app.controllers.paymentController import PaymentController

payment_api = Blueprint("payment_api", __name__)

payment_api.add_url_rule(
    "/<int:restaurant_id>",
    view_func=login_required(PaymentController.create_payment),
    methods=["POST"]
)

payment_api.add_url_rule(
    "/pay/<int:order_id>",
    view_func=login_required(PaymentController.pay_existing_order),
    methods=["POST"]
)

payment_api.add_url_rule(
    "/ipn",
    view_func=PaymentController.payment_ipn,
    methods=["POST"]  # MoMo gọi IPN bằng POST kèm JSON body
)

payment_api.add_url_rule(
    "/vnpay/ipn",
    view_func=PaymentController.vnpay_ipn,
    methods=["GET"]  # VNPay gọi IPN bằng GET kèm query string
)