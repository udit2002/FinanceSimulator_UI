# transactions.py

from database import connect_db
from accounts import get_account
from budgets import add_expense


def add_transaction(acc_id, trans_type, amount, category="General"):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    INSERT INTO transactions (acc_id, type, amount, category)
    VALUES (%s, %s, %s, %s);
    """

    cur.execute(query, (acc_id, trans_type, amount, category))

    conn.commit()
    cur.close()
    conn.close()


def deposit(acc_id, amount, category="Deposit"):
    account = get_account(acc_id)

    if not account:
        print("Account not found.")
        return

    conn = connect_db()
    cur = conn.cursor()

    query = """
    UPDATE accounts
    SET balance = balance + %s
    WHERE acc_id = %s;
    """

    cur.execute(query, (amount, acc_id))
    conn.commit()

    cur.close()
    conn.close()

    add_transaction(acc_id, "Deposit", amount, category)

    print(f"${amount} deposited successfully.")


def withdraw(acc_id, amount, category="General"):
    account = get_account(acc_id)

    if not account:
        print("Account not found.")
        return

    current_balance = float(account[3])

    if current_balance < amount:
        print("Insufficient balance.")
        return

    conn = connect_db()
    cur = conn.cursor()

    query = """
    UPDATE accounts
    SET balance = balance - %s
    WHERE acc_id = %s;
    """

    cur.execute(query, (amount, acc_id))
    conn.commit()

    cur.close()
    conn.close()

    add_transaction(acc_id, "Withdraw", amount, category)
    add_expense(category, amount)
    print(f"${amount} withdrawn successfully.")


def transfer(from_acc, to_acc, amount):
    sender = get_account(from_acc)
    receiver = get_account(to_acc)

    if not sender:
        print("Sender account not found.")
        return

    if not receiver:
        print("Receiver account not found.")
        return

    sender_balance = float(sender[3])

    if sender_balance < amount:
        print("Insufficient balance.")
        return

    conn = connect_db()
    cur = conn.cursor()

    debit_query = """
    UPDATE accounts
    SET balance = balance - %s
    WHERE acc_id = %s;
    """

    credit_query = """
    UPDATE accounts
    SET balance = balance + %s
    WHERE acc_id = %s;
    """

    cur.execute(debit_query, (amount, from_acc))
    cur.execute(credit_query, (amount, to_acc))

    conn.commit()

    cur.close()
    conn.close()

    add_transaction(from_acc, "Transfer Out", amount, "Transfer")
    add_transaction(to_acc, "Transfer In", amount, "Transfer")

    print(f"${amount} transferred successfully.")


def view_transactions():
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

    print("\nTransaction History:")
    print("-" * 80)

    for trans in transactions:
        print(
            f"ID: {trans[0]} | "
            f"Account: {trans[1]} | "
            f"{trans[2]} | "
            f"${trans[3]} | "
            f"{trans[4]} | "
            f"{trans[5]}"
        )