import json
import csv
from typing import List, Dict, Callable
from datetime import datetime
import os
from typing import List, Dict
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Utility functions
def ensure_files_exist():
    """Ensure that necessary files exist with initial content."""
    for filename, default_content in [("transactions.json", []), ("budgets.json", {})]:
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            with open(path, "w") as file:
                json.dump(default_content, file)
            print(f"Created '{filename}' with initial content.")

def load_data(file_name: str) -> List or Dict:
    """Load JSON data from file."""
    path = os.path.join(BASE_DIR, file_name)
    with open(path, "r") as file:
        return json.load(file)

def save_data(file_name: str, data: List or Dict):
    """Save JSON data to file."""
    path = os.path.join(BASE_DIR, file_name)
    with open(path, "w") as file:
        json.dump(data, file, indent=4)

def input_transaction() -> Dict:
    """Input a transaction and return it as a dictionary."""
    return {
        "amount": float(input("Enter transaction amount: ")),
        "category": input("Enter transaction category: "),
        "type": input("Enter transaction type (income/expense): "),
        "date": input("Enter date (YYYY-MM-DD) or press Enter for today: ") or datetime.now().strftime('%Y-%m-%d'),
    }

def add_transaction(transactions: List[Dict], transaction: Dict) -> List[Dict]:
    """Add a new transaction to the transactions list."""
    return transactions + [transaction]

def set_budget(budgets: Dict) -> Callable:
    """Return a function to add/update a budget."""
    def add_budget(category: str, amount: float) -> Dict:
        budgets[category] = amount
        return budgets
    return add_budget

def calculate_budget_utilization(transactions: List[Dict], budgets: Dict) -> Dict:
    """Calculate spending for each budget category."""
    def is_expense_in_budget(transaction):
        return transaction['type'] == 'expense' and transaction['category'] in budgets

    # Use filter to keep relevant transactions, and reduce to aggregate totals
    expenses = filter(is_expense_in_budget, transactions)
    utilization = {}
    for transaction in expenses:
        utilization[transaction['category']] = utilization.get(transaction['category'], 0) + transaction['amount']
    return utilization

def summarize_spending(transactions: List[Dict]):
    """Summarize spending by category."""
    def is_expense(transaction):
        return transaction['type'] == 'expense'

    expenses = filter(is_expense, transactions)
    spending = {}
    for transaction in expenses:
        spending[transaction['category']] = spending.get(transaction['category'], 0) + transaction['amount']
    return spending

def savings_target(goal: float, months: int) -> float:
    """Calculate monthly savings needed."""
    return goal / months

def analyze_trends(transactions: List[Dict], current_month: int, previous_month: int) -> Dict:
    """Analyze trends between two months."""
    get_month = lambda t: int(t['date'].split('-')[1])
    current_spending = sum(t['amount'] for t in transactions if get_month(t) == current_month)
    previous_spending = sum(t['amount'] for t in transactions if get_month(t) == previous_month)
    return {"current": current_spending, "previous": previous_spending}

# Menu-driven system using Higher-Order Functions
def menu_loop():
    """Main menu loop."""
    ensure_files_exist()
    transactions = load_data("transactions.json")
    budgets = load_data("budgets.json")
    update_budget = set_budget(budgets)  # Higher-order function to set budget

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
        
        if choice == "1":
            transaction = input_transaction()
            transactions = add_transaction(transactions, transaction)
            print("Transaction recorded successfully.")

        elif choice == "2":
            category = input("Enter category: ")
            amount = float(input("Enter budget amount: "))
            update_budget(category, amount)  # Call the higher-order function
            print("Budget set successfully.")

        elif choice == "3":
            utilization = calculate_budget_utilization(transactions, budgets)
            for category, spent in utilization.items():
                print(f"{category}: Spent {spent}, Budget {budgets.get(category, 'Not Set')}")

        elif choice == "4":
            goal = float(input("Enter savings goal: "))
            months = int(input("Enter number of months: "))
            print(f"You need to save {savings_target(goal, months):.2f} per month.")

        elif choice == "5":
            spending = summarize_spending(transactions)
            print("Spending Summary:")
            for category, amount in spending.items():
                print(f"{category}: {amount}")
            print(f"Total Spent: {sum(spending.values())}")

        elif choice == "6":
            current_month = int(input("Enter current month (1-12): "))
            previous_month = int(input("Enter previous month (1-12): "))
            trends = analyze_trends(transactions, current_month, previous_month)
            print(f"Current Month: {trends['current']}, Previous Month: {trends['previous']}")

        elif choice == "7":
            save_data("transactions.json", transactions)
            save_data("budgets.json", budgets)
            print("Data saved successfully. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    menu_loop()
