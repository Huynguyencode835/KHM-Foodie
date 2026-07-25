from app.dao.restaurantsDao import RestaurantsDao
from flask import jsonify, render_template, request
from app.dao.dishesDao import DishesDao


class RestaurantsController:
    @staticmethod
    def get_all_restaurants():
        restaurants = RestaurantsDao.get_all_restaurants()

        data = []

        for r in restaurants:
            data.append({
                "id": r.id,
                "name": r.name,
                "address": r.address,
                "cover_image": r.cover_image,
                "cuisine_type": r.cuisine_type.value if r.cuisine_type else None,
                "opening_time":
                    r.opening_time.strftime("%H:%M")
                    if r.opening_time else None,
                "closing_time":
                    r.closing_time.strftime("%H:%M")
                    if r.closing_time else None
            })

        return jsonify({
            "data": data
        }), 200

    @staticmethod
    def get_restaurant_by_id(restaurant_id):
        restaurant = RestaurantsDao.get_restaurant_by_id(restaurant_id)
        if restaurant:
            user = restaurant.user
            return jsonify({
                "id": restaurant.id,
                "name": restaurant.name,
                "address": user.address if user else None,
                "avatar": user.avatar if user else None,
                "cover_image": restaurant.cover_image,
                "description": restaurant.description,
                "cuisine_type": restaurant.cuisine_type.value if restaurant.cuisine_type else None,
                "opening_time":
                    restaurant.opening_time.strftime("%H:%M")
                    if restaurant.opening_time else None,
                "closing_time":
                    restaurant.closing_time.strftime("%H:%M")
                    if restaurant.closing_time else None,
                "phonenumber": user.phonenumber if user else None,
                "email": user.email if user else None,
                "status": restaurant.status,
                "tax_code": restaurant.tax_code,
                "username": user.username if user else None,
                "role": user.role.value if user and user.role else None,
                "auth_provider": user.auth_provider if user else None,
                "active": restaurant.active,
                "created_at": restaurant.created_at.isoformat() if restaurant.created_at else None,
                "created_updated_at": restaurant.created_updated_at.isoformat() if restaurant.created_updated_at else None
            }), 200
        else:
            return jsonify({'message': 'Restaurant not found'}), 404


    @staticmethod
    def get_list_dishes(restaurant_id):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        pagination = DishesDao.get_list_dishes_by_restaurant(restaurant_id, page, per_page)

        data = []
        for d in pagination.items:
            data.append({
                "id": d.id,
                "name": d.name,
                "category": d.category.value if d.category else None,
                "description": d.description,
                "price": float(d.price) if d.price is not None else None,
                "image": d.image
            })

        return jsonify({
            "data": data,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }), 200

    @staticmethod
    def index(restaurant_id):
        return render_template(
            "restaurantDetail.html",
            title="Chi tiết nhà hàng"
        )