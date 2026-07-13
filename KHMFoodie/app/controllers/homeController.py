from flask import render_template


def index():
    return render_template('homePage.html', title='KHM Foodie', description='Welcome to KHM Foodie! Explore the best food in Cambodia.')


def login_page():
    return render_template('loginPage.html')

def register_page():
    return render_template('registerPage.html')
