# budgets.py

from database import connect_db


def set_budget(category, limit_amount):
    conn = connect_db()
    cur = conn.cursor()

    check_query = """
    SELECT * FROM budgets
    WHERE category = %s;
    """

    cur.execute(check_query, (category,))
    existing = cur.fetchone()

    if existing:
        update_query = """
        UPDATE budgets
        SET limit_amount = %s
        WHERE category = %s;
        """
        cur.execute(update_query, (limit_amount, category))
        print(f"{category} budget updated.")
    else:
        insert_query = """
        INSERT INTO budgets (category, limit_amount, spent)
        VALUES (%s, %s, 0);
        """
        cur.execute(insert_query, (category, limit_amount))
        print(f"{category} budget created.")

    conn.commit()
    cur.close()
    conn.close()


def add_expense(category, amount):
    conn = connect_db()
    cur = conn.cursor()

    check_query = """
    SELECT limit_amount, spent
    FROM budgets
    WHERE category = %s;
    """

    cur.execute(check_query, (category,))
    budget = cur.fetchone()

    if not budget:
        cur.close()
        conn.close()
        return

    limit_amount = float(budget[0])
    spent = float(budget[1])
    new_spent = spent + amount

    update_query = """
    UPDATE budgets
    SET spent = %s
    WHERE category = %s;
    """

    cur.execute(update_query, (new_spent, category))
    conn.commit()

    cur.close()
    conn.close()

    if new_spent > limit_amount:
        print(f"WARNING: {category} budget exceeded!")
    else:
        remaining = limit_amount - new_spent
        print(f"{category} budget remaining: ${remaining}")


def reset_budget(category):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    UPDATE budgets
    SET spent = 0
    WHERE category = %s;
    """

    cur.execute(query, (category,))
    conn.commit()

    cur.close()
    conn.close()

    print(f"{category} budget reset.")


def view_budgets():
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT budget_id, category, limit_amount, spent
    FROM budgets
    ORDER BY budget_id;
    """

    cur.execute(query)
    budgets = cur.fetchall()

    cur.close()
    conn.close()

    if not budgets:
        print("No budgets found.")
        return

    print("\nBudgets:")
    print("-" * 60)

    for budget in budgets:
        remaining = float(budget[2]) - float(budget[3])

        print(
            f"ID: {budget[0]} | "
            f"Category: {budget[1]} | "
            f"Limit: ${budget[2]} | "
            f"Spent: ${budget[3]} | "
            f"Remaining: ${remaining}"
        )