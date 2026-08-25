from flask import Blueprint

from app.controllers.paymentController import PaymentController

payment_bp = Blueprint("payment_bp", __name__)

payment_bp.add_url_rule(
    "/return",
    view_func=PaymentController.payment_return,
    methods=["GET"]
)
