from app.models.model import Dish, DishCategory
from sqlalchemy import or_
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError


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

    @staticmethod
    def create_dishes(name, price, category, restaurant_id, description=None, image=None):
        try:
            if category not in DishCategory._value2member_map_ and category not in DishCategory.__members__:
                raise ValueError(f"Category không hợp lệ: {category}")

            if isinstance(category, str):
                category = DishCategory(category)

            new_dish = Dish(
                name=name,
                description=description,
                image=image,
                price=price,
                category=category,
                restaurant_id=restaurant_id
            )

            db.session.add(new_dish)
            db.session.commit()
            return new_dish

        except ValueError as ve:
            print(f"Lỗi giá trị: {ve}")
            db.session.rollback()
            return None
        except SQLAlchemyError as e:
            print(f"Lỗi khi tạo món ăn: {e}")
            db.session.rollback()
            return None