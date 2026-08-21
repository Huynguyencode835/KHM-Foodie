from app.extensions import db
from app.models.model import Dish, VoucherDish


class DishesDao:
    @staticmethod
    def get_list_dishes_by_restaurant(restaurant_id):
        return Dish.query.options(
            db.joinedload(Dish.voucher_links).joinedload(VoucherDish.voucher)
        ).filter_by(restaurant_id=restaurant_id, active=True).all()

    @staticmethod
    def get_active_by_ids_and_restaurant(dish_ids, restaurant_id):
        return Dish.query.filter(
            Dish.id.in_(dish_ids),
            Dish.restaurant_id == restaurant_id,
            Dish.active.is_(True)
        ).all()
