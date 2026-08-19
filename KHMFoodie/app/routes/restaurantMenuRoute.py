from flask import Blueprint
from flask_login import login_required

from app.controllers.restaurantMenuController import RestaurantMenuController

restaurantMenu_bp = Blueprint('restaurantMenu_bp', __name__)

restaurantMenu_bp.add_url_rule('/restaurant_menu', view_func=login_required(RestaurantMenuController.index))
