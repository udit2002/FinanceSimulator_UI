# app.py
#
# Flask web UI for the Personal Finance Simulator.
# Reads/writes through web_data.py. For CSV export and PNG charts it
# calls straight into the existing exports.py / charts.py modules so
# the CLI's behaviour there is reused, not duplicated.

import os

from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
)

import web_data as data
import exports as export_mod
import charts as chart_mod

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(BASE_DIR, "exports_output")
CHARTS_DIR = os.path.join(BASE_DIR, "static", "charts")

os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"


# ------------------------------------------------------------------ helpers

def parse_amount(value):
    try:
        amount = float(value)
        if amount <= 0:
            return None
        return amount
    except (TypeError, ValueError):
        return None


# ----------------------------------------------------------------- dashboard

@app.route("/")
def dashboard():
    accounts = data.list_accounts()
    recent = data.list_transactions(limit=8)
    budgets = data.list_budgets()
    income = data.income_summary()
    expenses = data.expense_summary()

    return render_template(
        "dashboard.html",
        accounts=accounts,
        recent=recent,
        budgets=budgets,
        income=income,
        expenses=expenses,
        net=income - expenses,
        total_balance=data.total_balance(),
    )


@app.route("/api/spending-by-category")
def api_spending_by_category():
    rows = data.spending_by_category()
    return jsonify({
        "labels": [r["category"] for r in rows],
        "values": [r["total"] for r in rows],
    })


@app.route("/api/spending-trend")
def api_spending_trend():
    rows = data.daily_spending_trend()
    return jsonify({
        "labels": [r["day"] for r in rows],
        "values": [r["total"] for r in rows],
    })


@app.route("/api/income-vs-expense")
def api_income_vs_expense():
    return jsonify({
        "income": data.income_summary(),
        "expenses": data.expense_summary(),
    })


# ------------------------------------------------------------------ accounts

@app.route("/accounts")
def accounts_page():
    return render_template("accounts.html", accounts=data.list_accounts())


@app.route("/accounts/create", methods=["POST"])
def accounts_create():
    name = request.form.get("name", "").strip()
    acc_type = request.form.get("type", "").strip()
    balance = parse_amount(request.form.get("balance") or 0) or 0

    if not name or not acc_type:
        flash("Name and type are required.", "error")
        return redirect(url_for("accounts_page"))

    acc_id = data.create_account(name, acc_type, balance)
    flash(f"Account created successfully (ID: {acc_id}).", "success")
    return redirect(url_for("accounts_page"))


@app.route("/accounts/<int:acc_id>/update", methods=["POST"])
def accounts_update(acc_id):
    name = request.form.get("name", "").strip()
    acc_type = request.form.get("type", "").strip()

    ok, message = data.update_account(acc_id, name, acc_type)
    flash(message, "success" if ok else "error")
    return redirect(url_for("accounts_page"))


@app.route("/accounts/<int:acc_id>/delete", methods=["POST"])
def accounts_delete(acc_id):
    ok, message = data.delete_account(acc_id)
    flash(message, "success" if ok else "error")
    return redirect(url_for("accounts_page"))


# -------------------------------------------------------------- transactions

@app.route("/transactions")
def transactions_page():
    category = request.args.get("category") or None
    trans_type = request.args.get("type") or None
    start = request.args.get("start") or None
    end = request.args.get("end") or None

    rows = data.list_transactions(
        category=category,
        trans_type=trans_type,
        start=start if start and end else None,
        end=end if start and end else None,
    )

    return render_template(
        "transactions.html",
        transactions=rows,
        accounts=data.list_accounts(),
        categories=data.categories_in_use(),
        types=data.transaction_types_in_use(),
        filters={"category": category, "type": trans_type, "start": start, "end": end},
    )


@app.route("/transactions/deposit", methods=["POST"])
def transactions_deposit():
    acc_id = request.form.get("acc_id", type=int)
    amount = parse_amount(request.form.get("amount"))
    category = request.form.get("category", "Deposit").strip() or "Deposit"

    if not acc_id or amount is None:
        flash("Enter a valid account and amount.", "error")
        return redirect(url_for("transactions_page"))

    ok, message, _ = data.deposit(acc_id, amount, category)
    flash(message, "success" if ok else "error")
    return redirect(url_for("transactions_page"))


@app.route("/transactions/withdraw", methods=["POST"])
def transactions_withdraw():
    acc_id = request.form.get("acc_id", type=int)
    amount = parse_amount(request.form.get("amount"))
    category = request.form.get("category", "General").strip() or "General"

    if not acc_id or amount is None:
        flash("Enter a valid account and amount.", "error")
        return redirect(url_for("transactions_page"))

    ok, message, warning = data.withdraw(acc_id, amount, category)
    flash(message, "success" if ok else "error")
    if warning:
        flash(warning, "warning" if "WARNING" in warning else "info")
    return redirect(url_for("transactions_page"))


@app.route("/transactions/transfer", methods=["POST"])
def transactions_transfer():
    from_acc = request.form.get("from_acc", type=int)
    to_acc = request.form.get("to_acc", type=int)
    amount = parse_amount(request.form.get("amount"))

    if not from_acc or not to_acc or amount is None:
        flash("Enter valid accounts and amount.", "error")
        return redirect(url_for("transactions_page"))

    if from_acc == to_acc:
        flash("From and To accounts must be different.", "error")
        return redirect(url_for("transactions_page"))

    ok, message = data.transfer(from_acc, to_acc, amount)
    flash(message, "success" if ok else "error")
    return redirect(url_for("transactions_page"))


# ------------------------------------------------------------------ budgets

@app.route("/budgets")
def budgets_page():
    return render_template("budgets.html", budgets=data.list_budgets())


@app.route("/budgets/set", methods=["POST"])
def budgets_set():
    category = request.form.get("category", "").strip()
    limit_amount = parse_amount(request.form.get("limit_amount"))

    if not category or limit_amount is None:
        flash("Enter a valid category and budget amount.", "error")
        return redirect(url_for("budgets_page"))

    message = data.set_budget(category, limit_amount)
    flash(message, "success")
    return redirect(url_for("budgets_page"))


@app.route("/budgets/<category>/reset", methods=["POST"])
def budgets_reset(category):
    message = data.reset_budget(category)
    flash(message, "success")
    return redirect(url_for("budgets_page"))


# ------------------------------------------------------------------ reports

@app.route("/reports")
def reports_page():
    return render_template(
        "reports.html",
        income=data.income_summary(),
        expenses=data.expense_summary(),
        by_category=data.spending_by_category(),
    )


# ------------------------------------------------------------------- export

@app.route("/export")
def export_page():
    return render_template(
        "export.html",
        accounts=data.list_accounts(),
        categories=data.categories_in_use(),
    )


def _send_export(filename):
    if not os.path.exists(filename):
        flash("No matching transactions to export.", "error")
        return redirect(url_for("export_page"))
    return send_file(filename, as_attachment=True)


@app.route("/export/all")
def export_all():
    filename = os.path.join(EXPORT_DIR, "transactions_export.csv")
    if os.path.exists(filename):
        os.remove(filename)
    export_mod.export_all_transactions(filename)
    return _send_export(filename)


@app.route("/export/account")
def export_account():
    acc_id = request.args.get("acc_id", type=int)
    filename = os.path.join(EXPORT_DIR, f"account_{acc_id}_statement.csv")
    if os.path.exists(filename):
        os.remove(filename)
    export_mod.export_by_account(acc_id, filename)
    return _send_export(filename)


@app.route("/export/category")
def export_category():
    category = request.args.get("category", "")
    filename = os.path.join(EXPORT_DIR, f"category_{category.lower().replace(' ', '_')}_export.csv")
    if os.path.exists(filename):
        os.remove(filename)
    export_mod.export_by_category(category, filename)
    return _send_export(filename)


@app.route("/export/date-range")
def export_date_range():
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    filename = os.path.join(EXPORT_DIR, f"statement_{start}_to_{end}.csv")
    if os.path.exists(filename):
        os.remove(filename)
    export_mod.export_by_date_range(start, end, filename)
    return _send_export(filename)


# ------------------------------------------------------------------- charts

CHART_GENERATORS = {
    "spending_by_category": chart_mod.chart_spending_by_category,
    "income_vs_expenses": chart_mod.chart_income_vs_expenses,
    "spending_pie": chart_mod.chart_spending_pie,
    "transaction_trend": chart_mod.chart_transaction_trend,
    "budget_vs_spent": chart_mod.chart_budget_vs_spent,
}


@app.route("/charts")
def charts_page():
    existing = {}
    for key in CHART_GENERATORS:
        path = os.path.join(CHARTS_DIR, f"{key}.png")
        if os.path.exists(path):
            existing[key] = int(os.path.getmtime(path))
    return render_template("charts.html", existing=existing, chart_keys=list(CHART_GENERATORS))


@app.route("/charts/generate/<key>", methods=["POST"])
def charts_generate(key):
    generator = CHART_GENERATORS.get(key)
    if not generator:
        flash("Unknown chart type.", "error")
        return redirect(url_for("charts_page"))

    filename = os.path.join(CHARTS_DIR, f"{key}.png")
    generator(filename)
    flash("Chart generated.", "success")
    return redirect(url_for("charts_page"))


if __name__ == "__main__":
    app.run(debug=True)
