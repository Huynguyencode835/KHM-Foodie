from app.models.model import Dish, DishCategory
from sqlalchemy import or_


class DishesDao:
    @staticmethod
    def get_list_dishes_by_restaurant(restaurant_id, page=1, per_page=12, category=None, keyword=None):
        query = Dish.query.with_entities(
            Dish.id,
            Dish.name,
            Dish.category,
            Dish.description,
            Dish.price,
            Dish.image
        ).filter_by(restaurant_id=restaurant_id, active=True)

        if category and category != 'all':
            category_enum = next((c for c in DishCategory if c.value == category), None)
            if category_enum:
                query = query.filter(Dish.category == category_enum)

        if keyword:
            query = query.filter(
                or_(
                    Dish.name.ilike(f'%{keyword}%'),
                    Dish.description.ilike(f'%{keyword}%')
                )
            )

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        return pagination