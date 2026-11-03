import tempfile
import unittest
from pathlib import Path
from src.tracker import ExpenseTracker

class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tracker = ExpenseTracker(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def test_add_and_list_expense(self):
        item = self.tracker.add_expense("2026-11-03", "food", 120, "Lunch")
        self.assertEqual(item["category"], "Food")
        self.assertEqual(self.tracker.list_expenses()[0]["description"], "Lunch")
    def test_monthly_summary(self):
        self.tracker.add_expense("2026-11-01", "Food", 100, "Breakfast")
        self.tracker.add_expense("2026-11-02", "Travel", 50, "Bus")
        result = self.tracker.monthly_summary("2026-11")
        self.assertEqual(result["total"], 150.0)
        self.assertEqual(result["expense_count"], 2)
    def test_reject_zero_and_negative_amounts(self):
        for amount in (0, -1):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.tracker.add_expense("2026-11-03", "Food", amount, "Invalid")
    def test_reject_invalid_date(self):
        with self.assertRaises(ValueError):
            self.tracker.add_expense("2026-02-30", "Food", 10, "Invalid")
    def test_reject_empty_fields(self):
        with self.assertRaises(ValueError):
            self.tracker.add_expense("2026-11-03", " ", 10, "Lunch")
        with self.assertRaises(ValueError):
            self.tracker.add_expense("2026-11-03", "Food", 10, " ")
    def test_budget_overrun(self):
        self.tracker.set_budget("Food", 100)
        self.tracker.add_expense("2026-11-03", "Food", 125, "Lunch")
        status = self.tracker.budget_status("2026-11")["Food"]
        self.assertEqual(status["status"], "Over budget")
        self.assertEqual(status["remaining"], -25.0)
    def test_update_expense(self):
        item = self.tracker.add_expense("2026-11-03", "Food", 100, "Lunch")
        updated = self.tracker.update_expense(item["id"], amount=150, category="Dining")
        self.assertEqual(updated["category"], "Dining")
        self.assertEqual(float(updated["amount"]), 150.0)
    def test_delete_expense(self):
        item = self.tracker.add_expense("2026-11-03", "Food", 100, "Lunch")
        self.tracker.delete_expense(item["id"])
        self.assertEqual(self.tracker.list_expenses(), [])
    def test_search(self):
        self.tracker.add_expense("2026-11-03", "Food", 100, "Lunch at cafe")
        self.tracker.add_expense("2026-11-03", "Travel", 50, "Bus ticket")
        self.assertEqual(len(self.tracker.search_expenses(category="food", keyword="CAFE")), 1)
    def test_export_csv(self):
        self.tracker.add_expense("2026-11-03", "Food", 100, "Lunch")
        path = self.tracker.export_csv(Path(self.temp.name) / "export.csv")
        self.assertIn("Lunch", path.read_text(encoding="utf-8-sig"))
    def test_missing_expense(self):
        with self.assertRaises(ValueError): self.tracker.delete_expense("999")
    def test_invalid_month(self):
        with self.assertRaises(ValueError): self.tracker.monthly_summary("2026-13")

if __name__ == "__main__":
    unittest.main()
