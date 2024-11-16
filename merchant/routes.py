from flask import render_template, request, redirect, url_for, flash
from . import merchant_bp  # Import the Blueprint from __init__.py
from .data import SAMPLE_LOANS, BANKS  # Import the data


@merchant_bp.route('/merchant-dashboard')
def merchant_dashboard():
    return render_template('merchant-dashboard.html', loans=SAMPLE_LOANS, banks=BANKS)


@merchant_bp.route('/submit-loan', methods=['POST'])
def submit_loan():
    bank = request.form.get('bank')
    # Add processing logic here
    flash('Loan application submitted successfully!', 'success')
    return redirect(url_for('merchant.merchant_dashboard'))
