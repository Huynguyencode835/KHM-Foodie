import hashlib
from datetime import datetime, time as dtime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    Float, Enum, ForeignKey, Time, UniqueConstraint, Text
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

class RestaurantApprovalStatus(RoleEnum):
    PENDING = "Chờ duyệt"
    APPROVED = "Đã duyệt"
    REJECTED = "Bị từ chối"

class Restaurant(Base):
    __tablename__ = 'restaurant'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    description = Column(String(500), nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    status = Column(Boolean, default=True)
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)
    cuisine_type = Column(Enum(CuisineType), nullable=True)
    tax_code = Column(String(50), nullable=True)
    cover_image = Column(String(300), nullable=True)
    approval_status = Column(Enum(RestaurantApprovalStatus), default=RestaurantApprovalStatus.PENDING)

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


class OrderStatus(RoleEnum):
    PENDING = "Chờ xác nhận"
    ACCEPTED = "Đã nhận đơn"
    PREPARING = "Đang chuẩn bị"
    DELIVERING = "Đang giao"
    COMPLETED = "Hoàn thành"
    CANCELLED = "Đã hủy"


class PaymentMethod(RoleEnum):
    COD = "Thanh toán khi nhận hàng"
    ONLINE = "Thanh toán online"


class PaymentProvider(RoleEnum):
    COD = "COD"
    VNPAY = "VNPay"

class PaymentStatus(RoleEnum):
    UNPAID = "Chưa thanh toán"
    PENDING = "Đang xử lý"
    PAID = "Đã thanh toán"
    FAILED = "Thất bại"
    REFUNDED = "Đã hoàn tiền"


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
    __table_args__ = (
        UniqueConstraint('user_id', 'restaurant_id', name='uq_cart_user_restaurant'),
    )
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    note = Column(String(300), nullable=True)

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
    __table_args__ = (
        UniqueConstraint('cart_id', 'dish_id', name='uq_cart_items_cart_dish'),
    )
    cart_id = Column(Integer, ForeignKey('cart.id'), nullable=False)
    dish_id = Column(Integer, ForeignKey('dish.id'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=False)
    cart = relationship('Cart', backref=backref('items', lazy=True))
    dish = relationship('Dish', backref=backref('cart_items', lazy=True))

    def __str__(self):
        return f"CartItem({self.cart_id}, {self.dish_id})"


class Order(Base):
    __tablename__ = 'order'
    code = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    voucher_id = Column(Integer, ForeignKey('voucher.id'), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    subtotal = Column(Float, default=0, nullable=False)
    discount_amount = Column(Float, default=0, nullable=False)
    delivery_fee = Column(Float, default=0, nullable=False)
    total_amount = Column(Float, default=0, nullable=False)
    note = Column(String(500), nullable=True)
    delivery_address = Column(String(300), nullable=False)
    recipient_name = Column(String(150), nullable=False)
    recipient_phone = Column(String(50), nullable=False)
    placed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancel_reason = Column(String(500), nullable=True)

    customer = relationship('User', backref=backref('orders', lazy=True), foreign_keys=[customer_id])
    restaurant = relationship('Restaurant', backref=backref('orders', lazy=True))
    voucher = relationship('Voucher', backref=backref('orders', lazy=True))


class OrderItem(Base):
    __tablename__ = 'order_item'
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    dish_id = Column(Integer, ForeignKey('dish.id'), nullable=True)
    dish_name = Column(String(150), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    subtotal = Column(Float, nullable=False)
    note = Column(String(300), nullable=True)

    order = relationship('Order', backref=backref('items', lazy=True))
    dish = relationship('Dish', backref=backref('order_items', lazy=True))


class Payment(Base):
    __tablename__ = 'payment'
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    method = Column(Enum(PaymentMethod), default=PaymentMethod.COD, nullable=False)
    provider = Column(Enum(PaymentProvider), default=PaymentProvider.COD, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.UNPAID, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='VND', nullable=False)
    transaction_ref = Column(String(150), nullable=True)
    gateway_payload = Column(Text, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(String(500), nullable=True)

    order = relationship('Order', backref=backref('payments', lazy=True))


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
