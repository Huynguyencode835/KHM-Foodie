from app.models.model import Cart, CartItems, Dish
from app.extensions import db


class CartDao:

    @staticmethod
    def get_cart_by_user_and_restaurant(user_id, restaurant_id):
        return Cart.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()

    @staticmethod
    def get_cart_by_id(cart_id):
        return Cart.query.options(
            db.joinedload(Cart.items).joinedload(CartItems.dish)
        ).get(cart_id)

    @staticmethod
    def get_or_create_cart(user_id, restaurant_id):
        cart = Cart.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
        if cart:
            return cart
        cart = Cart(name=f"cart-{user_id}-{restaurant_id}", user_id=user_id, restaurant_id=restaurant_id)
        db.session.add(cart)
        db.session.commit()
        return cart

    @staticmethod
    def add_item(user_id, restaurant_id, dish_id, quantity=1):
        dish = Dish.query.get(dish_id)
        if not dish or not dish.active:
            return None

        cart = CartDao.get_or_create_cart(user_id, restaurant_id)

        item = CartItems.query.filter_by(cart_id=cart.id, dish_id=dish_id).first()
        if item:
            item.quantity += quantity
        else:
            item = CartItems(
                name=dish.name,
                cart_id=cart.id,
                dish_id=dish_id,
                quantity=quantity,
                price=dish.price,
            )
            db.session.add(item)

        db.session.commit()
        return item

    @staticmethod
    def update_item_quantity(cart_item_id, quantity):
        item = CartItems.query.get(cart_item_id)
        if not item:
            return None
        if quantity <= 0:
            db.session.delete(item)
            db.session.commit()
            return None
        item.quantity = quantity
        db.session.commit()
        return item

    @staticmethod
    def remove_item(cart_item_id):
        item = CartItems.query.get(cart_item_id)
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    @staticmethod
    def clear_cart(cart_id):
        cart = Cart.query.get(cart_id)
        if not cart:
            return False
        CartItems.query.filter_by(cart_id=cart_id).delete()
        db.session.commit()
        return True

    @staticmethod
    def get_carts_by_user(user_id):
        return Cart.query.options(
            db.joinedload(Cart.items).joinedload(CartItems.dish)
        ).filter_by(user_id=user_id).all()
