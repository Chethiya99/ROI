%%writefile app.py

import streamlit as st
import pandas as pd

# Global variables for Cluster 1
mean_monetary = 2001.3
avg_cashback = 297.28
num_users = 3258

# Function to calculate cashback budget and customers to target
def calculate_cashback_budget_and_customers(revenue_target):
    potential_cashback_budget = avg_cashback * num_users
    max_possible_revenue = mean_monetary * num_users

    if revenue_target < potential_cashback_budget:
        return None, f"Error: The revenue target must be at least {potential_cashback_budget:.2f} yen to cover the minimum cashback budget."

    num_customers_to_target = min(revenue_target / mean_monetary, num_users)
    cashback_budget_needed = num_customers_to_target * avg_cashback

    if num_customers_to_target == num_users and revenue_target > max_possible_revenue:
        return None, f"Error: The revenue target of {revenue_target} yen exceeds the maximum possible revenue ({max_possible_revenue:.2f} yen) that can be generated from this cluster."

    return cashback_budget_needed, num_customers_to_target

# Streamlit UI
st.image("logo.png", width=200)  # Add your company logo here

st.markdown("<h1>Cashback Budget Calculator<br>for At-Risk Low Spenders</h1>", unsafe_allow_html=True)

# Initialize session state
if 'revenue_target' not in st.session_state:
    st.session_state.revenue_target = 0.0
    st.session_state.calculated = False
    st.session_state.cashback_budget = None
    st.session_state.num_customers = None
    st.session_state.error = None
    st.session_state.show_summary = False  # Track the visibility of the summary

# Input: Revenue target
revenue_target = st.number_input("Enter your Revenue Target (in yen):", min_value=0.0, step=1.0)

# Check if the revenue target has changed
if revenue_target != st.session_state.revenue_target:
    st.session_state.revenue_target = revenue_target
    st.session_state.calculated = False
    st.session_state.cashback_budget = None
    st.session_state.num_customers = None
    st.session_state.error = None

# Calculate and display results
if st.button("Calculate Cashback Budget") or st.session_state.calculated:
    if not st.session_state.calculated:
        result, error = calculate_cashback_budget_and_customers(revenue_target)

        if result:
            st.session_state.cashback_budget, st.session_state.num_customers = result, error
            st.session_state.error = None
            st.session_state.calculated = True
        else:
            st.session_state.error = error
            st.session_state.calculated = True

    if st.session_state.error:
        st.error(st.session_state.error)
    else:
        cashback_budget, num_customers = st.session_state.cashback_budget, st.session_state.num_customers
        st.success(f"To achieve a revenue target of {revenue_target} yen:")
        st.write(f"**Cashback Budget Needed:** {cashback_budget:.2f} yen")
        st.write(f"**Number of Customers to Target:** {num_customers:.0f} customers")

        # Load your customer data CSV
        customer_data = pd.read_csv("customer_data.csv")

        # Sort the dataset by Monetary in descending order
        customer_data_sorted = customer_data.sort_values(by="Monetary", ascending=False)

        # Select the top number of customers
        top_customers = customer_data_sorted.head(int(num_customers))

        # Provide an option to download the data
        csv = top_customers.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Top Customers Data as CSV",
            data=csv,
            file_name='top_customers.csv',
            mime='text/csv',
        )

        # Add a checkbox to show or hide the sliders
        if st.checkbox("Show and Adjust Sliders"):
            # User adjustment of number of customers to target
            adjusted_num_customers = st.slider("Adjust the number of customers to target:",
                                               min_value=1, max_value=int(num_customers), value=int(num_customers))

            # Recalculate based on adjusted number of customers
            adjusted_cashback_budget = adjusted_num_customers * avg_cashback
            adjusted_target_revenue = adjusted_num_customers * mean_monetary

            st.write(f"**Adjusted Cashback Budget:** {adjusted_cashback_budget:.2f} yen")
            st.write(f"**Adjusted Target Revenue:** {adjusted_target_revenue:.2f} yen")

            # User adjustment of cashback amount
            adjusted_cashback_amount = st.slider("Adjust the cashback amount (total):",
                                                 min_value=0.0, max_value=cashback_budget, value=cashback_budget)

            # Recalculate based on adjusted cashback amount
            final_num_customers = adjusted_cashback_amount / avg_cashback
            final_target_revenue = final_num_customers * mean_monetary

            st.write(f"**Final Number of Customers to Target:** {final_num_customers:.0f} customers")
            st.write(f"**Final Adjusted Target Revenue:** {final_target_revenue:.2f} yen")

# Button to toggle Cluster 1 Summary Statistics visibility
if st.button("View At-Risk Low Spenders Summary Statistics"):
    st.session_state.show_summary = not st.session_state.show_summary

# Display the summary statistics if the toggle is on
if st.session_state.show_summary:
    st.subheader("At-Risk Low Spenders Summary Statistics")
    st.write(f"Number of Users: {num_users}")
    st.write(f"Average Recency: {36.97:.2f} days")
    st.write(f"Average Frequency: {1.43:.2f} transactions")
    st.write(f"Average Monetary Value: {mean_monetary:.2f} yen")
    st.write(f"Average Cashback per User: {avg_cashback:.2f} yen")
