from datetime import date
from src.tracker import ExpenseTracker

def read_amount(prompt):
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("Enter a valid number.")

def main():
    tracker = ExpenseTracker()
    while True:
        print("\\n=== PERSONAL EXPENSE TRACKER ===")
        print("1. Add expense\\n2. View expenses\\n3. Monthly summary\\n4. Set category budget\\n5. Exit")
        choice = input("Choose (1-5): ").strip()
        try:
            if choice == "1":
                day = input(f"Date YYYY-MM-DD [{date.today().isoformat()}]: ").strip() or date.today().isoformat()
                record = tracker.add_expense(day, input("Category: "), read_amount("Amount (INR): "), input("Description: "))
                print(f"Saved expense #{record['id']}.")
            elif choice == "2":
                rows = tracker.list_expenses()
                if not rows:
                    print("No expenses recorded.")
                for r in rows:
                    print(f"#{r['id']} | {r['date']} | {r['category']} | INR {float(r['amount']):.2f} | {r['description']}")
            elif choice == "3":
                month = input("Month YYYY-MM: ").strip()
                summary = tracker.monthly_summary(month)
                print(f"\\n{month}: {summary['expense_count']} expenses; total INR {summary['total']:.2f}")
                for category, total in summary["by_category"].items():
                    print(f"  {category}: INR {total:.2f}")
                for category, status in tracker.budget_status(month).items():
                    print(f"  Budget {category}: {status['status']} (remaining INR {status['remaining']:.2f})")
            elif choice == "4":
                tracker.set_budget(input("Category: "), read_amount("Monthly budget (INR): "))
                print("Budget saved.")
            elif choice == "5":
                print("Your data is saved locally. Goodbye!")
                break
            else:
                print("Choose a number from 1 to 5.")
        except (ValueError, OSError) as error:
            print(f"Error: {error}")

if __name__ == "__main__":
    main()
