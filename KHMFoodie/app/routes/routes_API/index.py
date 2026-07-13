from app.routes.routes_API.restaurantRoute import restaurant_api
from app.routes.routes_API.searchRoute import search_api


def route_api(app):
    app.register_blueprint(restaurant_api, url_prefix="/api/restaurants")
    app.register_blueprint(search_api, url_prefix = "/api/search")