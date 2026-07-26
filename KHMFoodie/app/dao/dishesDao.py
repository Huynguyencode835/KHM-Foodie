from app.models.model import Dish


class DishesDao:
    @staticmethod
    def get_list_dishes_by_restaurant(restaurant_id, page=1, per_page=12):
        pagination = Dish.query.with_entities(
            Dish.id,
            Dish.name,
            Dish.category,
            Dish.description,
            Dish.price,
            Dish.image
        ).filter_by(restaurant_id=restaurant_id, active=True).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        return pagination