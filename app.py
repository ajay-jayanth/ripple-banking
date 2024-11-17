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
    return render_template('loan-application.html')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3000)
