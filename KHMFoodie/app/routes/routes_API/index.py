from app.routes.routes_API.restaurantRoute import restaurant_api


def route_api(app):
    app.register_blueprint(restaurant_api, url_prefix="/api/restaurants")