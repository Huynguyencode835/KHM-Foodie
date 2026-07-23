from app.routes.routes_API.authRoute import auth_local_bp
from app.routes.routes_API.restaurantRoute import restaurant_api
from app.routes.routes_API.searchRoute import search_api
from app.routes.routes_API.adminRoute import admin_api
from app.routes.routes_API.cartRoute import cart_api
from app.routes.routes_API.voucherRoute import voucher_api


def route_api(app):
    app.register_blueprint(restaurant_api, url_prefix="/api/restaurants")
    app.register_blueprint(auth_local_bp, url_prefix="/api/auth")
    app.register_blueprint(search_api, url_prefix="/api/search")
    app.register_blueprint(admin_api, url_prefix="/api/admin")
    app.register_blueprint(cart_api, url_prefix="/api/cart")
    app.register_blueprint(voucher_api, url_prefix="/api")
