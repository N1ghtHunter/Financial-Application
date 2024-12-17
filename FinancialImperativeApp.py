import json
import os
from datetime import datetime
from typing import List, Dict

# Global data stores
transactions = []
budgets = {}

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSACTIONS_FILE = os.path.join(BASE_DIR, "transactions.json")
BUDGETS_FILE = os.path.join(BASE_DIR, "budgets.json")

# File Management Functions
def ensure_files_exist():
    """Ensure that necessary data files exist with initial content."""
    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, "w") as file:
            json.dump([], file)  # Empty list for transactions
        print(f"Created '{TRANSACTIONS_FILE}' with initial empty data.")

    if not os.path.exists(BUDGETS_FILE):
        with open(BUDGETS_FILE, "w") as file:
            json.dump({}, file)  # Empty dictionary for budgets
        print(f"Created '{BUDGETS_FILE}' with initial empty data.")

def load_data():
    """Load transactions and budgets from files."""
    global transactions, budgets

    try:
        with open(TRANSACTIONS_FILE, "r") as file:
            transactions = json.load(file)
        print("Transactions loaded successfully.")
    except FileNotFoundError:
        transactions = []
        print("No transactions file found. Starting with an empty list.")

    try:
        with open(BUDGETS_FILE, "r") as file:
            budgets = json.load(file)
        print("Budgets loaded successfully.")
    except FileNotFoundError:
        budgets = {}
        print("No budgets file found. Starting with an empty dictionary.")

def save_data():
    """Save transactions and budgets to files."""
    with open(TRANSACTIONS_FILE, "w") as file:
        json.dump(transactions, file, indent=4)
    with open(BUDGETS_FILE, "w") as file:
        json.dump(budgets, file, indent=4)
    print("Data saved successfully. Goodbye!")

# Transaction Functions
def record_transaction():
    """Record a new transaction."""
    amount = float(input("Enter transaction amount: "))
    category = input("Enter transaction category: ")
    type_ = input("Enter transaction type (income/expense): ")
    date = input("Enter transaction date (YYYY-MM-DD) or press Enter for today: ")
    date = date or datetime.now().strftime('%Y-%m-%d')

    transactions.append({
        "amount": amount,
        "category": category,
        "type": type_,
        "date": date,
    })
    print("Transaction recorded successfully.")

def summarize_spending():
    """Summarize spending by category."""
    spending = {}
    for transaction in transactions:
        if transaction['type'] == 'expense':
            spending[transaction['category']] = spending.get(transaction['category'], 0) + transaction['amount']

    total_spent = sum(spending.values())
    print("Spending Summary:")
    for category, amount in spending.items():
        print(f"{category}: {amount}")
    print(f"Total Spent: {total_spent}")

def analyze_trends():
    """Analyze spending trends for the current and previous months."""
    current_month = int(input("Enter current month (1-12): "))
    previous_month = int(input("Enter previous month (1-12): "))

    current_spending = sum(
        t['amount'] for t in transactions if int(t['date'].split('-')[1]) == current_month and t['type'] == 'expense'
    )
    previous_spending = sum(
        t['amount'] for t in transactions if int(t['date'].split('-')[1]) == previous_month and t['type'] == 'expense'
    )
    print("Spending Trends:")
    print(f"Current Month: {current_spending}, Previous Month: {previous_spending}")

# Budget Functions
def set_budget():
    """Set a budget for a category."""
    category = input("Enter category to set budget for: ")
    amount = float(input("Enter budget amount: "))
    budgets[category] = amount
    print("Budget set successfully.")

def track_budget_utilization():
    """Track the budget utilization."""
    utilization = {category: 0 for category in budgets}
    for transaction in transactions:
        if transaction['type'] == 'expense' and transaction['category'] in budgets:
            utilization[transaction['category']] += transaction['amount']

    print("Budget Utilization:")
    for category, spent in utilization.items():
        print(f"{category}: Spent {spent}, Budget {budgets.get(category, 'Not Set')}")

def calculate_savings():
    """Calculate monthly savings target."""
    goal = float(input("Enter savings goal: "))
    months = int(input("Enter number of months: "))
    monthly_savings = goal / months
    print(f"You need to save {monthly_savings:.2f} per month.")

# Main Application Loop
def main():
    """Main function to run the financial app."""
    ensure_files_exist()
    load_data()

    while True:
        print("\nMenu:")
        print("1. Record a transaction")
        print("2. Set a budget")
        print("3. Track budget utilization")
        print("4. Calculate savings target")
        print("5. Summarize spending")
        print("6. Analyze trends")
        print("7. Save and Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            record_transaction()
        elif choice == '2':
            set_budget()
        elif choice == '3':
            track_budget_utilization()
        elif choice == '4':
            calculate_savings()
        elif choice == '5':
            summarize_spending()
        elif choice == '6':
            analyze_trends()
        elif choice == '7':
            save_data()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
