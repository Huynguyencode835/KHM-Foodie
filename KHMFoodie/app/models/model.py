import hashlib
from datetime import datetime, time as dtime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    Float, Enum, ForeignKey, Time
)
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from enum import Enum as RoleEnum
from app.extensions import db


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)

    def __str__(self):
        return self.name


class UserRole(RoleEnum):
    ADMIN = "Admin"
    CUSTOMER = "Customer"
    RESTAURANT = "Restaurant"


class User(Base, UserMixin):
    __tablename__ = 'user'
    username = Column(String(150), unique=True, nullable=True)
    password = Column(String(150), nullable=True)
    phonenumber = Column(String(150), nullable=True)
    avatar = Column(String(300), default="https://res.cloudinary.com/dy1unykph/image/upload/v1740037805/apple-iphone-16-pro-natural-titanium_lcnlu2.webp")
    email = Column(String(150), unique=True, nullable=True)
    address = Column(String(300), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    auth_provider = Column(String(50), default='local')
    restaurant = relationship(
        'Restaurant',
        backref=backref('user', uselist=False),
        uselist=False
    )
    carts = relationship('Cart', backref='user', lazy=True)


class CuisineType(RoleEnum):
    VIETNAMESE = "Món Việt"
    ASIAN = "Món Á"
    WESTERN = "Món Âu"
    JAPANESE = "Món Nhật"
    KOREAN = "Món Hàn"
    CHINESE = "Món Trung"
    THAI = "Món Thái"
    VEGETARIAN = "Món chay"
    FAST_FOOD = "Đồ ăn nhanh"
    SEAFOOD = "Hải sản"
    BBQ_HOTPOT = "Nướng & Lẩu"
    CAFE_DESSERT = "Cafe & Tráng miệng"
    OTHER = "Khác"


class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    description = Column(String(500), nullable=True)
    status = Column(Boolean, default=True)
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)
    cuisine_type = Column(Enum(CuisineType), nullable=True)
    tax_code = Column(String(50), nullable=True)
    cover_image = Column(String(300), nullable=True)
    is_close = Column(Boolean, default=False)

    carts = relationship('Cart', backref='restaurant', lazy=True)
    vouchers = relationship('Voucher', backref='restaurant', lazy=True)


class DishCategory(RoleEnum):
    APPETIZER = "Món khai vị"
    MAIN_COURSE = "Món chính"
    DESSERT = "Món tráng miệng"
    BEVERAGE = "Đồ uống"
    SIDE_DISH = "Món ăn kèm"


class DiscountType(RoleEnum):
    PERCENTAGE = "Phần trăm"
    FIXED_AMOUNT = "Số tiền cố định"


class Dish(Base):
    __tablename__ = 'dish'
    description = Column(String(500), nullable=True)
    image = Column(String(300), nullable=True)
    price = Column(Float, nullable=False)
    category = Column(Enum(DishCategory), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship('Restaurant', backref=backref('dishes', lazy=True))

class Cart(Base):
    __tablename__ = 'cart'
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)

class Voucher(Base):
    __tablename__ = 'voucher'
    code = Column(String(50), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    discount_type = Column(Enum(DiscountType), nullable=False)
    discount_value = Column(Float, nullable=False)
    minimum_order = Column(Float, default=0)
    max_discount = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    usage_limit = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=True)

class CartItems(Base):
    __tablename__ = 'cart_items'
    cart_id = Column(Integer, ForeignKey('cart.id'), nullable=False)
    dish_id = Column(Integer, ForeignKey('dish.id'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=False)
    cart = relationship('Cart', backref=backref('items', lazy=True))
    dish = relationship('Dish', backref=backref('cart_items', lazy=True))

    def __str__(self):
        return f"CartItem({self.cart_id}, {self.dish_id})"

def hash_password(raw_password: str) -> str:
    return str(hashlib.md5(raw_password.encode('utf-8')).hexdigest())


def parse_time(time_str):
    if not time_str:
        return None
    h, m = map(int, time_str.split(':'))
    if h == 24:
        h = 23
        m = 59
    return dtime(hour=h, minute=m)