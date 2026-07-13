from flask import render_template


def index():
    return render_template('homePage.html', title='KHM Foodie', description='Welcome to KHM Foodie! Explore the best food in Cambodia.')
