from flask import Flask, render_template, request, session, redirect, url_for, flash
import csv
import os
import re
import random
import string

from auth_utils import customer_signup_fn, customer_signin_fn
from maps_utils import merchant_maps_fn

name = 'Budget Buddy'
app = Flask(name)
app.config.update(
    SECRET_KEY='dev'
)

@app.route('/')
def index():
    return render_template('landing-page.html')

@app.route('/merchant-map', methods=['GET'])  # On Customer Side
def merchant_map():
    return merchant_maps_fn()

@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
    return customer_signup_fn()

@app.route('/customer/signin', methods=['GET', 'POST'])
def customer_signin():
    return customer_signin_fn()

@app.route('/signout')
def signout():
    # Clear the session
    session.clear()
    flash('You have been signed out successfully.', 'success')
    return redirect(url_for('customer_signin'))

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000)