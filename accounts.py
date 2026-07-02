# accounts.py

from database import connect_db


class Account:
    def __init__(self, name, acc_type, balance=0):
        self.name = name
        self.acc_type = acc_type
        self.balance = balance


def create_account(name, acc_type, balance=0):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    INSERT INTO accounts (name, type, balance)
    VALUES (%s, %s, %s)
    RETURNING acc_id;
    """

    cur.execute(query, (name, acc_type, balance))
    acc_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    print(f"Account created successfully. Account ID: {acc_id}")


def view_accounts():
    conn = connect_db()
    cur = conn.cursor()

    query = "SELECT * FROM accounts ORDER BY acc_id;"
    cur.execute(query)

    accounts = cur.fetchall()

    cur.close()
    conn.close()

    if not accounts:
        print("No accounts found.")
        return

    print("\nAccounts:")
    print("-" * 50)

    for acc in accounts:
        print(
            f"ID: {acc[0]} | "
            f"Name: {acc[1]} | "
            f"Type: {acc[2]} | "
            f"Balance: ${acc[3]}"
        )


def get_account(acc_id):
    conn = connect_db()
    cur = conn.cursor()

    query = "SELECT * FROM accounts WHERE acc_id = %s;"
    cur.execute(query, (acc_id,))

    account = cur.fetchone()

    cur.close()
    conn.close()

    return account


def update_account(acc_id, new_name=None, new_type=None):
    account = get_account(acc_id)

    if not account:
        print("Account not found.")
        return

    name = new_name if new_name else account[1]
    acc_type = new_type if new_type else account[2]

    conn = connect_db()
    cur = conn.cursor()

    query = """
    UPDATE accounts
    SET name = %s, type = %s
    WHERE acc_id = %s;
    """

    cur.execute(query, (name, acc_type, acc_id))

    conn.commit()
    cur.close()
    conn.close()

    print("Account updated successfully.")


def delete_account(acc_id):
    account = get_account(acc_id)

    if not account:
        print("Account not found.")
        return

    conn = connect_db()
    cur = conn.cursor()

    # delete related transactions first
    cur.execute(
        """
        DELETE FROM transactions
        WHERE acc_id = %s;
        """,
        (acc_id,)
    )

    # then delete account
    cur.execute(
        """
        DELETE FROM accounts
        WHERE acc_id = %s;
        """,
        (acc_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    print("Account deleted successfully.")