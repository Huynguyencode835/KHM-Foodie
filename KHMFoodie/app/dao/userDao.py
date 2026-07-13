from app.models.model import User, hash_password
from app.extensions import db


class UserDao:

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(int(user_id))

    @staticmethod
    def create_user(name, username, email, phone, password):
        new_user = User(
            name=name,
            username=username,
            email=email,
            phonenumber=phone,
            password=hash_password(password)
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user
