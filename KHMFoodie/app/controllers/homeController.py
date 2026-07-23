from flask import render_template, abort
from flask_login import current_user, login_required
from app.models.model import UserRole, CuisineType


def index():
    return render_template('homePage.html', title='KHM Foodie', description='Welcome to KHM Foodie! Explore the best food in Cambodia.')

def login_page():
    return render_template('loginPage.html')

def register_page():
    return render_template('registerPage.html')

def register_page_restaurant():
    return render_template('registerPageRestaurant.html')

@login_required
def me_page():
    role = current_user.role

    if role == UserRole.RESTAURANT:
        layout_template = 'layout/baseRestaurent.html'
        cuisine_types = [(c.name, c.value) for c in CuisineType]
        r = current_user.restaurant
        return render_template(
            'mePage.html',
            layout_template=layout_template,
            role='Restaurant',
            cuisine_types=cuisine_types,
            opening_time=r.opening_time.strftime('%H:%M') if r and r.opening_time else '06:30',
            closing_time=r.closing_time.strftime('%H:%M') if r and r.closing_time else '22:30',
            is_open=r.status if r and r.status is not None else True
        )

    elif role == UserRole.CUSTOMER:
        layout_template = 'layout/baseCustomer.html'
        return render_template(
            'mePage.html',
            layout_template=layout_template,
            role='Customer'
        )

    else:
        layout_template = 'layout/baseCustomer.html'
        return render_template(
            'mePage.html',
            layout_template=layout_template,
            role='Guest'
        )


@login_required
def promotions_page():
    role = current_user.role
    if role != UserRole.RESTAURANT:
        abort(403)

    return render_template(
        'promotionsPage.html',
        title='Khuyến mãi'
    )
