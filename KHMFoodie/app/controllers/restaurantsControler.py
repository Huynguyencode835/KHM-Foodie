from app.dao.restaurantsDao import RestaurantsDao
from flask import jsonify, request


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
                "avatar": r.avatar,
                "cover_image": r.cover_image,
                "description": r.description,
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
            return jsonify(restaurant.to_dict()), 200
        else:
            return jsonify({'message': 'Restaurant not found'}), 404