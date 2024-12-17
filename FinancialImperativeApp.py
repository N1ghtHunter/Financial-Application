import json
import os
import csv
from datetime import datetime

class BudgetTracker:
    def __init__(self):
        # Mutable global state
        self.transactions = []
        self.budgets = {}
        self.savings = {
            'goal': 0,
            'current_savings': 0,
            'recommended_monthly': 0
        }
        
        # Configuration
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.TRANSACTIONS_FILE = os.path.join(self.BASE_DIR, "transactions.json")
        self.BUDGETS_FILE = os.path.join(self.BASE_DIR, "budgets.json")
        self.SAVINGS_FILE = os.path.join(self.BASE_DIR, "savings.json")
        self.ALERT_THRESHOLD = 0.9  # 90% of the budget

    def load_state(self):
        """Load mutable state from files."""
        try:
            with open(self.TRANSACTIONS_FILE, 'r') as f:
                self.transactions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.transactions = []

        try:
            with open(self.BUDGETS_FILE, 'r') as f:
                self.budgets = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.budgets = {}

        try:
            with open(self.SAVINGS_FILE, 'r') as f:
                self.savings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.savings = {
                'goal': 0,
                'current_savings': 0,
                'recommended_monthly': 0
            }

    def save_state(self):
        """Save current mutable state to files."""
        with open(self.TRANSACTIONS_FILE, 'w') as f:
            json.dump(self.transactions, f, indent=4)

        with open(self.BUDGETS_FILE, 'w') as f:
            json.dump(self.budgets, f, indent=4)

        with open(self.SAVINGS_FILE, 'w') as f:
            json.dump(self.savings, f, indent=4)

    def record_transaction(self, amount, category, type, date=None):
        """Add a transaction with side effects."""
        transaction = {
            'amount': amount,
            'category': category,
            'type': type,
            'date': date or datetime.now().strftime('%Y-%m-%d')
        }
        self.transactions.append(transaction)
        self.save_state()
        self.check_budget_alerts()

    def set_budget(self, category, amount):
        """Set a budget with side effects."""
        self.budgets[category] = amount
        self.save_state()
        print(f"Budget for {category} set to ${amount}")

    def check_budget_alerts(self):
        """Check budget alerts with side effects."""
        category_spending = {}
        
        # Mutate spending tracker
        for transaction in self.transactions:
            if transaction['type'] == 'expense':
                category = transaction['category']
                if category not in category_spending:
                    category_spending[category] = 0
                category_spending[category] += transaction['amount']
        
        # Side effect: print alerts
        for category, spent in category_spending.items():
            if category in self.budgets:
                utilization = spent / self.budgets[category]
                if utilization >= self.ALERT_THRESHOLD:
                    print(f"⚠️ ALERT: '{category}' is at {utilization:.0%} of budget!")

    def summarize_spending(self):
        """Generate spending summary with side effects."""
        category_totals = {}
        total_spending = 0

        # Mutate totals
        for transaction in self.transactions:
            if transaction['type'] == 'expense':
                category = transaction['category']
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += transaction['amount']
                total_spending += transaction['amount']

        # Side effect: print summary
        print("\nSpending Summary:")
        for category, amount in category_totals.items():
            print(f"  - {category}: ${amount:.2f}")
        print(f"Total Spending: ${total_spending:.2f}")

    def set_savings_goal(self, goal):
        """Set savings goal with side effects."""
        self.savings['goal'] = goal
        self.savings['recommended_monthly'] = goal / 12
        self.save_state()
        print(f"Savings goal set to ${goal}. Recommended monthly savings: ${goal/12:.2f}")

    def update_savings(self, amount):
        """Update savings with side effects."""
        self.savings['current_savings'] += amount
        self.save_state()

        print(f"Added ${amount} to savings.")
        print(f"Current savings: ${self.savings['current_savings']}")

        # Side effect: achievement notification
        if self.savings['current_savings'] >= self.savings['goal']:
            print("🎉 Congratulations! You've achieved your savings goal!")

    def import_transactions(self, file_path):
        """Import transactions with side effects."""
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.record_transaction(
                    amount=float(row['amount']),
                    category=row['category'],
                    type=row['type'],
                    date=row['date']
                )
        print(f"Imported transactions from {file_path}")

    def run(self):
        """Main imperative control flow."""
        self.load_state()

        while True:
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
            choice = input("Choose an option: ")

            try:
                if choice == '1':
                    amount = float(input("Amount: "))
                    category = input("Category: ")
                    type = input("Type (income/expense): ")
                    self.record_transaction(amount, category, type)
                
                elif choice == '2':
                    category = input("Category: ")
                    amount = float(input("Budget Amount: "))
                    self.set_budget(category, amount)
                
                elif choice == '3':
                    self.check_budget_alerts()
                
                elif choice == '4':
                    self.summarize_spending()
                
                elif choice == '5':
                    goal = float(input("Savings Goal: "))
                    self.set_savings_goal(goal)
                
                elif choice == '6':
                    amount = float(input("Savings Amount: "))
                    self.update_savings(amount)
                
                elif choice == '7':
                    file_path = input("CSV File Path: ")
                    self.import_transactions(file_path)
                elif choice == '8':
                    print("Exporting transactions...")
                    self.save_state()
                    print("Transactions exported.")
                    
                elif choice == '9':
                    print("Exiting...")
                    break
                
                else:
                    print("Invalid option")

            except ValueError as e:
                print(f"Error: {e}")

def main():
    tracker = BudgetTracker()
    tracker.run()

if __name__ == "__main__":
    main()