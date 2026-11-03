import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

FIELDS = ["id", "date", "category", "amount", "description"]

class ExpenseTracker:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.expenses_file = self.data_dir / "expenses.csv"
        self.budgets_file = self.data_dir / "budgets.json"
        if not self.expenses_file.exists():
            with self.expenses_file.open("w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=FIELDS).writeheader()
        if not self.budgets_file.exists():
            self.budgets_file.write_text("{}", encoding="utf-8")

    @staticmethod
    def _date(value):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
        except ValueError as exc:
            raise ValueError("Date must use YYYY-MM-DD format.") from exc

    @staticmethod
    def _amount(value):
        try:
            result = round(float(value), 2)
        except (TypeError, ValueError) as exc:
            raise ValueError("Amount must be a valid number.") from exc
        if result <= 0:
            raise ValueError("Amount must be greater than zero.")
        return result

    def _read(self):
        with self.expenses_file.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def add_expense(self, expense_date, category, amount, description):
        expense_date = self._date(expense_date)
        category = category.strip().title()
        description = description.strip()
        amount = self._amount(amount)
        if not category or not description:
            raise ValueError("Category and description cannot be empty.")
        rows = self._read()
        next_id = max((int(row["id"]) for row in rows), default=0) + 1
        record = {
            "id": str(next_id), "date": expense_date, "category": category,
            "amount": f"{amount:.2f}", "description": description
        }
        with self.expenses_file.open("a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writerow(record)
        return record

    def list_expenses(self):
        return sorted(self._read(), key=lambda r: (r["date"], int(r["id"])), reverse=True)

    def monthly_summary(self, year_month):
        try:
            datetime.strptime(year_month, "%Y-%m")
        except ValueError as exc:
            raise ValueError("Month must use YYYY-MM format.") from exc
        selected = [r for r in self._read() if r["date"].startswith(year_month)]
        categories = defaultdict(float)
        for row in selected:
            categories[row["category"]] += float(row["amount"])
        return {
            "month": year_month,
            "expense_count": len(selected),
            "total": round(sum(categories.values()), 2),
            "by_category": {k: round(v, 2) for k, v in sorted(categories.items())}
        }

    def set_budget(self, category, monthly_limit):
        category = category.strip().title()
        if not category:
            raise ValueError("Category cannot be empty.")
        limit = self._amount(monthly_limit)
        budgets = json.loads(self.budgets_file.read_text(encoding="utf-8"))
        budgets[category] = limit
        self.budgets_file.write_text(json.dumps(budgets, indent=2), encoding="utf-8")
        return budgets

    def budget_status(self, year_month):
        summary = self.monthly_summary(year_month)
        budgets = json.loads(self.budgets_file.read_text(encoding="utf-8"))
        result = {}
        for category, limit in sorted(budgets.items()):
            spent = summary["by_category"].get(category, 0.0)
            remaining = round(limit - spent, 2)
            result[category] = {
                "limit": limit, "spent": spent, "remaining": remaining,
                "status": "Over budget" if remaining < 0 else "Within budget"
            }
        return result
