from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Models ---
class ExpenseUpdate(BaseModel):
    description: str
    amount: float

# --- Routes ---
@app.post("/add_expense/")
def add_expense(description: str, amount: float):
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("INSERT INTO expenses (description, amount) VALUES (?, ?)", (description, amount))
    conn.commit()
    conn.close()
    return {"status": "Expense added successfully"}

@app.get("/expenses/")
def get_expenses():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("SELECT * FROM expenses")
    rows = c.fetchall()
    conn.close()
    return {"expenses": rows}

@app.put("/edit_expense/{expense_id}")
def edit_expense(expense_id: int, update: ExpenseUpdate):
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("UPDATE expenses SET description=?, amount=? WHERE id=?", 
              (update.description, update.amount, expense_id))
    conn.commit()
    conn.close()
    return {"status": "Expense updated successfully"}

@app.delete("/delete_expense/{expense_id}")
def delete_expense(expense_id: int):
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
    return {"status": "Expense deleted successfully"}
