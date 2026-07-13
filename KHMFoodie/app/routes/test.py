from app.controllers.controller import index
from flask import Blueprint

from app.controllers.searchController import SearchController

test_bp = Blueprint('test_bp', __name__)

test_bp.add_url_rule('/', view_func=index, methods=['GET'])
test_bp.add_url_rule('/search_customer', view_func=SearchController.search_web, methods=['GET'])
