from decimal import Decimal
from datetime import datetime

from sqlalchemy import or_

from app.extensions import db
from app.models.model import (
    Order, OrderItem, OrderStatus,
    Voucher, DiscountType
)


class OrderDao:

    @staticmethod
    def _to_decimal(value):
        if value is None:
            return Decimal("0")
        return Decimal(str(value))

    @staticmethod
    def _get_valid_voucher(voucher_code, restaurant_id, subtotal):
        if not voucher_code:
            return None

        code = voucher_code.strip().upper()
        now = datetime.utcnow()

        voucher = Voucher.query.filter(
            Voucher.code == code,
            Voucher.active == True,
            or_(
                Voucher.restaurant_id == restaurant_id,
                Voucher.restaurant_id.is_(None)
            )
        ).first()

        if not voucher:
            raise ValueError("Voucher không tồn tại hoặc không áp dụng cho nhà hàng này")

        if voucher.start_date > now or voucher.end_date < now:
            raise ValueError("Voucher đã hết hạn hoặc chưa bắt đầu")

        if voucher.used_count >= voucher.usage_limit:
            raise ValueError("Voucher đã hết lượt sử dụng")

        minimum_order = OrderDao._to_decimal(voucher.minimum_order)
        if subtotal < minimum_order:
            raise ValueError("Đơn hàng chưa đạt giá trị tối thiểu để dùng voucher")

        return voucher

    @staticmethod
    def _calculate_discount(voucher, subtotal):
        if not voucher:
            return Decimal("0")

        discount_value = OrderDao._to_decimal(voucher.discount_value)

        if voucher.discount_type == DiscountType.PERCENTAGE:
            discount = subtotal * discount_value / Decimal("100")

            if voucher.max_discount is not None:
                max_discount = OrderDao._to_decimal(voucher.max_discount)
                discount = min(discount, max_discount)

            return min(discount, subtotal)

        if voucher.discount_type == DiscountType.FIXED_AMOUNT:
            return min(discount_value, subtotal)

        return Decimal("0")


    @staticmethod
    def create_order_from_cart(cart, checkout_data):
        if not cart:
            raise ValueError("Cart không tồn tại")

        if not cart.items:
            raise ValueError("Cart đang trống")

        user = cart.user
        restaurant = cart.restaurant

        if not user:
            raise ValueError("Cart không có user hợp lệ")

        if not restaurant:
            raise ValueError("Cart không có restaurant hợp lệ")

        customer_name = checkout_data.get("customer_name") or user.name
        customer_phone = checkout_data.get("customer_phone") or user.phonenumber
        customer_email = checkout_data.get("customer_email") or user.email
        delivery_address = checkout_data.get("delivery_address") or user.address
        note = checkout_data.get("note") or cart.note

        if not customer_name:
            raise ValueError("Tên người nhận là bắt buộc")

        if not customer_phone:
            raise ValueError("Số điện thoại người nhận là bắt buộc")

        if not delivery_address:
            raise ValueError("Địa chỉ giao hàng là bắt buộc")

        subtotal = Decimal("0")
        snapshot_items = []

        for cart_item in cart.items:
            dish = cart_item.dish

            if not dish or not dish.active:
                raise ValueError("Một số món trong giỏ đã ngừng bán")

            if dish.restaurant_id != cart.restaurant_id:
                raise ValueError("Món ăn không thuộc nhà hàng của cart")

            quantity = int(cart_item.quantity)
            unit_price = OrderDao._to_decimal(cart_item.price)
            item_subtotal = unit_price * quantity

            subtotal += item_subtotal

            snapshot_items.append({
                "dish_id": dish.id,
                "dish_name": dish.name,
                "dish_image": dish.image,
                "unit_price": unit_price,
                "quantity": quantity,
                "subtotal_amount": item_subtotal,
            })

        voucher_code = checkout_data.get("voucher_code")
        voucher = OrderDao._get_valid_voucher(
            voucher_code,
            cart.restaurant_id,
            subtotal
        )

        discount_amount = OrderDao._calculate_discount(voucher, subtotal)
        shipping_fee = OrderDao._to_decimal(checkout_data.get("shipping_fee", 0))
        total_amount = subtotal - discount_amount + shipping_fee

        if total_amount <= 0:
            raise ValueError("Tổng tiền thanh toán không hợp lệ")

        restaurant_user = restaurant.user if restaurant else None

        order = Order(
            name=f"order-{cart.user_id}-{cart.restaurant_id}-{int(datetime.utcnow().timestamp())}",
            user_id=cart.user_id,
            restaurant_id=cart.restaurant_id,
            voucher_id=voucher.id if voucher else None,

            status=OrderStatus.PENDING_PAYMENT,
            note=note,

            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            delivery_address=delivery_address,

            restaurant_name=restaurant.name,
            restaurant_phone=restaurant_user.phonenumber if restaurant_user else None,
            restaurant_address=restaurant_user.address if restaurant_user else None,

            voucher_code=voucher.code if voucher else None,
            subtotal_amount=subtotal,
            discount_amount=discount_amount,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
        )

        try:
            db.session.add(order)
            db.session.flush()

            for item in snapshot_items:
                db.session.add(OrderItem(
                    name=item["dish_name"],
                    order_id=order.id,
                    dish_id=item["dish_id"],
                    dish_name=item["dish_name"],
                    dish_image=item["dish_image"],
                    unit_price=item["unit_price"],
                    quantity=item["quantity"],
                    subtotal_amount=item["subtotal_amount"],
                ))

            db.session.commit()
            return order

        except Exception:
            db.session.rollback()
            raise


    @staticmethod
    def get_order_by_id(order_id):
        return Order.query.options(
            db.joinedload(Order.items),
            db.joinedload(Order.payment_transactions),
            db.joinedload(Order.user),
            db.joinedload(Order.restaurant)
        ).get(order_id)

    @staticmethod
    def update_order_status(order_id, status):
        order = Order.query.get(order_id)

        if not order:
            return None

        if isinstance(status, str):
            status = OrderStatus[status]

        order.status = status

        if status == OrderStatus.PAID and not order.paid_at:
            order.paid_at = datetime.utcnow()

        if status == OrderStatus.CANCELLED and not order.cancelled_at:
            order.cancelled_at = datetime.utcnow()

        db.session.commit()
        return order