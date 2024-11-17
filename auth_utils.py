from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
from datetime import datetime
import csv
import re
import random
from typing import Dict
import string

from maps_utils import address_to_coords


CSV_PATH = os.path.join(os.getcwd(), 'customers.csv')

def generate_customer_id():
    """Generate a unique customer ID in the format 'RB' followed by 8 digits"""
    return f"RB{''.join(random.choices(string.digits, k=8))}"

def ensure_csv_exists():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'w', newline='') as file:
            writer = csv.writer(file)
            headers = [
                'customer_id', 'first_name', 'last_name', 'dob', 'ssn',
                'email', 'phone', 'address', 'city', 'state',
                'employment_status', 'employer', 'income', 'occupation',
                'account_type', 'debit_card', 'password', 'customer_lat', 'customer_long', 'created_at'
            ]
            writer.writerow(headers)

def save_customer(data):
    customer_id = generate_customer_id()
    with open(CSV_PATH, 'a', newline='') as file:
        writer = csv.writer(file)
        row = [
            customer_id,
            data.get('firstName', ''),
            data.get('lastName', ''),
            data.get('dob', ''),
            data.get('ssn', ''),
            data.get('email', ''),
            data.get('phone', ''),
            data.get('address', ''),
            data.get('city', ''),
            data.get('state', ''),
            data.get('employmentStatus', ''),
            data.get('employer', ''),
            data.get('income', ''),
            data.get('occupation', ''),
            data.get('accountType', ''),
            data.get('debitCard', ''),
            data.get('password', ''),
            data.get('customer_lat', 0.0),
            data.get('customer_long', 0.0),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
        writer.writerow(row)
    return customer_id


def validate_step(step_num, form_data):
    if step_num == 1:
        return all([
            form_data.get('firstName'),
            form_data.get('lastName'),
            form_data.get('dob'),
            form_data.get('ssn')
        ])
    elif step_num == 2:
        return all([
            form_data.get('email'),
            form_data.get('phone'),
            form_data.get('address'),
            form_data.get('city'),
            form_data.get('state')
        ])
    elif step_num == 3:
        return all([
            form_data.get('employmentStatus'),
            form_data.get('income'),
            form_data.get('occupation')
        ])
    elif step_num == 4:
        return all([
            form_data.get('accountType'),
            form_data.get('debitCard'),
            form_data.get('password'),
            form_data.get('confirmPassword')
        ])
    return False

def verify_customer(email, password):
    """Verify customer credentials against CSV file"""
    if not os.path.exists(CSV_PATH):
        return None
    
    with open(CSV_PATH, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['email'] == email and row['password'] == password:
                return {
                    'customer_id': row['customer_id'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email']
                }
    return None

def customer_signup_fn():
    if request.method == 'POST':
        current_step = int(request.form.get('current_step', 1))
        
        for key, value in request.form.items():
            if key != 'current_step':
                session[key] = value

        if not validate_step(current_step, request.form):
            flash('Please fill in all required fields.', 'error')
            return render_template('customer-signup.html', step=current_step)

        try:
            if current_step == 4:
                if request.form.get('password') != request.form.get('confirmPassword'):
                    flash('Passwords do not match.', 'error')
                    return render_template('customer-signup.html', step=4)
                    
                ensure_csv_exists()
                address = f'{session["address"]}, {session["city"]}, {session["state"]}'
                customer_lat, customer_long = address_to_coords(address)
                session['customer_lat'] = customer_lat
                session['customer_long'] = customer_long
                customer_id = save_customer(session)
                customer_session({
                    'customer_id': customer_id,
                    'first_name': session['firstName'],
                    'last_name': session['lastName'],
                    'email': session['email'],

                })
                return redirect(url_for('merchant_map'))
            
            next_step = current_step + 1
            return render_template('customer-signup.html', step=next_step)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            flash('An error occurred. Please try again. ' + e, 'error')
            return render_template('customer-signup.html', step=current_step)

    step = request.args.get('step')
    if step is None and not session.get('step'):
        step = 1
    elif step is None:
        step = session.get('step')
    step = int(step)
    session['step'] = step
    return render_template('customer-signup.html', step=step)

def customer_signin_fn():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('customer-signin.html')
        
        customer = verify_customer(email, password)
        
        if customer:
            # Store all necessary customer data in session
            customer_session(customer)
            return redirect(url_for('merchant_map'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('customer-signin.html')
    
    return render_template('customer-signin.html')

def customer_session(customer: Dict):
    for key in customer:
        session[key] = customer[key]
