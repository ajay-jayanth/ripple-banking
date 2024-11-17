from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
from datetime import datetime
import csv
import re
import random
from typing import Dict
import pandas as pd
import string

from maps_utils import address_to_coords

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
                # 'account_type', 'debit_card', 'password', 'customer_lat', 'customer_long', 'created_at'
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
            # data.get('customer_lat', 0.0),
            # data.get('customer_long', 0.0),
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
                    'email': row['email'],
                    'customer_lat': row['latitude'],
                    'customer_long': row['longitude'],
                    'address': row['address'],
                    'city': row['city'],
                    'state': row['state']
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
                address = f'{session["address"]}, {session["city"]}, {session["state"]}'
                session['address_combined'] = address
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
            session['address_combined'] = f'{session["address"]}, {session["city"]}, {session["state"]}'
            return redirect(url_for('merchant_map'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('customer-signin.html')
    
    return render_template('customer-signin.html')

def customer_session(customer: Dict):
    for key in customer:
        session[key] = customer[key]

# merchent stuff

MERCHANT_CSV_PATH = os.path.join(os.getcwd(), 'merchants.csv')

def generate_merchant_id():
    """Generate a unique merchant ID in the format 'MC' followed by 8 digits"""
    return f"MC{''.join(random.choices(string.digits, k=8))}"

def ensure_merchant_csv_exists():
    """Create merchants CSV with proper columns if it doesn't exist"""
    if not os.path.exists(MERCHANT_CSV_PATH):
        df = pd.DataFrame(columns=[
            'merchant_id', 'business_name', 'business_type', 'ein', 'years_in_business',
            'email', 'phone', 'website', 'first_name', 'last_name',
            'address', 'city', 'state', 'zip_code', 'business_hours',
            'bank_name', 'account_number', 'routing_number', 'monthly_revenue',
            'password', 'security_question', 'security_answer', 'created_at'
        ])
        df.to_csv(MERCHANT_CSV_PATH, index=False)

def save_merchant_data(form_data):
    """Save merchant data to the CSV file."""
    ensure_merchant_csv_exists()
    merchant_id = generate_merchant_id()

    merchant_data = {
        'merchant_id': merchant_id,
        'business_name': form_data.get('businessName', ''),
        'business_type': form_data.get('businessType', ''),
        'ein': form_data.get('ein', ''),
        'years_in_business': form_data.get('yearsInBusiness', ''),
        'email': form_data.get('email', ''),
        'phone': form_data.get('phone', ''),
        'website': form_data.get('website', ''),
        'first_name': form_data.get('firstName', ''),
        'last_name': form_data.get('lastName', ''),
        'address': form_data.get('address', ''),
        'city': form_data.get('city', ''),
        'state': form_data.get('state', ''),
        'zip_code': form_data.get('zipCode', ''),
        'business_hours': form_data.get('businessHours', ''),
        'bank_name': form_data.get('bankName', ''),
        'account_number': form_data.get('accountNumber', ''),
        'routing_number': form_data.get('routingNumber', ''),
        'monthly_revenue': form_data.get('monthlyRevenue', ''),
        'password': form_data.get('password', ''),
        'security_question': form_data.get('securityQuestion', ''),
        'security_answer': form_data.get('securityAnswer', ''),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    try:
        with open(MERCHANT_CSV_PATH, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=merchant_data.keys())
            if os.stat(MERCHANT_CSV_PATH).st_size == 0:
                writer.writeheader()
            writer.writerow(merchant_data)
    except Exception as e:
        print(f"Error saving merchant data: {e}")
        raise e

    return merchant_id

def check_email_exists(email):
    """Check if email already exists in merchants database"""
    if os.path.exists(MERCHANT_CSV_PATH):
        df = pd.read_csv(MERCHANT_CSV_PATH)
        return email in df['email'].values
    return False


def verify_merchant(email, password):
    """Verify merchant credentials and check for current loans"""
    if not os.path.exists(MERCHANT_CSV_PATH):
        print(f"DEBUG: CSV file not found at {MERCHANT_CSV_PATH}")
        return None
    
    try:
        merchant_df = pd.read_csv(MERCHANT_CSV_PATH)
        loans_df = pd.read_csv('static/data/loans.csv')
        
        # Replace NaN values with empty strings
        merchant_df = merchant_df.fillna('')
        
        # Clean the data before comparison
        merchant_df['email'] = merchant_df['email'].astype(str).str.strip()
        merchant_df['password'] = merchant_df['password'].astype(str).str.strip()
        email = str(email).strip()
        password = str(password).strip()
        
        merchant = merchant_df[(merchant_df['email'] == email) & (merchant_df['password'] == password)]
        
        if not merchant.empty:
            merchant_id = str(merchant.iloc[0]['merchant_id'])
            
            # Check if merchant has any current loans
            has_current_loan = any(
                (loans_df['merchant_id'] == merchant_id) &
                (loans_df['status'] == 'current')
            )
            print(has_current_loan)
            
            return {
                'merchant_id': merchant_id,
                'business_name': str(merchant.iloc[0]['business_name']),
                'email': str(merchant.iloc[0]['email']),
                'has_current_loan': has_current_loan
            }
    except Exception as e:
        print(f"DEBUG: Error verifying merchant: {str(e)}")
    return None

def merchant_signin_fn():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"DEBUG: Login attempt - Email: {email}")
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('merchant-signin.html')
        
        merchant = verify_merchant(email, password)
        print(f"DEBUG: Verify merchant result: {merchant}")
        
        if merchant:
            print("DEBUG: Login successful, setting session")
            # Set session data
            session['merchant_id'] = str(merchant['merchant_id'])
            session['business_name'] = str(merchant['business_name'])
            session['email'] = str(merchant['email'])
            
            # Redirect based on loan status
            if merchant['has_current_loan']:
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('merchant.merchant_dashboard'))
        else:
            print("DEBUG: Login failed - invalid credentials")
            flash('Invalid email or password.', 'error')
            return render_template('merchant-signin.html')
    
    return render_template('merchant-signin.html')

def validate_merchant_step(step_num, form_data):
    """Validate required fields for each step in the merchant signup process."""
    required_fields = {
        1: ['businessName', 'businessType', 'ein', 'yearsInBusiness'],
        2: ['email', 'phone', 'firstName', 'lastName'],
        3: ['address', 'city', 'state', 'zipCode', 'businessHours'],
        4: ['password', 'confirmPassword', 'securityQuestion', 'securityAnswer'],  # This was previously step 5
    }
    is_valid = all(form_data.get(field) for field in required_fields.get(step_num, []))
    
    if not is_valid:
        missing_fields = [field for field in required_fields.get(step_num, []) if not form_data.get(field)]
        print(f"[DEBUG] Step {step_num} - Missing fields: {missing_fields}")
    
    print(f"[DEBUG] Step {step_num} validation result: {is_valid}")
    return is_valid

def ensure_merchant_csv_exists():
    """Create merchants CSV with proper columns if it doesn't exist"""
    if not os.path.exists(MERCHANT_CSV_PATH):
        df = pd.DataFrame(columns=[
            'merchant_id', 'business_name', 'business_type', 'ein', 'years_in_business',
            'email', 'phone', 'website', 'first_name', 'last_name',
            'address', 'city', 'state', 'zip_code', 'business_hours',
            'password', 'security_question', 'security_answer', 'created_at'
        ])
        df.to_csv(MERCHANT_CSV_PATH, index=False)

def save_merchant_data(form_data):
    """Save merchant data to the CSV file."""
    ensure_merchant_csv_exists()
    merchant_id = generate_merchant_id()

    merchant_data = {
        'merchant_id': merchant_id,
        'business_name': form_data.get('businessName', ''),
        'business_type': form_data.get('businessType', ''),
        'ein': form_data.get('ein', ''),
        'years_in_business': form_data.get('yearsInBusiness', ''),
        'email': form_data.get('email', ''),
        'phone': form_data.get('phone', ''),
        'website': form_data.get('website', ''),
        'first_name': form_data.get('firstName', ''),
        'last_name': form_data.get('lastName', ''),
        'address': form_data.get('address', ''),
        'city': form_data.get('city', ''),
        'state': form_data.get('state', ''),
        'zip_code': form_data.get('zipCode', ''),
        'business_hours': form_data.get('businessHours', ''),
        'password': form_data.get('password', ''),  # Make sure password is properly saved
        'security_question': form_data.get('securityQuestion', ''),
        'security_answer': form_data.get('securityAnswer', ''),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        # Add empty values for unused bank fields to prevent NaN
        'bank_name': '',
        'account_number': '',
        'routing_number': '',
        'monthly_revenue': ''
    }

    print(f"DEBUG: Saving merchant data with password: {merchant_data['password']}")  # Debug line

    try:
        df = pd.read_csv(MERCHANT_CSV_PATH) if os.path.exists(MERCHANT_CSV_PATH) else pd.DataFrame()
        df = pd.concat([df, pd.DataFrame([merchant_data])], ignore_index=True)
        df.to_csv(MERCHANT_CSV_PATH, index=False)
        print(f"DEBUG: Merchant data saved successfully")
    except Exception as e:
        print(f"Error saving merchant data: {e}")
        raise e

    return merchant_id

def merchant_signup_fn():
    """Handle merchant signup with step-by-step control."""
    if request.method == 'POST':
        current_step = int(request.form.get('current_step', 1))
        form_data = request.form.to_dict()
        
        if 'merchant_data' not in session:
            session['merchant_data'] = {}
        
        merchant_data = dict(session['merchant_data'])
        merchant_data.update(form_data)
        session['merchant_data'] = merchant_data
        
        print(f"[DEBUG] After updating session data at Step {current_step}: {session['merchant_data']}")

        if not validate_merchant_step(current_step, session['merchant_data']):
            flash('Please fill in all required fields.', 'error')
            return render_template('merchant-signup.html', step=current_step, form_data=session['merchant_data'])

        try:
            if current_step == 2:
                email = session['merchant_data'].get('email')
                if check_email_exists(email):
                    flash('This email is already registered.', 'error')
                    return render_template('merchant-signup.html', step=current_step, form_data=session['merchant_data'])

            if current_step == 4:  # This was previously step 5
                if session['merchant_data'].get('password') != session['merchant_data'].get('confirmPassword'):
                    flash('Passwords do not match.', 'error')
                    return render_template('merchant-signup.html', step=current_step, form_data=session['merchant_data'])

                merchant_data = dict(session['merchant_data'])
                session.pop('merchant_data', None)
                merchant_id = save_merchant_data(merchant_data)
                flash(f'Registration successful! Your Merchant ID is {merchant_id}.', 'success')
                return redirect(url_for('merchant_signin'))

            next_step = current_step + 1
            return render_template('merchant-signup.html', step=next_step, form_data=session['merchant_data'])

        except Exception as e:
            print(f"Error: {e}")
            flash('An unexpected error occurred.', 'error')
            return render_template('merchant-signup.html', step=current_step, form_data=session['merchant_data'])

    step = int(request.args.get('step', 1))
    return render_template('merchant-signup.html', step=step, form_data=session.get('merchant_data', {}))
