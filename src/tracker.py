"""Expense tracking, budgeting, searching, and CSV export."""
import csv, json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

FIELDS = ["id", "date", "category", "amount", "description"]
CENT = Decimal("0.01")

class ExpenseTracker:
    """Manage local expenses in CSV and category budgets in JSON."""
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
        value = str(value).strip()
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
            if parsed.strftime("%Y-%m-%d") != value: raise ValueError
            return parsed.date().isoformat()
        except ValueError as exc:
            raise ValueError("Date must be a real date in YYYY-MM-DD format.") from exc

    @staticmethod
    def _month(value):
        value = str(value).strip()
        try:
            parsed = datetime.strptime(value, "%Y-%m")
            if parsed.strftime("%Y-%m") != value: raise ValueError
            return parsed.strftime("%Y-%m")
        except ValueError as exc:
            raise ValueError("Month must use YYYY-MM format.") from exc

    @staticmethod
    def _amount(value):
        try:
            amount = Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("Amount must be a valid number.") from exc
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        return amount

    @staticmethod
    def _category(value):
        category = str(value).strip().title()
        if not category: raise ValueError("Category cannot be empty.")
        return category

    def _read(self):
        with self.expenses_file.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _write(self, rows):
        with self.expenses_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def _read_budgets(self):
        try: data = json.loads(self.budgets_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Budget file is not valid JSON.") from exc
        if not isinstance(data, dict): raise ValueError("Budget file must contain a JSON object.")
        return data

    def add_expense(self, expense_date, category, amount, description):
        expense_date, category = self._date(expense_date), self._category(category)
        description = str(description).strip()
        if not description: raise ValueError("Description cannot be empty.")
        amount, rows = self._amount(amount), self._read()
        next_id = max((int(r["id"]) for r in rows), default=0) + 1
        record = {"id": str(next_id), "date": expense_date, "category": category,
                  "amount": f"{amount:.2f}", "description": description}
        with self.expenses_file.open("a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writerow(record)
        return record

    def list_expenses(self):
        return sorted(self._read(), key=lambda r: (r["date"], int(r["id"])), reverse=True)

    def get_expense(self, expense_id):
        for row in self._read():
            if row["id"] == str(expense_id): return row
        raise ValueError(f"Expense ID {expense_id} was not found.")

    def update_expense(self, expense_id, **changes):
        allowed = {"date", "category", "amount", "description"}
        unknown = set(changes) - allowed
        if unknown: raise ValueError(f"Unsupported fields: {', '.join(sorted(unknown))}")
        rows = self._read()
        for row in rows:
            if row["id"] == str(expense_id):
                if "date" in changes: row["date"] = self._date(changes["date"])
                if "category" in changes: row["category"] = self._category(changes["category"])
                if "amount" in changes: row["amount"] = f"{self._amount(changes['amount']):.2f}"
                if "description" in changes:
                    value = str(changes["description"]).strip()
                    if not value: raise ValueError("Description cannot be empty.")
                    row["description"] = value
                self._write(rows)
                return row
        raise ValueError(f"Expense ID {expense_id} was not found.")

    def delete_expense(self, expense_id):
        rows = self._read()
        remaining = [r for r in rows if r["id"] != str(expense_id)]
        if len(remaining) == len(rows): raise ValueError(f"Expense ID {expense_id} was not found.")
        self._write(remaining)

    def search_expenses(self, category=None, start_date=None, end_date=None, keyword=None):
        start = self._date(start_date) if start_date else None
        end = self._date(end_date) if end_date else None
        if start and end and start > end: raise ValueError("Start date cannot be after end date.")
        cat = self._category(category).casefold() if category else None
        word = str(keyword).strip().casefold() if keyword else None
        results = []
        for row in self.list_expenses():
            if cat and row["category"].casefold() != cat: continue
            if start and row["date"] < start: continue
            if end and row["date"] > end: continue
            if word and word not in row["description"].casefold(): continue
            results.append(row)
        return results

    def monthly_summary(self, year_month):
        month = self._month(year_month)
        selected = [r for r in self._read() if r["date"].startswith(month)]
        categories = defaultdict(Decimal)
        for row in selected: categories[row["category"]] += Decimal(row["amount"])
        return {"month": month, "expense_count": len(selected),
                "total": float(sum(categories.values(), Decimal("0.00")).quantize(CENT)),
                "by_category": {k: float(v.quantize(CENT)) for k, v in sorted(categories.items())}}

    def set_budget(self, category, monthly_limit):
        category, limit = self._category(category), self._amount(monthly_limit)
        budgets = self._read_budgets()
        budgets[category] = float(limit)
        self.budgets_file.write_text(json.dumps(budgets, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return budgets

    def budget_status(self, year_month):
        summary, budgets, result = self.monthly_summary(year_month), self._read_budgets(), {}
        for category, raw_limit in sorted(budgets.items()):
            limit = self._amount(raw_limit)
            spent = Decimal(str(summary["by_category"].get(category, 0.0)))
            remaining = (limit - spent).quantize(CENT)
            result[category] = {"limit": float(limit), "spent": float(spent),
                "remaining": float(remaining),
                "status": "Over budget" if remaining < 0 else "Within budget"}
        return result

    def export_csv(self, destination="expenses_export.csv"):
        path = Path(destination)
        if not path.is_absolute(): path = Path.cwd() / path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(self.list_expenses())
        return path
