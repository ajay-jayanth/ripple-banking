from flask import render_template, request, redirect, url_for, flash
from . import merchant_bp  # Import the Blueprint from __init__.py
# Import functions to read data from CSV
from .data import read_loans, read_banks


@merchant_bp.route('/merchant-dashboard')
def merchant_dashboard():
    # Fetch data from CSV files
    loans = read_loans()
    banks = read_banks()
    return render_template('merchant-dashboard.html', loans=loans, banks=banks)


@merchant_bp.route('/submit-loan', methods=['POST'])
def submit_loan():
    bank = request.form.get('bank')
    # Add processing logic here (e.g., save new loan)
    flash('Loan application submitted successfully!', 'success')
    return redirect(url_for('merchant.merchant_dashboard'))
