from app.models.model import Restaurant, User, Dish
from app.extensions import db
from sqlalchemy import func


class RestaurantsDao:
    
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