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
    def search_web():
        keyword = request.args.get('q', '').strip()
        restaurants = RestaurantsDao.search_restaurants(keyword)
        return render_template(
            "searchCustomer.html",
            title="Tìm kiếm",
            restaurants=restaurants,
            keyword=keyword
        )