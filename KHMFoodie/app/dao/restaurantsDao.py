from app.models.model import Restaurant
from app.models.model import Dish
from sqlalchemy import func

class RestaurantsDao:
    
    @staticmethod
    def get_all_restaurants():
        return Restaurant.query.with_entities(
            Restaurant.id,
            func.coalesce(Restaurant.cover_image, Restaurant.avatar).label("cover_image"),
            Restaurant.name,
            Restaurant.cuisine_type,
            Restaurant.address,
            Restaurant.opening_time,
            Restaurant.closing_time
        ).filter_by(active=True).all()

    @staticmethod
    def get_restaurant_by_id(restaurant_id):
        return Restaurant.query.filter_by(id=restaurant_id, active=True).first()

    @staticmethod
    def search_restaurants(keyword):
        if not keyword:
            return Restaurant.query.filter_by(active=True).all()
        return Restaurant.query.filter(
            Restaurant.active == True,
            Restaurant.name.ilike(f"%{keyword}%")
        ).all()

    @staticmethod
    def search_dishes(keyword):
        if not keyword:
            return []
        return Dish.query.filter(
            Dish.active == True,
            Dish.name.ilike(f"%{keyword}%")
        ).all()