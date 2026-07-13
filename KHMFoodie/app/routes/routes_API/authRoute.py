from flask import Blueprint
from app.controllers.authController import LoginController

auth_bp = Blueprint("auth_bp", __name__)

auth_bp.add_url_rule("/login", view_func=LoginController.login, methods=["POST"])
auth_bp.add_url_rule("/logout", view_func=LoginController.logout, methods=["GET"])
auth_bp.add_url_rule("/register", view_func=LoginController.register, methods=["POST"])