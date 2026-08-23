from app.extensions import db
from app.models.model import SystemConfig, DEFAULT_MAX_CART_ITEMS


class SystemConfigDao:

    @staticmethod
    def get_max_cart_items():
        config = SystemConfig.query.first()
        if config:
            return config.max_cart_items
        return DEFAULT_MAX_CART_ITEMS
