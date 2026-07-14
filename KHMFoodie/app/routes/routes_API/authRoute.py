from flask import Blueprint
from app.controllers.authController import LoginController

auth_local_bp = Blueprint("auth_local_bp", __name__)

auth_local_bp.add_url_rule("/login", view_func=LoginController.login, methods=["POST"])
auth_local_bp.add_url_rule("/logout", view_func=LoginController.logout, methods=["GET"])
auth_local_bp.add_url_rule("/register", view_func=LoginController.register, methods=["POST"])
auth_local_bp.add_url_rule("/update-profile", view_func=LoginController.update_profile, methods=["PUT"])