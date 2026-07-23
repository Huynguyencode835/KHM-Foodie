from app.models.model import Restaurant, User, Dish, RestaurantApprovalStatus
from app.extensions import db
from sqlalchemy import func
from app.service.notificationByEmail import send_restaurant_approved_email,send_restaurant_rejected_email

class RestaurantsDao:

    @staticmethod
    def get_restaurants_by_status(status, page=1, per_page=10):
        query = Restaurant.query.options(
            db.joinedload(Restaurant.user)
        )
        if status and status.lower() != "all":
            try:
                status_enum = RestaurantApprovalStatus[status.upper()]
                query = query.filter(Restaurant.approval_status == status_enum)
            except KeyError:
                pass
        query = query.order_by(Restaurant.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def approve_restaurant(restaurant_id):
        r = Restaurant.query.get(restaurant_id)
        if not r:
            return None
        r.approval_status = RestaurantApprovalStatus.APPROVED
        r.rejection_reason = None
        if r.user:
            r.user.active = True
            r.active = True
        db.session.commit()
        send_restaurant_approved_email(
            recipient=r.user.email,
            restaurant_name=r.user.name
        )
        return r

    @staticmethod
    def reject_restaurant(restaurant_id, reason=None):
        r = Restaurant.query.get(restaurant_id)
        if not r:
            return None
        reason = reason.strip()
        r.approval_status = RestaurantApprovalStatus.REJECTED
        r.rejection_reason = reason
        if r.user:
            r.user.active = False
        db.session.commit()
        send_restaurant_rejected_email(
            recipient=r.user.email,
            restaurant_name=r.user.name
        )
        return r
    
    @staticmethod
    def get_all_restaurants():
        return db.session.query(
            Restaurant.id,
            func.coalesce(Restaurant.cover_image, User.avatar).label("cover_image"),
            Restaurant.name,
            Restaurant.cuisine_type,
            User.address,
            Restaurant.opening_time,
            Restaurant.closing_time
        ).join(User, Restaurant.id == User.id
        ).filter(Restaurant.active == True).all()

    @staticmethod
    def get_restaurant_by_id(restaurant_id):
        return Restaurant.query.options(
            db.joinedload(Restaurant.user)
        ).filter_by(id=restaurant_id, active=True).first()

    @staticmethod
    def search_restaurants(keyword):
        query = Restaurant.query.options(db.joinedload(Restaurant.user)).filter(Restaurant.active == True)
        if keyword:
            query = query.filter(Restaurant.name.ilike(f"%{keyword}%"))
        return query.all()

    @staticmethod
    def search_dishes(keyword):
        if not keyword:
            return []
        return Dish.query.options(
            db.joinedload(Dish.restaurant).joinedload(Restaurant.user)
        ).filter(
            Dish.active == True,
            Dish.name.ilike(f"%{keyword}%")
        ).all()
