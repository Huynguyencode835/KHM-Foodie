from flask import Blueprint
from app.controllers.homeController import customer_requirements

customer_requirements_bp = Blueprint("customer_requirements_bp", __name__)
customer_requirements_bp.add_url_rule("/customer-requirements", view_func=customer_requirements)