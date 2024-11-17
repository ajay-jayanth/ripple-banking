from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import pandas as pd
from neil_util import format_currency, load_data, calculate_risk_indicators
from auth_utils import (
    customer_signin_fn,
    customer_signup_fn,
    merchant_signup_fn,
    merchant_signin_fn
)
from maps_utils import merchant_maps_fn
from merchant import merchant_bp  # Import the merchant blueprint
import random
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER_SECRET_LOL'
app.register_blueprint(merchant_bp, url_prefix='/merchant')


@app.route('/')
def index():
    return render_template('landing-page.html')


from flask import render_template, session
import pandas as pd

@app.route('/merchant/loans')
def loan_overview():
    # Assuming you have the merchant ID stored in the session, e.g., session['merchant_id']
    current_merchant_id = session.get('merchant_id')

    # Load the data
    loans_df = pd.read_csv('static/data/merchant_loans.csv')
    customers_df = pd.read_csv('static/data/customer_applications.csv')

    # Filter loans by the current merchant's ID
    filtered_loans = loans_df[loans_df['merchant_id'] == current_merchant_id]

    # Merge loan data with customer information
    merged_data = filtered_loans.merge(
        customers_df[['customer_id', 'name', 'purpose']],
        on='customer_id',
        how='left'
    )

    # Convert merged data to a dictionary format for use in the template
    loans = merged_data.to_dict('records')
    return render_template('loan_overview.html', loans=loans)



@app.route('/merchant/dashboard')
def dashboard():
    # Check if merchant is logged in
    if 'merchant_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('merchant_signin'))

    # Get the logged-in merchant ID
    merchant_id = session.get('merchant_id')

    # Load the bank loan data
    bank_loan_df = pd.read_csv('static/data/loans.csv')

    # Filter loans for the logged-in merchant
    merchant_loans_df = bank_loan_df[bank_loan_df['merchant_id'] == merchant_id]
    
    # Check if there are any current loans
    has_current_loan = any(merchant_loans_df['status'] == 'current')

    # Convert merchant-specific loans to dictionary for rendering
    loans = merchant_loans_df.to_dict('records')

    # List of available banks (excluding those with current loans)
    available_banks = ['Goldman Sachs', 'Bank of America', 'Capital One', 'Chase', 'Citi']

    if not has_current_loan:
        # If no current loans, show merchant-dashboard with loan history
        return render_template('merchant-dashboard.html', 
                            loans=loans,
                            banks=available_banks,
                            has_current_loan=has_current_loan)

    # If there is a current loan, load additional metrics for the full dashboard
    loans_df, applications_df = load_data()
    
    # Filter the loans_df to only include loans for the logged-in merchant
    loans_df = loans_df[loans_df['merchant_id'] == merchant_id]

    # Filter the active loan for the logged-in merchant
    active_loan = merchant_loans_df[merchant_loans_df['status'] == 'current'].iloc[-1]
    formatted_date = pd.to_datetime(active_loan['date']).strftime('%b %d, %Y')

    # Calculate merchant lending metrics for this merchant
    total_loaned = loans_df['loan_amount'].sum()
    total_remaining = loans_df['remaining_amount'].sum()
    active_loans = len(loans_df[loans_df['status'] == 'active'])

    loan_history = loans_df.to_dict('records')
    pending_applications = applications_df.to_dict('records')
    avg_credit_score = applications_df['credit_score'].mean()
    avg_requested_amount = applications_df['requested_amount'].mean()

    # Calculate metrics for pending applications for this merchant
    # merchant_applications_df = applications_df[applications_df['merchant_id'] == merchant_id]
    # pending_applications = merchant_applications_df.to_dict('records')
    # avg_credit_score = merchant_applications_df['credit_score'].mean()
    # avg_requested_amount = merchant_applications_df['requested_amount'].mean()

    return render_template('dashboard.html',
                         bank=active_loan['bank'],
                         status=active_loan['status'].capitalize(),
                         date=formatted_date,
                         amount=format_currency(active_loan['amount']),
                         total_loaned=total_loaned,
                         total_remaining=total_remaining,
                         active_loans=active_loans,
                         loan_history=loan_history,
                         pending_applications=pending_applications,
                         avg_credit_score=avg_credit_score,
                         avg_requested_amount=avg_requested_amount,
                         loans=loans,
                         banks=available_banks,
                         has_current_loan=has_current_loan)



@app.route('/loan/<customer_id>')
def loan_details(customer_id):
    # Load customer data from CSV
    import pandas as pd
    df = pd.read_csv('static/data/customer_applications.csv')
    customer = df[df['customer_id'] == int(customer_id)].to_dict(orient='records')
    
    if not customer:
        return "Customer not found", 404

    customer = customer[0]  # Get the first (and only) record as a dict
    return render_template('loan_details.html', customer=customer)

@app.route('/api/customer/<customer_id>')
def get_customer_details(customer_id):
    _, applications_df = load_data()
    # Convert customer_id to integer for comparison
    customer_data = applications_df[applications_df['customer_id'] == int(
        customer_id)]

    if customer_data.empty:
        return jsonify({'error': 'Customer not found'}), 404

    customer = customer_data.to_dict('records')[0]

    # Add risk indicators
    customer['risk_indicators'] = calculate_risk_indicators(customer)

    return jsonify(customer)


@app.route('/customer/merchant-map', methods=['GET'])  # On Customer Side
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

@app.route('/customer/loan-application')
def request_loan_page():
    df = pd.read_csv('merchants.csv').set_index('first_name')
    row = df.loc[session['merchant_name'].split()[0]]
    return render_template(
        'loan-application.html',
        merchant_name=session['merchant_name'],
        merchant_id=session['merchant_id'],
        business_name=session['business_name'],
        email=session['email'],
        rating=str(session['rating']),
        risk_score=str(session['risk_score']),
        image_path=row['file']
    )

@app.route('/save-merchant-session', methods=['POST'])
def save_merchant_session():
    data = request.json
    session['merchant_name'] = data['name']
    df = pd.read_csv('merchants.csv').set_index('first_name')
    row = df.loc[session['merchant_name'].split()[0]]
    session['merchant_id'] = row['merchant_id']
    session['business_name'] = row['business_name']
    session['email'] = row['email']
    session['rating'] = float(row['rating'])
    session['risk_score'] = int(row.get('risk_score', 65))
    return redirect(url_for('request_loan_page'))

@app.route('/customer/customer-loans', methods=['POST'])
def customer_loans():
    if request.method == 'POST':
        # Validate required form fields
        if 'amount' not in request.form or 'purpose' not in request.form:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('customer_loans'))
        
        try:
            CUST_APP_CSV = 'static/data/customer_applications.csv'
            df = pd.read_csv(CUST_APP_CSV)

            customers_df = pd.read_csv('customers.csv').set_index('first_name')
            cust_row = customers_df.loc[session['first_name']]
            ph_number = str(cust_row['phone'])
            ph_number = f'({ph_number[:3]}) {ph_number[3:6]}-{ph_number[-4:]}'
            email = cust_row['email']

            
            # Convert and validate amount
            try:
                loan_amount = float(request.form['amount'])
                if loan_amount <= 0:
                    raise ValueError("Loan amount must be positive")
            except ValueError as e:
                flash(f'Invalid loan amount: {str(e)}', 'error')
                return redirect(url_for('request_loan_page'))
            
            # Generate realistic random values
            monthly_income = max(loan_amount + random.randint(700, 3000), 2000)  # Ensure minimum income
            debt_amount = min(loan_amount + random.randint(0, 1000), monthly_income * 0.8)  # Cap debt at 80% of income
            
            # Validate session data
            if 'customer_id' not in session or 'first_name' not in session or 'last_name' not in session:
                flash('Please log in to submit a loan application.', 'error')
                return redirect(url_for('customer_signin'))
            
            # Create new application with validated data
            new_application = {
                'customer_id': int(random.randint(15, 10000)),
                'name': f"{session['first_name']} {session['last_name']}",
                'credit_score': random.randint(600, 850),
                'monthly_income': monthly_income,
                'requested_amount': loan_amount,
                'purpose': request.form['purpose'],
                'application_date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'status': 'pending',
                'risk_score': random.randint(45, 95),
                'total_debts': debt_amount,
                'dti_ratio': round(debt_amount / monthly_income * 100, 2),  # Convert to percentage
                'lti_ratio': round(loan_amount / monthly_income * 100, 2),  # Convert to percentage
                'payment_history_score': random.randint(45, 95),
                'credit_history_years': random.randint(0, 30),
                'recent_credit_inquiries': random.randint(0, 6),
                'existing_debts': float(debt_amount + random.randint(1500, 6000)),
                'savings_and_assets': float(monthly_income + random.randint(-1000, 3000)),
                'employment_stability_years': random.randint(1, 10),
                'phone_number': ph_number,
                'email': email
            }
            session['loan_title'] = f'{new_application["purpose"]} Loan'
            session['amount'] = f'{loan_amount:,.2f}'
            session['monthly_payment'] = f'{loan_amount/12:,.2f}'
            try:
                df = pd.concat([df, pd.DataFrame([new_application])], ignore_index=True)
                df.to_csv(CUST_APP_CSV, index=False)
                flash('Loan application submitted successfully!', 'success')
            except Exception as e:
                flash(f'Error saving application: {str(e)}', 'error')
                return redirect(url_for('request_loan_page'))

        except Exception as e:
            print(e)
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('request_loan_page'))

        return redirect(url_for('my_loans'))

@app.route('/customer/my_loans')
def my_loans():
    return render_template(
        'customer-loans.html',
    )

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000)
