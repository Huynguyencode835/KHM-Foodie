from flask import Blueprint
from app.controllers.voucherController import VoucherController


voucher_api = Blueprint("voucher_api", __name__)

voucher_api.add_url_rule("/promotions", view_func=VoucherController.list_vouchers, methods=["GET"])
voucher_api.add_url_rule("/promotions", view_func=VoucherController.create_voucher, methods=["POST"])
voucher_api.add_url_rule("/promotions/<int:voucher_id>", view_func=VoucherController.update_voucher, methods=["PUT"])
voucher_api.add_url_rule("/promotions/<int:voucher_id>", view_func=VoucherController.delete_voucher, methods=["DELETE"])
