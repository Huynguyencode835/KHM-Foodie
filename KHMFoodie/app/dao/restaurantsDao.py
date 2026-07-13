from app.models.model import Restaurant


class RestaurantsDao:
    
    @staticmethod
    def get_all_restaurants():
        return Restaurant.query.filter_by(active=True).all()

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
