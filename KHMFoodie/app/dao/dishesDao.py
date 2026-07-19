from app.models.model import Dish, DishCategory


class DishesDao:
    @staticmethod
    def get_list_dishes_by_restaurant(restaurant_id):
        return Dish.query.with_entities(
            Dish.id,
            Dish.name,
            Dish.category,
            Dish.description,
            Dish.price,
            Dish.image
        ).filter_by(restaurant_id=restaurant_id, active=True).all()
    