def register_routes(app):
    from app.routes.index import route_web
    route_web(app)