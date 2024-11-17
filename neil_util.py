import pandas as pd
import json
from datetime import datetime

def format_currency(amount):
    """Format the amount as currency, e.g., $30,000"""
    return f"${amount:,.0f}"

def load_data():
    # Load CSV files
    loans_df = pd.read_csv('static/data/merchant_loans.csv')
    applications_df = pd.read_csv('static/data/customer_applications.csv')
    return loans_df, applications_df

def calculate_risk_indicators(customer):
    # Calculate risk indicators (this could be expanded with more sophisticated logic)
    indicators = {
        'credit_score': {
            'value': customer['credit_score'],
            'status': 'good' if customer['credit_score'] >= 700 else 'moderate' if customer['credit_score'] >= 650 else 'poor'
        },
        'debt_to_income': {
            'value': round((customer['requested_amount'] / (customer['monthly_income'] * 12)) * 100, 1),
            'status': 'good' if (customer['requested_amount'] / (customer['monthly_income'] * 12)) < 0.3 else 'moderate'
        },
        'risk_score': {
            'value': customer['risk_score'],
            'status': 'good' if customer['risk_score'] >= 75 else 'moderate' if customer['risk_score'] >= 65 else 'poor'
        }
    }
    return indicators