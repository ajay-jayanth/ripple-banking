from flask import Flask, render_template, request, session, redirect, url_for, flash
import csv
import os
import re
import random
import string
from auth_utils import (
    customer_signup_fn, 
    customer_signin_fn,
    merchant_signup_fn,  
    merchant_signin_fn   
)
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


@app.route('/merchant/signup', methods=['GET', 'POST'])
def merchant_signup():
    return merchant_signup_fn()

@app.route('/merchant/signin', methods=['GET', 'POST'])
def merchant_signin():
    return merchant_signin_fn()

# sarvesh said remove everyting in between this start
@app.route('/merchant/dashboard')
def merchant_dashboard():
    # Check if merchant is logged in
    if 'merchant_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('merchant_signin'))
    
    # Get merchant data from session
    merchant_data = {
        'merchant_id': session.get('merchant_id'),
        'business_name': session.get('business_name'),
        'email': session.get('email')
    }
    
    return render_template('merchant-dashboard.html', merchant=merchant_data)

# sarvesh said remove everyting in between this end
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000)