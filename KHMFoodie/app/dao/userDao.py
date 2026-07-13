import hashlib
from app import db
from app.models.model import User, Restaurant, UserRole

def add_user(
    name,
    phonenumber=None,
    username=None,
    password=None,
    email=None,
    role=None,
    is_restaurant=False,
    **kwargs
):
    if password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    common_data = dict(
        name=name.strip() if name else None,
        phonenumber=phonenumber.strip() if phonenumber else None,
        username=username.strip() if username else None,
        password=password if password else None,
        email=email.strip() if email else None,
        address=kwargs.get('address'),
        avatar=kwargs.get('avatar'),
        auth_provider=kwargs.get('auth_provider', 'local'),
    )
    if role:
        common_data['role'] = role

    if is_restaurant:
        user = Restaurant(
            **common_data,
            description=kwargs.get('description'),
            opening_time=kwargs.get('opening_time'),
            closing_time=kwargs.get('closing_time'),
            cuisine_type=kwargs.get('cuisine_type'),
            tax_code=kwargs.get('tax_code'),
            cover_image=kwargs.get('cover_image'),
        )
    else:
        user = User(**common_data)

    db.session.add(user)
    db.session.commit()
    return user


def check_userEmail(email):
    return User.query.filter_by(email=email.strip().lower()).first()