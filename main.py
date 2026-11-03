"""Command-line interface for Atelier Expense Tracker."""
from datetime import date
from src.tracker import ExpenseTracker

def read_amount(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            if value <= 0: print("Amount must be greater than zero."); continue
            return value
        except ValueError:
            print("Enter a valid number, for example 250 or 125.50.")

def read_required(prompt):
    while True:
        value = input(prompt).strip()
        if value: return value
        print("This field cannot be empty.")

def print_expenses(rows):
    if not rows: print("No expenses found."); return
    print("\n{:<5} {:<12} {:<16} {:>12}  {}".format("ID", "DATE", "CATEGORY", "AMOUNT (INR)", "DESCRIPTION"))
    print("-" * 78)
    for r in rows:
        print("{:<5} {:<12} {:<16} {:>12.2f}  {}".format(r["id"], r["date"], r["category"], float(r["amount"]), r["description"]))

def main():
    tracker = ExpenseTracker()
    while True:
        print("\n=== ATELIER PERSONAL EXPENSE TRACKER ===")
        print("1. Add expense\n2. View all expenses\n3. Monthly summary and budget status")
        print("4. Set or update category budget\n5. Search expenses\n6. Edit an expense")
        print("7. Delete an expense\n8. Export expenses to CSV\n9. Exit")
        choice = input("Choose (1-9): ").strip()
        try:
            if choice == "1":
                day = input(f"Date YYYY-MM-DD [{date.today().isoformat()}]: ").strip() or date.today().isoformat()
                item = tracker.add_expense(day, read_required("Category: "), read_amount("Amount (INR): "), read_required("Description: "))
                print(f"Expense #{item['id']} saved.")
            elif choice == "2":
                print_expenses(tracker.list_expenses())
            elif choice == "3":
                month = read_required("Month YYYY-MM: ")
                summary = tracker.monthly_summary(month)
                print(f"\nSUMMARY FOR {month}\nExpenses: {summary['expense_count']}\nTotal: INR {summary['total']:.2f}")
                for category, total in summary["by_category"].items(): print(f"  {category}: INR {total:.2f}")
                statuses = tracker.budget_status(month)
                for category, s in statuses.items():
                    print(f"  {category}: {s['status']} | spent INR {s['spent']:.2f} / limit INR {s['limit']:.2f} | remaining INR {s['remaining']:.2f}")
                if not statuses: print("No category budgets configured.")
            elif choice == "4":
                category = read_required("Category: ")
                tracker.set_budget(category, read_amount("Monthly budget (INR): "))
                print(f"Budget for {category.title()} saved.")
            elif choice == "5":
                print("Leave filters blank to skip them.")
                cat = input("Category: ").strip() or None
                start = input("Start date YYYY-MM-DD: ").strip() or None
                end = input("End date YYYY-MM-DD: ").strip() or None
                keyword = input("Description contains: ").strip() or None
                print_expenses(tracker.search_expenses(cat, start, end, keyword))
            elif choice == "6":
                expense_id = input("Expense ID to edit: ").strip()
                print("Leave a field blank to keep its current value.")
                changes = {}
                for key, prompt in [("date", "New date YYYY-MM-DD: "), ("category", "New category: "), ("amount", "New amount INR: "), ("description", "New description: ")]:
                    value = input(prompt).strip()
                    if value: changes[key] = value
                if changes: tracker.update_expense(expense_id, **changes); print(f"Expense #{expense_id} updated.")
                else: print("No changes entered.")
            elif choice == "7":
                expense_id = input("Expense ID to delete: ").strip()
                if input(f"Delete expense #{expense_id}? Type yes to confirm: ").strip().lower() == "yes":
                    tracker.delete_expense(expense_id); print("Expense deleted.")
                else: print("Deletion cancelled.")
            elif choice == "8":
                name = input("Export filename [expenses_export.csv]: ").strip() or "expenses_export.csv"
                print(f"Exported to: {tracker.export_csv(name)}")
            elif choice == "9":
                print("Your data is saved locally. Goodbye!")
                break
            else: print("Choose a number from 1 to 9.")
        except (ValueError, OSError) as error:
            print(f"Could not complete that action: {error}")

if __name__ == "__main__":
    main()
