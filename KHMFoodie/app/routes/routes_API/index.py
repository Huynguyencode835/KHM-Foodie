from app.routes.routes_API.authRoute import auth_api
from app.routes.routes_API.restaurantRoute import restaurant_api
from app.routes.routes_API.searchRoute import search_api
from app.routes.routes_API.adminRoute import admin_api
from app.routes.routes_API.fcmRoute import fcm_api
from app.routes.routes_API.cartRoute import cart_api
from app.routes.routes_API.voucherRoute import voucher_api
from app.routes.routes_API.ordersRoute import orders_api
from app.routes.routes_API.dishesRoute import dishes_api


def route_api(app):
    app.register_blueprint(restaurant_api, url_prefix="/api/restaurants")
    app.register_blueprint(dishes_api, url_prefix="/api/dishes")
    app.register_blueprint(auth_api, url_prefix="/api/auth")
    app.register_blueprint(search_api, url_prefix="/api/search")
    app.register_blueprint(admin_api, url_prefix="/api/admin")
    app.register_blueprint(fcm_api, url_prefix="/api/fcm")
    app.register_blueprint(cart_api, url_prefix="/api/cart")
    app.register_blueprint(voucher_api, url_prefix="/api")
    app.register_blueprint(orders_api, url_prefix="/api/orders")
