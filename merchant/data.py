import csv


import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def format_currency(amount):
    """Format the amount as currency, e.g., $30,000"""
    return f"${amount:,.0f}"  # This will format the amount with commas for thousands


def read_loans():
    """Read loan data from loans.csv"""
    loans = []
    loans_file_path = os.path.join(
        BASE_DIR, '..', 'static', 'data', 'loans.csv')  # Create absolute path
    with open(loans_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            loans.append({
                "bank": row['bank'],
                "status": row['status'],
                "date": row['date'],
                # Format the amount as currency
                "amount": format_currency(int(row['amount']))
            })
    return loans


def read_banks():
    """Read bank data from banks.csv"""
    banks = []
    with open('static/data/banks.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            banks.append(row[0])  # Only one column in this file
    return banks
