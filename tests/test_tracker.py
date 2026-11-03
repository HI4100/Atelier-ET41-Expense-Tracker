import tempfile
import unittest
from src.tracker import ExpenseTracker

class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tracker = ExpenseTracker(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_add_and_list(self):
        item = self.tracker.add_expense("2026-11-03", "food", 120, "Lunch")
        self.assertEqual(item["category"], "Food")
        self.assertEqual(self.tracker.list_expenses()[0]["description"], "Lunch")

    def test_monthly_summary(self):
        self.tracker.add_expense("2026-11-01", "Food", 100, "Breakfast")
        self.tracker.add_expense("2026-11-02", "Travel", 50, "Bus")
        result = self.tracker.monthly_summary("2026-11")
        self.assertEqual(result["total"], 150.0)
        self.assertEqual(result["expense_count"], 2)

    def test_reject_zero_amount(self):
        with self.assertRaises(ValueError):
            self.tracker.add_expense("2026-11-03", "Food", 0, "Invalid")

    def test_budget_status(self):
        self.tracker.set_budget("Food", 500)
        self.tracker.add_expense("2026-11-03", "Food", 125, "Lunch")
        self.assertEqual(self.tracker.budget_status("2026-11")["Food"]["remaining"], 375.0)

if __name__ == "__main__":
    unittest.main()
