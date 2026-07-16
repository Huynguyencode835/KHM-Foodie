from flask import render_template
from flask_login import current_user, login_required
from app.models.model import UserRole, CuisineType


def index():
    return render_template('homePage.html', title='KHM Foodie', description='Welcome to KHM Foodie! Explore the best food in Cambodia.')

def login_page():
    return render_template('loginPage.html')

def register_page():
    return render_template('registerPage.html')

@login_required
def me_page():
    role = current_user.role

    if role == UserRole.RESTAURANT:
        layout_template = 'layout/baseRestaurent.html'
        cuisine_types = [(c.name, c.value) for c in CuisineType]
        return render_template(
            'mePage.html',
            layout_template=layout_template,
            role='Restaurant',
            cuisine_types=cuisine_types,
            opening_time=current_user.opening_time.strftime('%H:%M') if current_user.opening_time else '06:30',
            closing_time=current_user.closing_time.strftime('%H:%M') if current_user.closing_time else '22:30',
            is_open=current_user.status if current_user.status is not None else True
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
