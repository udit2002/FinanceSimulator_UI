# main.py

from accounts import (
    create_account,
    view_accounts,
    update_account,
    delete_account
)

from transactions import (
    deposit,
    withdraw,
    transfer,
    view_transactions
)

from budgets import (
    set_budget,
    view_budgets,
    reset_budget
)

from reports import (
    income_summary,
    expense_summary,
    spending_by_category,
    filter_by_category,
    filter_by_type,
    filter_by_date
)

from exports import (
    export_all_transactions,
    export_by_account,
    export_by_date_range,
    export_by_category
)

from charts import (
    chart_spending_by_category,
    chart_income_vs_expenses,
    chart_spending_pie,
    chart_transaction_trend,
    chart_budget_vs_spent
)


def account_menu():
    while True:
        print("\n--- Account Management ---")
        print("1. Create Account")
        print("2. View Accounts")
        print("3. Update Account")
        print("4. Delete Account")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Enter name: ")
            acc_type = input("Enter type (Savings/Checking): ")
            balance = float(input("Enter opening balance: "))
            create_account(name, acc_type, balance)

        elif choice == "2":
            view_accounts()

        elif choice == "3":
            acc_id = int(input("Enter account ID: "))
            name = input("Enter new name: ")
            acc_type = input("Enter new type: ")
            update_account(acc_id, name, acc_type)

        elif choice == "4":
            acc_id = int(input("Enter account ID: "))
            delete_account(acc_id)

        elif choice == "5":
            break

        else:
            print("Invalid choice")


def transaction_menu():
    while True:
        print("\n--- Transactions ---")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Transfer")
        print("4. View Transactions")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            acc_id = int(input("Enter account ID: "))
            amount = float(input("Enter amount: "))
            deposit(acc_id, amount)

        elif choice == "2":
            acc_id = int(input("Enter account ID: "))
            amount = float(input("Enter amount: "))
            category = input("Enter category: ")
            withdraw(acc_id, amount, category)

        elif choice == "3":
            from_acc = int(input("From account ID: "))
            to_acc = int(input("To account ID: "))
            amount = float(input("Enter amount: "))
            transfer(from_acc, to_acc, amount)

        elif choice == "4":
            view_transactions()

        elif choice == "5":
            break

        else:
            print("Invalid choice")


def budget_menu():
    while True:
        print("\n--- Budget Management ---")
        print("1. Set Budget")
        print("2. View Budgets")
        print("3. Reset Budget")
        print("4. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            category = input("Enter category: ")
            limit = float(input("Enter budget amount: "))
            set_budget(category, limit)

        elif choice == "2":
            view_budgets()

        elif choice == "3":
            category = input("Enter category: ")
            reset_budget(category)

        elif choice == "4":
            break

        else:
            print("Invalid choice")


def report_menu():
    while True:
        print("\n--- Reports ---")
        print("1. Income Summary")
        print("2. Expense Summary")
        print("3. Spending By Category")
        print("4. Filter By Category")
        print("5. Filter By Type")
        print("6. Filter By Date")
        print("7. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            income_summary()

        elif choice == "2":
            expense_summary()

        elif choice == "3":
            spending_by_category()

        elif choice == "4":
            category = input("Enter category: ")
            filter_by_category(category)

        elif choice == "5":
            trans_type = input("Enter type: ")
            filter_by_type(trans_type)

        elif choice == "6":
            start = input("Start date (YYYY-MM-DD): ")
            end = input("End date (YYYY-MM-DD): ")
            filter_by_date(start, end)

        elif choice == "7":
            break

        else:
            print("Invalid choice")


def export_menu():
    while True:
        print("\n--- Export Statements (CSV) ---")
        print("1. Export All Transactions")
        print("2. Export by Account")
        print("3. Export by Date Range")
        print("4. Export by Category")
        print("5. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            filename = input("Enter filename (press Enter for default): ").strip()
            export_all_transactions(filename if filename else "transactions_export.csv")

        elif choice == "2":
            acc_id = int(input("Enter account ID: "))
            filename = input("Enter filename (press Enter for default): ").strip()
            export_by_account(acc_id, filename if filename else None)

        elif choice == "3":
            start = input("Start date (YYYY-MM-DD): ")
            end = input("End date (YYYY-MM-DD): ")
            filename = input("Enter filename (press Enter for default): ").strip()
            export_by_date_range(start, end, filename if filename else None)

        elif choice == "4":
            category = input("Enter category: ")
            filename = input("Enter filename (press Enter for default): ").strip()
            export_by_category(category, filename if filename else None)

        elif choice == "5":
            break

        else:
            print("Invalid choice")


def charts_menu():
    while True:
        print("\n--- Visual Reports (Charts) ---")
        print("1. Spending by Category (Bar Chart)")
        print("2. Income vs Expenses (Bar Chart)")
        print("3. Spending Distribution (Pie Chart)")
        print("4. Daily Spending Trend (Line Chart)")
        print("5. Budget vs Spent (Grouped Bar Chart)")
        print("6. Back")

        choice = input("Enter choice: ")

        if choice == "1":
            filename = input("Save as (press Enter for default): ").strip()
            chart_spending_by_category(filename if filename else "spending_by_category.png")

        elif choice == "2":
            filename = input("Save as (press Enter for default): ").strip()
            chart_income_vs_expenses(filename if filename else "income_vs_expenses.png")

        elif choice == "3":
            filename = input("Save as (press Enter for default): ").strip()
            chart_spending_pie(filename if filename else "spending_pie.png")

        elif choice == "4":
            filename = input("Save as (press Enter for default): ").strip()
            chart_transaction_trend(filename if filename else "transaction_trend.png")

        elif choice == "5":
            filename = input("Save as (press Enter for default): ").strip()
            chart_budget_vs_spent(filename if filename else "budget_vs_spent.png")

        elif choice == "6":
            break

        else:
            print("Invalid choice")


def main():
    while True:
        print("\n====== Personal Finance Simulator ======")
        print("1. Account Management")
        print("2. Transactions")
        print("3. Budget Management")
        print("4. Reports")
        print("5. Export Statements (CSV)")
        print("6. Visual Reports (Charts)")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            account_menu()

        elif choice == "2":
            transaction_menu()

        elif choice == "3":
            budget_menu()

        elif choice == "4":
            report_menu()

        elif choice == "5":
            export_menu()

        elif choice == "6":
            charts_menu()

        elif choice == "7":
            print("Thank you for using Personal Finance Simulator.")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()