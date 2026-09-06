from flask import Blueprint
from flask_login import login_required
from app.controllers.restaurantMenuController import RestaurantMenuController

dishes_api = Blueprint("dishes_api", __name__)
controller = RestaurantMenuController()

dishes_api.add_url_rule("/top-recommendations", view_func=controller.get_top_recommended_dishes, methods=["GET"])
dishes_api.add_url_rule("/stats", view_func=login_required(controller.get_dishes_stats), methods=["GET"])
dishes_api.add_url_rule("/", view_func=login_required(controller.create_dishes), methods=["POST"])
dishes_api.add_url_rule("/<int:dishes_id>", view_func=login_required(controller.delete_dishes), methods=["DELETE"])
dishes_api.add_url_rule("/", view_func=login_required(controller.change_dishes_status), methods=["PATCH"])

