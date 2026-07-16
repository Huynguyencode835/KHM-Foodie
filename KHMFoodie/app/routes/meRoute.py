from flask import Blueprint
from app.controllers.homeController import me_page

me_bp = Blueprint("me_bp", __name__)
me_bp.add_url_rule("/me", view_func=me_page)