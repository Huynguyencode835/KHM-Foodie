import hashlib, json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    Float, Enum, ForeignKey, Time
)
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from enum import Enum as RoleEnum
from app import db, create_app
from datetime import datetime, time as dtime
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RESTAURANTS_JSON = os.path.join(BASE_DIR, "..", "data", "restaurants.json")
DISHES_JSON = os.path.join(BASE_DIR, "..", "data", "dishes.json")



class Base(db.Model):
    __abstract__=True
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

class Restaurant(User):
    __tablename__ = 'restaurant'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    description = Column(String(500), nullable=True)
    status = Column(Boolean, default=True)
    opening_time = Column(Time, nullable=True)      # VD: 08:00
    closing_time = Column(Time, nullable=True)       # VD: 22:00
    cuisine_type = Column(Enum(CuisineType), nullable=True)
    tax_code = Column(String(50), nullable=True) 
    cover_image = Column(String(300), nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'restaurant'
    }


class DishCategory(RoleEnum):
    APPETIZER = "Món khai vị"
    MAIN_COURSE = "Món chính"
    DESSERT = "Món tráng miệng"
    BEVERAGE = "Đồ uống"
    SIDE_DISH = "Món ăn kèm"

class Dish(Base):
    __tablename__ = 'dish'
    description = Column(String(500), nullable=True)
    image = Column(String(300), nullable=True)
    price = Column(Float, nullable=False)
    category = Column(Enum(DishCategory), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'), nullable=False)
    restaurant = relationship('Restaurant', backref=backref('dishes', lazy=True))

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

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
 
        # ---------- Admin & Customer mau ----------
        new_admin = User(
            name="Quản trị viên",
            username="admin",
            password=hash_password("admin"),
            avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfjno7hGrNNuPZwaFZ8U8Mhr_Yq39rzd_p0YN_HVYk6KFmMETjtgd9bwl0UhU6g4xDDGg&usqp=CAU",
            role=UserRole.ADMIN
        )
 
        new_customer = User(
            name="Customer",
            username="customer",
            password=hash_password("customer"),
            avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTfjno7hGrNNuPZwaFZ8U8Mhr_Yq39rzd_p0YN_HVYk6KFmMETjtgd9bwl0UhU6g4xDDGg&usqp=CAU",
            role=UserRole.CUSTOMER
        )
 
        db.session.add_all([new_admin, new_customer])
        db.session.commit()
 
        # ---------- Doc du lieu nha hang tu JSON ----------
        with open(RESTAURANTS_JSON, "r", encoding="utf-8") as f:
            restaurants_data = json.load(f)
 
        # map username -> Restaurant object, de sau con gan Dish
        restaurant_map = {}
 
        for r in restaurants_data:
            new_restaurant = Restaurant(
                name=r["name"],
                username=r["username"],
                password=hash_password(r["password"]),
                phonenumber=r.get("phonenumber"),
                email=r.get("email"),
                address=r.get("address"),
                avatar=r.get("avatar"),
                cover_image=r.get("cover_image"),
                description=r.get("description"),
                status=r.get("status", True),
                opening_time=parse_time(r.get("opening_time")),
                closing_time=parse_time(r.get("closing_time")),
                cuisine_type=CuisineType[r["cuisine_type"]] if r.get("cuisine_type") else None,
                tax_code=r.get("tax_code"),
                role=UserRole.RESTAURANT
            )
            db.session.add(new_restaurant)
            restaurant_map[r["username"]] = new_restaurant
 
        db.session.commit()  # commit truoc de co id cho restaurant
 
        # ---------- Doc du lieu mon an tu JSON ----------
        with open(DISHES_JSON, "r", encoding="utf-8") as f:
            dishes_data = json.load(f)
 
        for d in dishes_data:
            restaurant_obj = restaurant_map.get(d["restaurant_username"])
            if not restaurant_obj:
                continue  # bo qua neu khong tim thay nha hang tuong ung
 
            new_dish = Dish(
                name=d["name"],
                description=d.get("description"),
                image=d.get("image"),
                price=d["price"],
                category=DishCategory[d["category"]],
                restaurant=restaurant_obj
            )
            db.session.add(new_dish)
 
        db.session.commit()
 
        print(f"Đã tạo {len(restaurant_map)} nhà hàng và {len(dishes_data)} món ăn.")