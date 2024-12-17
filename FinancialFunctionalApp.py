import json
import os
import time
import csv
from typing import List, Dict, Callable
from datetime import datetime
from functools import reduce

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSACTIONS_FILE = os.path.join(BASE_DIR, "transactions.json")
BUDGETS_FILE = os.path.join(BASE_DIR, "budgets.json")
SAVINGS_FILE = os.path.join(BASE_DIR, "savings.json")
ALERT_THRESHOLD = 0.9  # 90% of the budget

# Utility Functions
def ensure_files_exist():
    """Ensure that necessary files exist with initial content."""
    files = [
        (TRANSACTIONS_FILE, []),
        (BUDGETS_FILE, {}),
        (SAVINGS_FILE, {})
    ]
    def ensure_rec(index=0):
        if index >= len(files):
            return
        path, default_content = files[index]
        if not os.path.exists(path):
            with open(path, "w") as file:
                json.dump(default_content, file)
        ensure_rec(index + 1)
    ensure_rec()

def load_data(file_path: str) -> List or Dict:
    """Load JSON data from file."""
    with open(file_path, "r") as file:
        return json.load(file)

def save_data(file_path: str, data: List or Dict):
    """Save JSON data to file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Functional Helpers
def filter_transactions(transactions: List[Dict], predicate: Callable[[Dict], bool]) -> List[Dict]:
    return list(filter(predicate, transactions))

def map_transactions(transactions: List[Dict], mapper: Callable[[Dict], float]) -> List[float]:
    return list(map(mapper, transactions))

def reduce_transactions(values: List[float], reducer: Callable[[float, float], float], initial: float = 0) -> float:
    return reduce(reducer, values, initial)

# Budget Functions
def calculate_budget_utilization(transactions: List[Dict], budgets: Dict) -> Dict:
    expenses = filter_transactions(transactions, lambda t: t["type"] == "expense")
    def calculate_utilization(expenses_list, utilization=None):
        if utilization is None:
            utilization = {}
        if not expenses_list:
            return utilization
        txn = expenses_list[0]
        category = txn["category"]
        if category in budgets:
            utilization[category] = utilization.get(category, 0) + txn["amount"]
        return calculate_utilization(expenses_list[1:], utilization)

    return calculate_utilization(expenses)

def check_budget_alerts(transactions: List[Dict], budgets: Dict):
    utilization = calculate_budget_utilization(transactions, budgets)
    def check_alerts(alert_list):
        if not alert_list:
            return
        category, spent = alert_list[0]
        if spent / budgets[category] >= ALERT_THRESHOLD:
            print(f"\n⚠️ ALERT: '{category}' is at {spent / budgets[category]:.0%} of the budget! Spent: {spent}, Limit: {budgets[category]}")
        check_alerts(alert_list[1:])

    check_alerts(list(utilization.items()))

# Summarize Spending
def summarize_spending(transactions: List[Dict]):
    expenses = filter_transactions(transactions, lambda t: t["type"] == "expense")
    def calculate_totals(expenses_list, totals=None):
        if totals is None:
            totals = {}
        if not expenses_list:
            return totals
        txn = expenses_list[0]
        totals[txn["category"]] = totals.get(txn["category"], 0) + txn["amount"]
        return calculate_totals(expenses_list[1:], totals)

    category_totals = calculate_totals(expenses)
    total_spent = sum(category_totals.values())

    print("\nSpending Summary:")
    def print_summary(categories):
        if not categories:
            return
        category, amount = categories[0]
        print(f"  - {category}: ${amount:.2f}")
        print_summary(categories[1:])

    print_summary(list(category_totals.items()))
    print(f"Total Spending: ${total_spent:.2f}")

# Savings Functions
def set_savings_goal():
    savings = load_data(SAVINGS_FILE)
    goal = float(input("Enter savings goal amount: "))
    savings = {**savings, "goal": goal, "recommended_monthly": goal / 12, "current_savings": savings.get("current_savings", 0)}
    save_data(SAVINGS_FILE, savings)
    print(f"Savings goal of ${goal:.2f} set. You should save ${goal / 12:.2f} per month.")

def update_savings(amount: float):
    savings = load_data(SAVINGS_FILE)
    current_savings = savings.get("current_savings", 0) + amount
    savings = {**savings, "current_savings": current_savings}
    save_data(SAVINGS_FILE, savings)
    print(f"${amount:.2f} added to savings. Current savings: ${current_savings:.2f}")
    if current_savings >= savings["goal"]:
        print("🎉 Congratulations! You've achieved your savings goal!")

# Import and Export
def import_transactions(file_path: str):
    transactions = load_data(TRANSACTIONS_FILE)
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        new_transactions = [{
            "amount": float(row["amount"]),
            "category": row["category"],
            "type": row["type"],
            "date": row["date"]
        } for row in reader]
    save_data(TRANSACTIONS_FILE, transactions + new_transactions)
    print(f"Transactions imported successfully from {file_path}.")

def export_transactions():
    transactions = load_data(TRANSACTIONS_FILE)
    export_file = os.path.join(BASE_DIR, "transactions_export.json")
    save_data(export_file, transactions)
    print(f"Transactions exported to {export_file}.")

# Menu System
def menu_loop():
    ensure_files_exist()
    def loop():
        print("\n--- Budget Tracker ---")
        print("1. Record a transaction")
        print("2. Set a budget")
        print("3. Start budget monitoring")
        print("4. View spending summary")
        print("5. Set a savings goal")
        print("6. Update savings progress")
        print("7. Import transactions (CSV)")
        print("8. Export transactions")
        print("9. Exit")

        choice = input("Enter your choice: ")
        transactions = load_data(TRANSACTIONS_FILE)
        budgets = load_data(BUDGETS_FILE)
        
        if choice == "1":
            txn = {
                "amount": float(input("Enter amount: ")),
                "category": input("Enter category: "),
                "type": input("Enter type (income/expense): "),
                "date": input("Enter date (YYYY-MM-DD): ") or datetime.now().strftime('%Y-%m-%d')
            }
            save_data(TRANSACTIONS_FILE, transactions + [txn])
            print("Transaction recorded successfully.")
            check_budget_alerts(transactions + [txn], budgets)
        elif choice == "2":
            budgets = {**budgets, input("Enter category: "): float(input("Enter amount: "))}
            save_data(BUDGETS_FILE, budgets)
            print("Budget updated.")
        elif choice == "3":
            check_budget_alerts(transactions, budgets)
        elif choice == "4":
            summarize_spending(transactions)
        elif choice == "5":
            set_savings_goal()
        elif choice == "6":
            update_savings(float(input("Enter savings amount: ")))
        elif choice == "7":
            import_transactions(input("Enter CSV file path: "))
        elif choice == "8":
            export_transactions()
        elif choice == "9":
            print("Goodbye!")
            return
        else:
            print("Invalid choice, please try again.")
        loop()
    loop()

if __name__ == "__main__":
    menu_loop()
