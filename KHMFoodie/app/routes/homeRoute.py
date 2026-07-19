from flask import Blueprint, send_from_directory
from app.controllers.homeController import index

home_bp = Blueprint("home_bp", __name__)
home_bp.add_url_rule("/", view_func=index)

import os
from flask import current_app

@home_bp.route("/templates/<path:filename>")
def serve_template(filename):
    return send_from_directory(os.path.join(current_app.root_path, "templates"), filename)