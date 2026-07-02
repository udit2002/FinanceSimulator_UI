# charts.py

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from database import connect_db
from datetime import datetime


def chart_spending_by_category(save_to="spending_by_category.png"):
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
        print("No expense data found to chart.")
        return

    categories = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(categories, amounts, color="steelblue", edgecolor="white")

    for bar, amount in zip(bars, amounts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(amounts) * 0.01,
            f"${amount:,.2f}",
            ha="center", va="bottom", fontsize=9
        )

    ax.set_title("Spending by Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Category", fontsize=11)
    ax.set_ylabel("Total Spent ($)", fontsize=11)
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(save_to, dpi=150)
    plt.close()

    print(f"Chart saved to '{save_to}'.")


def chart_income_vs_expenses(save_to="income_vs_expenses.png"):
    conn = connect_db()
    cur = conn.cursor()

    income_query = """
    SELECT COALESCE(SUM(amount), 0)
    FROM transactions
    WHERE type IN ('Deposit', 'Transfer In');
    """

    expense_query = """
    SELECT COALESCE(SUM(amount), 0)
    FROM transactions
    WHERE type IN ('Withdraw', 'Transfer Out');
    """

    cur.execute(income_query)
    total_income = float(cur.fetchone()[0])

    cur.execute(expense_query)
    total_expenses = float(cur.fetchone()[0])

    cur.close()
    conn.close()

    labels = ["Income", "Expenses"]
    values = [total_income, total_expenses]
    colors = ["#4CAF50", "#F44336"]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.4)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.01,
            f"${val:,.2f}",
            ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    ax.set_title("Income vs Expenses", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Amount ($)", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(save_to, dpi=150)
    plt.close()

    print(f"Chart saved to '{save_to}'.")


def chart_spending_pie(save_to="spending_pie.png"):
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
        print("No expense data found to chart.")
        return

    categories = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.82
    )

    for text in autotexts:
        text.set_fontsize(9)

    ax.set_title("Spending Distribution by Category", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(save_to, dpi=150)
    plt.close()

    print(f"Chart saved to '{save_to}'.")


def chart_transaction_trend(save_to="transaction_trend.png"):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT DATE(date) AS day, SUM(amount)
    FROM transactions
    WHERE type IN ('Withdraw', 'Transfer Out')
    GROUP BY day
    ORDER BY day;
    """

    cur.execute(query)
    data = cur.fetchall()

    cur.close()
    conn.close()

    if not data:
        print("No data available for trend chart.")
        return

    dates = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, amounts, marker="o", color="steelblue", linewidth=2, markersize=5)
    ax.fill_between(dates, amounts, alpha=0.15, color="steelblue")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=30)

    ax.set_title("Daily Spending Trend", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Amount Spent ($)", fontsize=11)
    ax.grid(linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(save_to, dpi=150)
    plt.close()

    print(f"Chart saved to '{save_to}'.")


def chart_budget_vs_spent(save_to="budget_vs_spent.png"):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT category, limit_amount, spent
    FROM budgets
    ORDER BY category;
    """

    cur.execute(query)
    data = cur.fetchall()

    cur.close()
    conn.close()

    if not data:
        print("No budget data found to chart.")
        return

    categories = [row[0] for row in data]
    limits = [float(row[1]) for row in data]
    spent = [float(row[2]) for row in data]

    x = range(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 6))
    bars1 = ax.bar([i - width / 2 for i in x], limits, width, label="Budget Limit", color="#4CAF50", edgecolor="white")
    bars2 = ax.bar([i + width / 2 for i in x], spent, width, label="Spent", color="#F44336", edgecolor="white")

    ax.set_xticks(list(x))
    ax.set_xticklabels(categories, rotation=30)
    ax.set_title("Budget vs Spent by Category", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel("Amount ($)", fontsize=11)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(save_to, dpi=150)
    plt.close()

    print(f"Chart saved to '{save_to}'.")