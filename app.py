from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import datetime
import csv
import os
import re
import random
import string

name = 'Budget Buddy'
app = Flask(name)
app.config.update(
    SECRET_KEY='dev'
)

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
                'account_type', 'debit_card', 'password', 'created_at'
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
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
        writer.writerow(row)
    return customer_id

@app.route('/')
def index():
    return render_template('landing-page.html')

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

@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
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
                customer_id = save_customer(session)
                session.clear()
                flash(f'Registration completed successfully! Your Customer ID is: {customer_id}', 'success')
                return redirect(url_for('index'))
            
            next_step = current_step + 1
            return render_template('customer-signup.html', step=next_step)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
            return render_template('customer-signup.html', step=current_step)

    step = request.args.get('step')
    if step is None and not session.get('step'):
        step = 1
    elif step is None:
        step = session.get('step')
    step = int(step)
    session['step'] = step
    return render_template('customer-signup.html', step=step)

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

@app.route('/customer/signin', methods=['GET', 'POST'])
def customer_signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('customer-signin.html')
        
        customer = verify_customer(email, password)
        
        if customer:
            # Store all necessary customer data in session
            session['customer_id'] = customer['customer_id']
            session['first_name'] = customer['first_name']
            session['last_name'] = customer['last_name']
            session['email'] = customer['email']
            return redirect(url_for('merchant_map'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('customer-signin.html')
    
    return render_template('customer-signin.html')

@app.route('/merchant-map')
def merchant_map():
    # Check if user is logged in
    if 'customer_id' not in session:
        flash('Please sign in to access this page.', 'error')
        return redirect(url_for('customer_signin'))
    
    # Render merchant map with session data
    return render_template('merchant-map.html')

@app.route('/signout')
def signout():
    # Clear the session
    session.clear()
    flash('You have been signed out successfully.', 'success')
    return redirect(url_for('customer_signin'))

if __name__ == '__main__':
    print(f"Starting app... CSV path: {CSV_PATH}")
    app.run(debug=True, host='localhost', port=3000)