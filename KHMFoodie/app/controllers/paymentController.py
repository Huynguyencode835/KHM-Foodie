import os

from flask import request, jsonify, render_template, current_app, redirect, url_for, flash
from flask_login import current_user, login_required

from app.extensions import db
from app.dao.cartDao import CartDao
from app.dao.orderDao import OrderDao
from app.dao.restaurantsDao import RestaurantsDao
from app.service.momoService import create_momo_payment, verify_momo_signature
from app.service.notificationByEmail import send_order_payment_success_email


def _ipn_response(message, status_code=200):
    return jsonify({"message": message}), status_code


class PaymentController:

    @staticmethod
    @login_required
    def checkout(restaurant_id):
        restaurant = RestaurantsDao.get_restaurant_by_id(restaurant_id)
        cart = CartDao.get_cart_by_user_and_restaurant(current_user.id, restaurant_id)
        if not restaurant or not cart or not cart.items:
            return redirect(url_for("restaurant_bp.index", restaurant_id=restaurant_id))

        cart_total = sum(item.price * item.quantity for item in cart.items)

        return render_template(
            "payment.html",
            restaurant=restaurant,
            cart=cart,
            cart_total=cart_total,
            customer=current_user,
        )

    @staticmethod
    @login_required
    def create_payment(restaurant_id):
        data = request.get_json(silent=True) or {}

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

            redirect_url = os.getenv("MOMO_REDIRECT_URL", "http://127.0.0.1:5000/payment/return")
            ipn_url = os.getenv("MOMO_IPN_URL", "http://127.0.0.1:5000/api/payment/ipn")

            momo_res, momo_order_id, request_id = create_momo_payment(
                amount=int(order.total_amount),
                order_info=f"Thanh toan don hang #{order.id}",
                redirect_url=redirect_url,
                ipn_url=ipn_url,
            )

            if momo_res.get("resultCode") != 0:
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": momo_res.get("message", "Không thể tạo thanh toán MoMo")
                }), 400

            order.momo_order_id = momo_order_id
            order.momo_request_id = request_id
            db.session.commit()

            return jsonify({
                "success": True,
                "payment_url": momo_res["payUrl"],
                "order_id": order.id,
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

        result_code = params.get("resultCode")
        momo_order_id = params.get("orderId")

        is_valid_signature = verify_momo_signature(params)
        order = OrderDao.get_order_by_momo_order_id(momo_order_id)

        if is_valid_signature and result_code == "0" and order:
            order, updated = OrderDao.mark_order_paid_momo(order.id, momo_order_id)

            if updated and order.customer_email:
                try:
                    send_order_payment_success_email(
                        recipient=order.customer_email,
                        order_id=order.id,
                        total_amount=order.total_amount,
                        restaurant_name=order.restaurant.name if order.restaurant else "Nhà hàng"
                    )
                except Exception as email_error:
                    current_app.logger.exception(email_error)

            flash("Thanh toán thành công!", "success")
        else:
            if order:
                OrderDao.mark_order_payment_failed(order.id)
            flash("Thanh toán chưa thành công, vui lòng thử lại.", "danger")

        return redirect(url_for("me_bp.me_page"))

    @staticmethod
    def payment_ipn():
        # MoMo gọi IPN bằng POST kèm JSON body (khác GET query string của VNPay trước đây)
        params = request.get_json(silent=True) or {}

        try:
            if not verify_momo_signature(params):
                return _ipn_response("Invalid signature", 400)

            momo_order_id = params.get("orderId")
            result_code = params.get("resultCode")

            order = OrderDao.get_order_by_momo_order_id(momo_order_id)
            if not order:
                return _ipn_response("Order not found", 404)

            expected_amount = int(order.total_amount)
            if int(params.get("amount", 0)) != expected_amount:
                return _ipn_response("Invalid amount", 400)

            if result_code == "0":
                order, updated = OrderDao.mark_order_paid_momo(order.id, momo_order_id)

                if updated and order.customer_email:
                    try:
                        send_order_payment_success_email(
                            recipient=order.customer_email,
                            order_id=order.id,
                            total_amount=order.total_amount,
                            restaurant_name=order.restaurant.name if order.restaurant else "Nhà hàng"
                        )
                    except Exception as email_error:
                        current_app.logger.exception(email_error)
            else:
                OrderDao.mark_order_payment_failed(order.id)

            return _ipn_response("Confirm Success", 200)

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(e)
            return _ipn_response("Unknown error", 500)
