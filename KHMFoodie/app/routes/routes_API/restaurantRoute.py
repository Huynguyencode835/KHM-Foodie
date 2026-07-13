from flask import Blueprint
from app.controllers.restaurantsControler import RestaurantsController

restaurant_api = Blueprint("restaurant_api", __name__)
controller = RestaurantsController()

restaurant_api.add_url_rule("/", view_func=controller.get_all_restaurants, methods=["GET"])
restaurant_api.add_url_rule("/<int:restaurant_id>", view_func=controller.get_restaurant_by_id, methods=["GET"])