from flask import Blueprint
from app.controllers.homeController import index, login_page, register_page

main = Blueprint("main", __name__)

main.add_url_rule("/", view_func=index)
main.add_url_rule("/login", view_func=login_page)
main.add_url_rule("/register", view_func=register_page)
