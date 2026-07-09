from app.controllers.controller import index
from flask import Blueprint

test_bp = Blueprint('test_bp', __name__)

test_bp.add_url_rule('/', view_func=index, methods=['GET'])
