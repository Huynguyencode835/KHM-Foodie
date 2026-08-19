import uuid
from decimal import Decimal

from flask import request, jsonify, render_template, current_app
from flask_login import current_user, login_required

from app.extensions import db
from app.dao.cartDao import CartDao
from app.dao.orderDao import OrderDao
from app.dao.paymentDao import PaymentDao
from app.models.model import OrderStatus
from app.service.vnpayService import (
    build_payment_url,
    verify_signature,
    VNP_RESPONSE_MESSAGES
)
from app.service.notificationByEmail import send_order_payment_success_email



def _get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def _generate_txn_ref(order_id):
    return f"{order_id}-{uuid.uuid4().hex[:12]}"


def _to_vnp_amount(amount):
    return int(Decimal(str(amount)) * 100)


def _ipn_response(code, message):
    return jsonify({
        "RspCode": code,
        "Message": message
    })


class PaymentController:

    @staticmethod
    @login_required
    def create_payment(restaurant_id):
        data = request.get_json() or {}

        cart = CartDao.get_cart_by_user_and_restaurant(
            current_user.id,
            restaurant_id
        )

        if not cart:
            return jsonify({
                "success": False,
                "message": "Cart không tồn tại"
            }), 404

        try:
            order = OrderDao.create_order_from_cart(cart, data)

            txn_ref = _generate_txn_ref(order.id)
            ip_addr = _get_client_ip()

            transaction = PaymentDao.create_transaction(
                order_id=order.id,
                txn_ref=txn_ref,
                amount=order.total_amount
            )

            payment_url = build_payment_url(
                txn_ref=transaction.vnp_txn_ref,
                amount=transaction.amount,
                order_info=f"Thanh toan don hang #{order.id}",
                ip_addr=ip_addr,
                bank_code=data.get("bank_code")
            )

            transaction.ip_addr = ip_addr
            transaction.payment_url = payment_url
            db.session.commit()

            return jsonify({
                "payment_url": payment_url
            }), 200

        except ValueError as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(e)
            return jsonify({
                "success": False,
                "message": "Không thể tạo thanh toán"
            }), 500


    @staticmethod
    def payment_return():
        params = request.args.to_dict()

        is_valid_signature = verify_signature(params)

        txn_ref = params.get("vnp_TxnRef")
        response_code = params.get("vnp_ResponseCode")
        amount = params.get("vnp_Amount")
        message = VNP_RESPONSE_MESSAGES.get(
            response_code,
            "Không xác định được trạng thái giao dịch"
        )

        transaction = None
        if txn_ref:
            transaction = PaymentDao.get_transaction_by_txn_ref(txn_ref)

        success = is_valid_signature and response_code == "00"

        return render_template(
            "paymentResult.html",
            success=success,
            is_valid_signature=is_valid_signature,
            txn_ref=txn_ref,
            amount=amount,
            response_code=response_code,
            message=message,
            transaction=transaction
        )

    @staticmethod
    def payment_ipn():
        params = request.args.to_dict()

        try:
            if not verify_signature(params):
                return _ipn_response("97", "Invalid checksum")

            txn_ref = params.get("vnp_TxnRef")
            response_code = params.get("vnp_ResponseCode")
            transaction_no = params.get("vnp_TransactionNo")
            bank_code = params.get("vnp_BankCode")
            pay_date = params.get("vnp_PayDate")
            vnp_amount = params.get("vnp_Amount")

            transaction = PaymentDao.get_transaction_by_txn_ref(txn_ref)

            if not transaction:
                return _ipn_response("01", "Order not found")

            expected_amount = _to_vnp_amount(transaction.amount)

            if int(vnp_amount) != expected_amount:
                return _ipn_response("04", "Invalid amount")

            transaction, updated = PaymentDao.mark_transaction_result(
                txn_ref=txn_ref,
                response_code=response_code,
                transaction_no=transaction_no,
                bank_code=bank_code,
                pay_date=pay_date
            )

            if not updated:
                return _ipn_response("02", "Order already confirmed")

            if transaction.status == PaymentDao.STATUS_SUCCESS:
                order = OrderDao.update_order_status(
                    transaction.order_id,
                    OrderStatus.PAID
                )

                if order and order.customer_email:
                    try:
                        send_order_payment_success_email(
                            recipient=order.customer_email,
                            order_id=order.id,
                            total_amount=order.total_amount,
                            restaurant_name=order.restaurant_name
                        )
                    except Exception as email_error:
                        current_app.logger.exception(email_error)

            elif transaction.status == PaymentDao.STATUS_FAILED:
                OrderDao.update_order_status(
                    transaction.order_id,
                    OrderStatus.PAYMENT_FAILED
                )

            return _ipn_response("00", "Confirm Success")

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(e)
            return _ipn_response("99", "Unknown error")