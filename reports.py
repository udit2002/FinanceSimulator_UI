# reports.py

from database import connect_db


def view_all_transactions():
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT trans_id, acc_id, type, amount, category, date
    FROM transactions
    ORDER BY date DESC;
    """

    cur.execute(query)
    transactions = cur.fetchall()

    cur.close()
    conn.close()

    if not transactions:
        print("No transactions found.")
        return

    print("\nTransaction History")
    print("-" * 90)

    for t in transactions:
        print(
            f"ID: {t[0]} | "
            f"Account: {t[1]} | "
            f"{t[2]} | "
            f"${t[3]} | "
            f"{t[4]} | "
            f"{t[5]}"
        )


def income_summary():
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT COALESCE(SUM(amount), 0)
    FROM transactions
    WHERE type IN ('Deposit', 'Transfer In');
    """

    cur.execute(query)
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"\nTotal Income: ${total}")


def expense_summary():
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT COALESCE(SUM(amount), 0)
    FROM transactions
    WHERE type IN ('Withdraw', 'Transfer Out');
    """

    cur.execute(query)
    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"\nTotal Expenses: ${total}")


def spending_by_category():
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT category, SUM(amount)
    FROM transactions
    WHERE type = 'Withdraw'
    GROUP BY category
    ORDER BY SUM(amount) DESC;
    """

    cur.execute(query)
    data = cur.fetchall()

    cur.close()
    conn.close()

    if not data:
        print("No expense data found.")
        return

    print("\nSpending By Category")
    print("-" * 50)

    for row in data:
        print(f"{row[0]}: ${row[1]}")


def filter_by_category(category):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT trans_id, acc_id, type, amount, category, date
    FROM transactions
    WHERE category = %s
    ORDER BY date DESC;
    """

    cur.execute(query, (category,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        print("No matching transactions found.")
        return

    print(f"\nTransactions for category: {category}")
    print("-" * 80)

    for row in rows:
        print(
            f"ID:{row[0]} | "
            f"Acc:{row[1]} | "
            f"{row[2]} | "
            f"${row[3]} | "
            f"{row[5]}"
        )


def filter_by_type(trans_type):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT trans_id, acc_id, type, amount, category, date
    FROM transactions
    WHERE type = %s
    ORDER BY date DESC;
    """

    cur.execute(query, (trans_type,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        print("No matching transactions found.")
        return

    print(f"\nTransactions of type: {trans_type}")
    print("-" * 80)

    for row in rows:
        print(
            f"ID:{row[0]} | "
            f"Acc:{row[1]} | "
            f"${row[3]} | "
            f"{row[4]} | "
            f"{row[5]}"
        )


def filter_by_date(start_date, end_date):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT trans_id, acc_id, type, amount, category, date
    FROM transactions
    WHERE date BETWEEN %s AND %s
    ORDER BY date DESC;
    """

    cur.execute(query, (start_date, end_date))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        print("No matching transactions found.")
        return

    print(f"\nTransactions from {start_date} to {end_date}")
    print("-" * 90)

    for row in rows:
        print(
            f"ID:{row[0]} | "
            f"Acc:{row[1]} | "
            f"{row[2]} | "
            f"${row[3]} | "
            f"{row[4]} | "
            f"{row[5]}"
        )