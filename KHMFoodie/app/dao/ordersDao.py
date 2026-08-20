from sqlalchemy import or_

from app.extensions import db
from app.models.model import Order, OrderItem, Status
from app.service.notificationByFCM import send_push_notification


class OrdersDao:

    PIPELINE_STATUSES = [
        Status.PAID,
        Status.PREPARING,
        Status.COMPLETED,
    ]

    @staticmethod
    def get_orders(restaurant_id, status=None, keyword=None,
                            start_date=None, end_date=None,
                            page=1, per_page=10):
        query = Order.query.options(
            db.joinedload(Order.items).joinedload(OrderItem.dish),
            db.joinedload(Order.voucher)
        ).filter(Order.restaurant_id == restaurant_id)

        if status is not None:
            try:
                status_enum = status if isinstance(status, Status) else Status[status.upper()]
                query = query.filter(Order.status == status_enum)
            except (KeyError, AttributeError):
                pass
        else:
            query = query.filter(Order.status.in_(OrdersDao.PIPELINE_STATUSES))

        if keyword:
            like = f"%{keyword.strip()}%"
            query = query.filter(
                or_(
                    Order.name.ilike(like),
                    Order.customer_name.ilike(like),
                    Order.customer_phone.ilike(like),
                )
            )

        if start_date is not None:
            query = query.filter(Order.created_at >= start_date)
        if end_date is not None:
            query = query.filter(Order.created_at <= end_date)

        return query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_order_by_id_and_restaurant(order_id, restaurant_id):
        return Order.query.options(
            db.joinedload(Order.items).joinedload(OrderItem.dish),
            db.joinedload(Order.voucher)
        ).filter_by(id=order_id, restaurant_id=restaurant_id).first()

    @staticmethod
    def approve_order(order_id, restaurant_id):
        order = OrdersDao.get_order_by_id_and_restaurant(order_id, restaurant_id)
        if not order:
            return None

        if order.status == Status.PAID:
            order.status = Status.PREPARING
            notify = True
        elif order.status == Status.PREPARING:
            order.status = Status.COMPLETED
            notify = False
        else:
            return None

        db.session.commit()
        if notify:
            send_push_notification(
                order.user_id,
                "Đơn hàng đã được duyệt",
                f"Đơn hàng {order.name} đã được nhà hàng xác nhận."
            )
        return order

    @staticmethod
    def reject_order(order_id, restaurant_id, reason=None):
        order = OrdersDao.get_order_by_id_and_restaurant(order_id, restaurant_id)
        if not order or order.status not in (Status.PAID, Status.PREPARING):
            return None

        reason = (reason or "").strip()
        if not reason:
            raise ValueError("rejection_reason là bắt buộc")

        order.status = Status.CANCELLED
        order.rejection_reason = reason
        db.session.commit()
        send_push_notification(
            order.user_id,
            "Đơn hàng bị từ chối",
            f"Đơn hàng {order.name} bị từ chối: {reason}"
        )
        return order