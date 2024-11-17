from flask import render_template, request, redirect, url_for, flash, session
from . import merchant_bp  # Import the Blueprint from __init__.py
import csv
from datetime import datetime
from .data import read_loans, read_banks
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@merchant_bp.route('/merchant-dashboard', methods=['GET', 'POST'])
def merchant_dashboard():
    # Check if merchant is logged in
    if 'merchant_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('merchant_signin'))
    
    # Get current merchant ID from session
    current_merchant_id = session.get('merchant_id')
    
    # Read loans CSV file
    loans_file_path = os.path.join(BASE_DIR, '..', 'static', 'data', 'loans.csv')
    loans_df = pd.read_csv(loans_file_path)
    
    # Filter loans for current merchant
    merchant_loans_df = loans_df[loans_df['merchant_id'] == current_merchant_id]
    loans = merchant_loans_df.to_dict('records')
    
    # Read banks data
    banks = read_banks()
    
    # Check if there is any loan with the status 'current' for this merchant
    has_current_loan = any((loan['status'] == 'current' and loan['merchant_id'] == current_merchant_id) for loan in loans)
    
    return render_template('merchant-dashboard.html', 
                         loans=loans, 
                         banks=banks, 
                         has_current_loan=has_current_loan)

@merchant_bp.route('/submit-loan', methods=['POST'])
def submit_loan():
    if 'merchant_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('merchant_signin'))
        
    # Get current merchant ID from session
    current_merchant_id = session.get('merchant_id')
    
    # Get data from the form
    bank = request.form.get('bank')
    amount = request.form.get('amount')

    # Format the amount (remove any commas if they exist)
    amount = amount.replace(",", "")  # Remove commas from the amount
    amount = int(amount)  # Convert to integer

    # Get the current date
    current_date = datetime.today().strftime('%Y-%m-%d')

    # Prepare loan data
    loan_data = {
        "merchant_id": current_merchant_id,
        "bank": bank,
        "status": "current",
        "date": current_date,
        "amount": amount
    }

    # Write the new loan to the CSV file
    loans_file_path = os.path.join(BASE_DIR, '..', 'static', 'data', 'loans.csv')
    
    # Open the loans file in append mode
    with open(loans_file_path, mode='a', newline='') as file:
        fieldnames = ['merchant_id', 'bank', 'status', 'date', 'amount']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(loan_data)

    # flash('Loan application submitted successfully!', 'success')
    return redirect(url_for('merchant.merchant_dashboard'))