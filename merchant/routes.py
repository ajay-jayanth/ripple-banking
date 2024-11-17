from flask import render_template, request, redirect, url_for, flash
from . import merchant_bp  # Import the Blueprint from __init__.py
import csv
from datetime import datetime
from .data import read_loans, read_banks
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@merchant_bp.route('/merchant-dashboard', methods=['GET', 'POST'])
def merchant_dashboard():
    # Read loans and banks
    loans = read_loans()  # Assuming read_loans() returns loan data
    banks = read_banks()  # Assuming read_banks() returns bank data

    # Check if there is any loan with the status 'current'
    has_current_loan = any(loan['status'] == 'current' for loan in loans)

    return render_template('merchant-dashboard.html', loans=loans, banks=banks, has_current_loan=has_current_loan)


@merchant_bp.route('/submit-loan', methods=['POST'])
def submit_loan():
    # Get data from the form
    bank = request.form.get('bank')
    amount = request.form.get('amount')

    # Format the amount (remove any commas if they exist)
    amount = amount.replace(",", "")  # Remove commas from the amount
    amount = int(amount)  # Convert to integer

    # Get the current date
    current_date = datetime.today().strftime('%Y-%m-%d')

    # Append new loan to the CSV file
    loan_data = {
        "bank": bank,
        "status": "current",  # Set the loan status as 'current' for the new loan
        "date": current_date,
        "amount": amount
    }

    # Write the new loan to the CSV file
    loans_file_path = os.path.join(
        BASE_DIR, '..', 'static', 'data', 'loans.csv')

    # Open the loans file in append mode
    with open(loans_file_path, mode='a', newline='') as file:
        fieldnames = ['bank', 'status', 'date', 'amount']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the new loan record
        writer.writerow(loan_data)

    # Flash success message
    flash('Loan application submitted successfully!', 'success')

    # Redirect back to the dashboard
    return redirect(url_for('merchant.merchant_dashboard'))
