from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def connect_db():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = connect_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = connect_db()

    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY id DESC"
    ).fetchall()

    income = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE type = 'Income'"
    ).fetchone()[0] or 0

    total_expenses = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE type = 'Expense'"
    ).fetchone()[0] or 0

    balance = income - total_expenses

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        income=income,
        total_expenses=total_expenses,
        balance=balance
    )


@app.route("/add", methods=["POST"])
def add_expense():
    title = request.form["title"]
    category = request.form["category"]
    amount = float(request.form["amount"])
    transaction_type = request.form["type"]
    date = request.form["date"]

    conn = connect_db()

    conn.execute(
        """INSERT INTO expenses
        (title, category, amount, type, date)
        VALUES (?, ?, ?, ?, ?)""",
        (title, category, amount, transaction_type, date)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:expense_id>")
def delete_expense(expense_id):
    conn = connect_db()

    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


create_table()

if __name__ == "__main__":
    app.run(debug=True)