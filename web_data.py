# web_data.py
#
# Data-access layer for the Flask web UI. Mirrors the logic in
# accounts.py / transactions.py / budgets.py / reports.py but returns
# data (dicts, lists, tuples) instead of printing to stdout, so the
# Flask templates can render it. The original CLI modules are not
# imported or modified by this file.

from datetime import datetime, date

import psycopg2.extras

from database import connect_db


def _rows(query, params=None):
    conn = connect_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query, params or ())
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


def _execute(query, params=None):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    cur.close()
    conn.close()


def _scalar(query, params=None):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query, params or ())
    value = cur.fetchone()[0]
    cur.close()
    conn.close()
    return float(value) if value is not None else 0.0


# ---------------------------------------------------------------- accounts

def list_accounts():
    return _rows("SELECT acc_id, name, type, balance FROM accounts ORDER BY acc_id;")


def get_account(acc_id):
    rows = _rows("SELECT acc_id, name, type, balance FROM accounts WHERE acc_id = %s;", (acc_id,))
    return rows[0] if rows else None


def create_account(name, acc_type, balance):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO accounts (name, type, balance) VALUES (%s, %s, %s) RETURNING acc_id;",
        (name, acc_type, balance),
    )
    acc_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return acc_id


def update_account(acc_id, name, acc_type):
    if not get_account(acc_id):
        return False, "Account not found."
    _execute(
        "UPDATE accounts SET name = %s, type = %s WHERE acc_id = %s;",
        (name, acc_type, acc_id),
    )
    return True, "Account updated successfully."


def delete_account(acc_id):
    if not get_account(acc_id):
        return False, "Account not found."
    _execute("DELETE FROM transactions WHERE acc_id = %s;", (acc_id,))
    _execute("DELETE FROM accounts WHERE acc_id = %s;", (acc_id,))
    return True, "Account deleted successfully."


def total_balance():
    return _scalar("SELECT COALESCE(SUM(balance), 0) FROM accounts;")


# ------------------------------------------------------------ transactions

def _add_transaction(acc_id, trans_type, amount, category):
    _execute(
        "INSERT INTO transactions (acc_id, type, amount, category) VALUES (%s, %s, %s, %s);",
        (acc_id, trans_type, amount, category),
    )


def list_transactions(category=None, trans_type=None, start=None, end=None, acc_id=None, limit=None):
    query = """
        SELECT trans_id, acc_id, type, amount, category, date
        FROM transactions
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND category = %s"
        params.append(category)
    if trans_type:
        query += " AND type = %s"
        params.append(trans_type)
    if start and end:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start, end])
    if acc_id:
        query += " AND acc_id = %s"
        params.append(acc_id)

    query += " ORDER BY date DESC"

    if limit:
        query += " LIMIT %s"
        params.append(limit)

    return _rows(query, tuple(params))


def deposit(acc_id, amount, category="Deposit"):
    account = get_account(acc_id)
    if not account:
        return False, "Account not found.", None

    _execute("UPDATE accounts SET balance = balance + %s WHERE acc_id = %s;", (amount, acc_id))
    _add_transaction(acc_id, "Deposit", amount, category)

    return True, f"${amount:,.2f} deposited successfully.", None


def withdraw(acc_id, amount, category="General"):
    account = get_account(acc_id)
    if not account:
        return False, "Account not found.", None

    current_balance = float(account["balance"])
    if current_balance < amount:
        return False, "Insufficient balance.", None

    _execute("UPDATE accounts SET balance = balance - %s WHERE acc_id = %s;", (amount, acc_id))
    _add_transaction(acc_id, "Withdraw", amount, category)

    warning = _apply_budget_expense(category, amount)

    return True, f"${amount:,.2f} withdrawn successfully.", warning


def transfer(from_acc, to_acc, amount):
    sender = get_account(from_acc)
    receiver = get_account(to_acc)

    if not sender:
        return False, "Sender account not found."
    if not receiver:
        return False, "Receiver account not found."

    sender_balance = float(sender["balance"])
    if sender_balance < amount:
        return False, "Insufficient balance."

    _execute("UPDATE accounts SET balance = balance - %s WHERE acc_id = %s;", (amount, from_acc))
    _execute("UPDATE accounts SET balance = balance + %s WHERE acc_id = %s;", (amount, to_acc))

    _add_transaction(from_acc, "Transfer Out", amount, "Transfer")
    _add_transaction(to_acc, "Transfer In", amount, "Transfer")

    return True, f"${amount:,.2f} transferred successfully."


# ----------------------------------------------------------------- budgets

def list_budgets():
    rows = _rows("SELECT budget_id, category, limit_amount, spent FROM budgets ORDER BY budget_id;")
    for b in rows:
        b["limit_amount"] = float(b["limit_amount"])
        b["spent"] = float(b["spent"])
        b["remaining"] = b["limit_amount"] - b["spent"]
        b["pct"] = min(100, round((b["spent"] / b["limit_amount"]) * 100, 1)) if b["limit_amount"] else 0
        b["exceeded"] = b["spent"] > b["limit_amount"]
    return rows


def set_budget(category, limit_amount):
    existing = _rows("SELECT * FROM budgets WHERE category = %s;", (category,))
    if existing:
        _execute("UPDATE budgets SET limit_amount = %s WHERE category = %s;", (limit_amount, category))
        return f"{category} budget updated."
    _execute(
        "INSERT INTO budgets (category, limit_amount, spent) VALUES (%s, %s, 0);",
        (category, limit_amount),
    )
    return f"{category} budget created."


def reset_budget(category):
    _execute("UPDATE budgets SET spent = 0 WHERE category = %s;", (category,))
    return f"{category} budget reset."


def _apply_budget_expense(category, amount):
    rows = _rows("SELECT limit_amount, spent FROM budgets WHERE category = %s;", (category,))
    if not rows:
        return None

    limit_amount = float(rows[0]["limit_amount"])
    spent = float(rows[0]["spent"])
    new_spent = spent + amount

    _execute("UPDATE budgets SET spent = %s WHERE category = %s;", (new_spent, category))

    if new_spent > limit_amount:
        return f"WARNING: {category} budget exceeded!"
    remaining = limit_amount - new_spent
    return f"{category} budget remaining: ${remaining:,.2f}"


# ----------------------------------------------------------------- reports

def income_summary():
    return _scalar("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type IN ('Deposit', 'Transfer In');")


def expense_summary():
    return _scalar("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type IN ('Withdraw', 'Transfer Out');")


def spending_by_category():
    rows = _rows(
        """
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE type = 'Withdraw'
        GROUP BY category
        ORDER BY SUM(amount) DESC;
        """
    )
    for r in rows:
        r["total"] = float(r["total"])
    return rows


def daily_spending_trend():
    rows = _rows(
        """
        SELECT DATE(date) AS day, SUM(amount) AS total
        FROM transactions
        WHERE type IN ('Withdraw', 'Transfer Out')
        GROUP BY day
        ORDER BY day;
        """
    )
    for r in rows:
        r["total"] = float(r["total"])
        r["day"] = r["day"].isoformat() if isinstance(r["day"], (date, datetime)) else str(r["day"])
    return rows


def categories_in_use():
    rows = _rows("SELECT DISTINCT category FROM transactions ORDER BY category;")
    return [r["category"] for r in rows]


def transaction_types_in_use():
    rows = _rows("SELECT DISTINCT type FROM transactions ORDER BY type;")
    return [r["type"] for r in rows]
