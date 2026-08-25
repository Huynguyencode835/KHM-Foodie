from decimal import Decimal

from app.extensions import db
from app.models.model import Order, OrderItem, Status


class OrderDao:
    """Data access for creating and updating customer payment orders."""

    @staticmethod
    def create_order_from_cart(cart, data):
        customer_name = str(data.get("customer_name") or "").strip()
        customer_phone = str(data.get("customer_phone") or "").strip()
        customer_email = str(data.get("customer_email") or "").strip() or None
        delivery_address = str(data.get("delivery_address") or "").strip()
        note = str(data.get("note") or "").strip() or None

        if not customer_name:
            raise ValueError("Vui lòng nhập họ và tên")
        if not customer_phone:
            raise ValueError("Vui lòng nhập số điện thoại")
        if not delivery_address:
            raise ValueError("Vui lòng nhập địa chỉ giao hàng")
        if len(customer_name) > 150:
            raise ValueError("Họ và tên quá dài")
        if len(customer_phone) > 50:
            raise ValueError("Số điện thoại quá dài")
        if customer_email and len(customer_email) > 150:
            raise ValueError("Email quá dài")
        if len(delivery_address) > 300:
            raise ValueError("Địa chỉ giao hàng quá dài")
        if note and len(note) > 300:
            raise ValueError("Ghi chú quá dài")
        if not cart.items:
            raise ValueError("Giỏ hàng đang trống")

        subtotal = Decimal("0")
        order_items = []
        for cart_item in cart.items:
            if not cart_item.dish or not cart_item.dish.active:
                raise ValueError("Một món ăn trong giỏ hàng không còn phục vụ")
            if cart_item.quantity <= 0:
                raise ValueError("Số lượng món ăn không hợp lệ")

            unit_price = Decimal(str(cart_item.price))
            subtotal += unit_price * cart_item.quantity
            order_items.append(OrderItem(
                name=cart_item.dish.name,
                dish_id=cart_item.dish_id,
                unit_price=unit_price,
                quantity=cart_item.quantity,
            ))

        order = Order(
            name="pending-order",
            user_id=cart.user_id,
            restaurant_id=cart.restaurant_id,
            status=Status.PENDING_PAYMENT,
            note=note,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            delivery_address=delivery_address,
            shipping_fee=Decimal("0"),
            total_amount=subtotal,
            items=order_items,
        )
        db.session.add(order)
        db.session.flush()
        order.name = f"DH-{order.id:05d}"

        for cart_item in list(cart.items):
            db.session.delete(cart_item)

        return order

    @staticmethod
    def update_order_status(order_id, status):
        order = Order.query.get(order_id)
        if not order:
            return None
        order.status = status
        db.session.commit()
        return order
