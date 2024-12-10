import streamlit as st
import json
import pandas as pd

def orders_page():
    # Load the data from the JSON file
    json_filename = "data/analysisBepensa.json"
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)

    # Get the Login ID and Outlet Code from session state
    login_id = st.session_state.get("login_id")
    outlet_code = st.session_state.get("outlet_code")
    print(f"Login ID: {login_id}")
    print(f"Outlet Code: {outlet_code}")

    # Check if Login ID and Outlet Code exist in the data
    user_key = f"{login_id}::{outlet_code}"
    if st.button("Back to Home"):
        st.session_state.page = "home"  # Set the page back to home
        return
    st.markdown("### Orders")
    
    if user_key in data:
        user_data = data[user_key]
        st.subheader(f"User: {login_id} - Outlet: {outlet_code}")
        # Show Orders Data in Table
        if 'orders' in user_data:
            st.markdown("### Orders")
            orders_df = pd.DataFrame(user_data['orders'])
            st.dataframe(orders_df)  # Display orders in a table format

        # Show Recommendations Data in Table
        if 'recommendation' in user_data:
            st.markdown("### Recommendations")
            recommendation_df = pd.DataFrame(user_data['recommendation'])
            st.dataframe(recommendation_df)  # Display recommendations in a table format

        # Show Sales Data in Table
        if 'sales' in user_data:
            st.markdown("### Sales")
            sales_df = pd.DataFrame(user_data['sales'])
            st.dataframe(sales_df)  # Display sales in a table format
    else:
        st.write(f"No data found for Login ID: {login_id} and Outlet Code: {outlet_code}")

# orders_page();
