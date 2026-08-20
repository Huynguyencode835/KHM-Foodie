from sqlalchemy import or_

from app.extensions import db
from app.models.model import Order, OrderItem, Status


class OrdersDao:

    PIPELINE_STATUSES = [
        Status.PAID,
        Status.PREPARING,
        Status.COMPLETED,
    ]

    @staticmethod
    def get_pipeline_orders(restaurant_id, status=None, keyword=None,
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