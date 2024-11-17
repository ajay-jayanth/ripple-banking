from flask import Flask, render_template, jsonify
import pandas as pd
from neil_util import format_currency, load_data,calculate_risk_indicators
from merchant import merchant_bp  # Import the merchant blueprint


app = Flask(__name__)

app.register_blueprint(merchant_bp, url_prefix='/merchant')

@app.route('/loans')
def loan_overview():
    loans_df = pd.read_csv('static/data/merchant_loans.csv')
    customers_df = pd.read_csv('static/data/customer_applications.csv')
    
    # Merge loan data with customer information
    merged_data = loans_df.merge(
        customers_df[['customer_id', 'name', 'purpose']],
        on='customer_id',
        how='left'
    )
    
    loans = merged_data.to_dict('records')
    return render_template('loan_overview.html', loans=loans)

@app.route('/')
def dashboard():
    # Load all required data
    loans_df, applications_df = load_data()
    
    # Load the bank loan data
    bank_loan_df = pd.read_csv('static/data/loans.csv')
    # print(bank_loan_df)
    # Get the active bank loan (most recent active loan)
    active_loan = bank_loan_df[bank_loan_df['status'] == 'current'].iloc[-1]
    
    # Format the bank loan date
    formatted_date = pd.to_datetime(active_loan['date']).strftime('%b %d, %Y')
    
    # Calculate merchant lending metrics
    total_loaned = loans_df['loan_amount'].sum()
    total_remaining = loans_df['remaining_amount'].sum()
    active_loans = len(loans_df[loans_df['status'] == 'active'])
    
    # Prepare loan history data for chart
    loan_history = loans_df.to_dict('records')
    
    # Get pending applications
    pending_applications = applications_df.to_dict('records')
    
    # Calculate application statistics
    avg_credit_score = applications_df['credit_score'].mean()
    avg_requested_amount = applications_df['requested_amount'].mean()
    
    return render_template('dashboard.html',
                         # Bank loan data
                         bank=active_loan['bank'],
                         status=active_loan['status'].capitalize(),
                         date=formatted_date,
                         amount=format_currency(active_loan['amount']),
                         # Merchant lending metrics
                         total_loaned=total_loaned,
                         total_remaining=total_remaining,
                         active_loans=active_loans,
                         loan_history=loan_history,
                         # Application data
                         pending_applications=pending_applications,
                         avg_credit_score=avg_credit_score,
                         avg_requested_amount=avg_requested_amount)

@app.route('/api/customer/<customer_id>')
def get_customer_details(customer_id):
    _, applications_df = load_data()
    # Convert customer_id to integer for comparison
    customer_data = applications_df[applications_df['customer_id'] == int(customer_id)]
    
    if customer_data.empty:
        return jsonify({'error': 'Customer not found'}), 404
        
    customer = customer_data.to_dict('records')[0]
    
    # Add risk indicators
    customer['risk_indicators'] = calculate_risk_indicators(customer)
    
    return jsonify(customer)

if __name__ == '__main__':
    app.run(debug=True)