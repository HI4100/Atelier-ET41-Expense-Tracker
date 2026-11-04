# ATELIER 41 | Expense Tracker

A Python command-line application for recording personal expenses, managing category budgets, searching transactions, and reviewing monthly spending.

**Status:** Working CLI application with automated unit tests.

## Features
- Add expenses with date, category, amount, and description.
- View expenses, newest first.
- Generate monthly totals and category breakdowns.
- Set and update monthly category budgets.
- Compare category spending with budget limits.
- Search by category, date range, and description keyword.
- Edit and delete existing expense records.
- Export expenses to a separate CSV file.
- Validate dates, amounts, and required fields.
- Store expenses in CSV and budgets in JSON.
- Automated tests using Python unittest.

## Technology
Python 3.10+; CSV and JSON; Python standard library; unittest; Git and GitHub. No third-party packages are required.

## Getting started
1. Install Python 3.10 or newer and ensure it is on PATH.
2. Clone this repository:
   git clone https://github.com/HI4100/Atelier-ET41-Expense-Tracker.git
3. Enter the project directory:
   cd Atelier-ET41-Expense-Tracker
4. Run the app:
   python main.py
5. Run tests:
   python -m unittest discover -s tests -v

## Menu
1 Add expense | 2 View all | 3 Monthly summary and budget status | 4 Set/update budget | 5 Search | 6 Edit | 7 Delete | 8 Export CSV | 9 Exit

## Project structure
- main.py: command-line interface
- src/tracker.py: expense and budget logic
- tests/test_tracker.py: automated tests
- data/: local runtime data (created automatically and excluded from Git)

## Design notes
The core logic is separated from the CLI for independent testing. Decimal is used for currency arithmetic. Each expense receives an ID for editing and deletion. Tests use temporary directories and do not touch personal records.

## Privacy and limitations
Local, single-user educational project. It does not connect to banks, payment services, or live accounts. Real records are stored locally in data/ and should never be committed to GitHub. CSV/JSON storage is intended for a small personal project, not concurrent multi-user use. No GUI, authentication, or cloud sync is included yet.

## Future improvements
Desktop or web interface, charts, optional Excel export, SQLite storage, and import with duplicate detection.

## Disclaimer
For educational and personal record-keeping purposes only; not financial, tax, or investment advice.

---

## ✨ ATELIER 41

> **Build it clearly. Analyze it carefully. Test it honestly. Improve it continuously.**

**Humza Warsi ~ Author**  
Part of the **ATELIER 41** project collection.

🔗 **Portfolio:** [@HI4100](https://github.com/HI4100)

*Maybe fate brought you here for your sparkling future. ✨ Let's connect and build something meaningful.*
