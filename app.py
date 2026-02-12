import streamlit as st
import requests
import pandas as pd
import time
import math

BASE_URL = "http://127.0.0.1:8000"

st.title("💰 Smart Expense Tracker")

# --- Custom CSS for compact buttons ---
st.markdown("""
    <style>
    div.stButton > button {
        padding: 2px 6px;
        font-size: 11px;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Always fetch latest expenses ---
def fetch_expenses():
    try:
        response = requests.get(f"{BASE_URL}/expenses/")
        return response.json().get("expenses", [])
    except Exception as e:
        st.error(f"Error fetching expenses: {e}")
        return []

expenses = fetch_expenses()

# --- Add Expense Form ---
st.header("Add a new expense")
with st.form("expense_form", clear_on_submit=True):
    desc = st.text_input("Description", placeholder="Enter description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f", value=None, placeholder="Enter amount")
    
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if desc.strip() != "" and amount is not None and amount > 0:
            resp = requests.post(
                f"{BASE_URL}/add_expense/",
                params={"description": desc, "amount": amount}
            )
            msg = st.empty()
            msg.markdown(f"✅ {resp.json()['status']}")
            time.sleep(3)
            msg.empty()
            st.rerun()
        else:
            warn = st.empty()
            warn.markdown("⚠️ Please enter a valid description and amount.")
            time.sleep(3)
            warn.empty()

# --- Manage Expenses (Collapsible) ---
st.header("Manage Expenses")

with st.expander("📂 Show/Hide Expenses", expanded=False):
    if expenses:
        df = pd.DataFrame(expenses, columns=["ID", "Description", "Amount"])

        # --- Search bar (ID, Description, Amount) ---
        search_query = st.text_input("🔍 Search expenses (ID / Description / Amount):")
        if search_query.strip():
            df = df[
                df["Description"].str.contains(search_query, case=False, na=False) |
                df["ID"].astype(str).str.contains(search_query, case=False, na=False) |
                df["Amount"].astype(str).str.contains(search_query, case=False, na=False)
            ]

        # --- Pagination ---
        items_per_page = 10
        total_pages = math.ceil(len(df) / items_per_page)
        page = st.number_input("Page", min_value=1, max_value=max(total_pages, 1), step=1)

        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        df_page = df.iloc[start_idx:end_idx]

        st.write(f"Showing page {page} of {total_pages}")

        # --- Excel-style table headers ---
        header_cols = st.columns([1,3,2,1,1])
        header_cols[0].markdown("**ID**")
        header_cols[1].markdown("**Description**")
        header_cols[2].markdown("**Amount**")
        header_cols[3].markdown("**Edit**")
        header_cols[4].markdown("**Delete**")

        # --- Inline Edit/Delete rows ---
        for exp in df_page.values.tolist():
            col1, col2, col3, col4, col5 = st.columns([1,3,2,1,1])
            with col1:
                st.write(exp[0])  # ID
            with col2:
                st.write(exp[1])  # Description
            with col3:
                st.write(f"₹{exp[2]:.2f}")  # Amount
            with col4:
                if st.button("✏️", key=f"edit_{exp[0]}"):
                    with st.form(f"edit_form_{exp[0]}"):
                        new_desc = st.text_input("New Description", value=exp[1])
                        new_amount = st.number_input("New Amount", value=exp[2], min_value=0.0, format="%.2f")
                        save = st.form_submit_button("Save")
                        if save:
                            resp = requests.put(
                                f"{BASE_URL}/edit_expense/{exp[0]}",
                                json={"description": new_desc, "amount": new_amount}
                            )
                            msg = st.empty()
                            msg.markdown(f"✅ {resp.json()['status']}")
                            time.sleep(3)
                            msg.empty()
                            st.rerun()
            with col5:
                if st.button("🗑️", key=f"delete_{exp[0]}"):
                    resp = requests.delete(f"{BASE_URL}/delete_expense/{exp[0]}")
                    msg = st.empty()
                    msg.markdown(f"✅ {resp.json()['status']}")
                    time.sleep(3)
                    msg.empty()
                    st.rerun()

        # --- Total Expenses summary ---
        total = df["Amount"].sum()
        st.subheader(f"Total Expenses: ₹{total:.2f}")
    else:
        st.info("No expenses found yet.")
