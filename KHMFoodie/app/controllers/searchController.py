from app.dao.restaurantsDao import RestaurantsDao
from flask import jsonify, request, render_template


class SearchController:
    @staticmethod
    def search_restaurants():
        keyword = request.args.get('q', '').strip()
        restaurants = RestaurantsDao.search_restaurants(keyword)

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
                "opening_time": r.opening_time.strftime("%H:%M") if r.opening_time else None,
                "closing_time": r.closing_time.strftime("%H:%M") if r.closing_time else None
            })

        return jsonify({"data": data, "keyword": keyword}), 200
    

    @staticmethod
    def search_restaurants():
        keyword = request.args.get('q', '').strip()
        restaurants = RestaurantsDao.search_restaurants(keyword)
        dishes = RestaurantsDao.search_dishes(keyword)  # thêm dòng này

        restaurant_data = [
            {
                "id": r.id,
                "name": r.name,
                "address": r.address,
                "avatar": r.avatar,
                "cover_image": r.cover_image,
                "description": r.description,
                "cuisine_type": r.cuisine_type.value if r.cuisine_type else None,
                "opening_time": r.opening_time.strftime("%H:%M") if r.opening_time else None,
                "closing_time": r.closing_time.strftime("%H:%M") if r.closing_time else None
            }
            for r in restaurants
        ]

        dish_data = [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "image": d.image,
                "price": d.price,
                "category": d.category.value if d.category else None,
                "restaurant_id": d.restaurant_id,
                "restaurant_name": d.restaurant.name if d.restaurant else None,
                "restaurant_avatar": d.restaurant.avatar if d.restaurant else None
            }
            for d in dishes
        ]

        return jsonify({
            "data": restaurant_data,
            "dishes": dish_data,
            "keyword": keyword
        }), 200
    

    @staticmethod
    def search_web():
        keyword = request.args.get('q', '').strip()
        restaurants = RestaurantsDao.search_restaurants(keyword)
        dishes = RestaurantsDao.search_dishes(keyword)
        return render_template(
            "searchCustomer.html",
            title="Tìm kiếm",
            restaurants=restaurants,
            dishes=dishes,
            keyword=keyword
        )