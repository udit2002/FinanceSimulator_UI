# exports.py

import csv
import os
from database import connect_db


def export_all_transactions(filename="transactions_export.csv"):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT trans_id, acc_id, type, amount, category, date
    FROM transactions
    ORDER BY date DESC;
    """

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        print("No transactions to export.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Transaction ID", "Account ID", "Type", "Amount", "Category", "Date"])
        for row in rows:
            writer.writerow(row)

    print(f"Transactions exported to '{filename}' ({len(rows)} records).")


def export_by_account(acc_id, filename=None):
    if not filename:
        filename = f"account_{acc_id}_statement.csv"

    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT trans_id, acc_id, type, amount, category, date
    FROM transactions
    WHERE acc_id = %s
    ORDER BY date DESC;
    """

    cur.execute(query, (acc_id,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        print(f"No transactions found for account {acc_id}.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Transaction ID", "Account ID", "Type", "Amount", "Category", "Date"])
        for row in rows:
            writer.writerow(row)

    print(f"Account {acc_id} statement exported to '{filename}' ({len(rows)} records).")


def export_by_date_range(start_date, end_date, filename=None):
    if not filename:
        filename = f"statement_{start_date}_to_{end_date}.csv"

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
        print("No transactions found in the specified date range.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Transaction ID", "Account ID", "Type", "Amount", "Category", "Date"])
        for row in rows:
            writer.writerow(row)

    print(f"Statement from {start_date} to {end_date} exported to '{filename}' ({len(rows)} records).")


def export_by_category(category, filename=None):
    if not filename:
        filename = f"category_{category.lower().replace(' ', '_')}_export.csv"

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
        print(f"No transactions found for category '{category}'.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Transaction ID", "Account ID", "Type", "Amount", "Category", "Date"])
        for row in rows:
            writer.writerow(row)

    print(f"Category '{category}' transactions exported to '{filename}' ({len(rows)} records).")