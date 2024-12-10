import streamlit as st
import json
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from s3 import isKeyExist, read_file_from_s3
from analysisReading import generate_json_analysis
from lob_names import lob_list
from datetime import date
from analysisSummaryReading import read_and_trim_csv


home_page_content = {}
order_page_content = ""

def load_data(lob, date):
    keyAnalysisSummary = f"dailyResponseOderReport/analysisSummary_{lob}_{date} 00:00:00.csv"
    keyAnalysis = f"dailyResponseOderReport/analysis_{lob}_{date} 00:00:00.csv"

    # print(keyAnalysis)

    isKeyPresent = isKeyExist(keyAnalysisSummary)
    if(isKeyPresent):
        st.session_state.home_page_content = read_and_trim_csv(keyAnalysisSummary)
    else:
        st.session_state.page = "no-data"
        st.rerun()

    file_content_order = read_file_from_s3(keyAnalysis)

    # print(keyAnalysis)
    st.session_state.order_page_content = generate_json_analysis(file_content_order)


    # print(file_content)
    # print(" ------------------ ")
    # print(st.session_state["order_page_content"])
    # print(" ------------------ ")


def home_page():
    if st.button("← Back To Form"):
        st.session_state.page = "user-list"
        st.rerun()
        return
    st.markdown(
        "<h1 style='text-align: center; color: #4CAF50; font-family: Arial, sans-serif;'>Outlet Data Viewer</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align: center; font-size: 16px; color: #555;'>Click on the row to see the details</p>",
        unsafe_allow_html=True
    )

    # print(type(st.session_state.get("home_page_content")))
    df = pd.DataFrame(st.session_state.get("home_page_content"))
    # print(df)
    custom_css = """
    <style>
        .ag-theme-alpine {
            --ag-header-background-color: #3a3a3a;
            --ag-header-foreground-color: white;
            --ag-odd-row-background-color: #f4f4f4;
            --ag-even-row-background-color: #ffffff;
            --ag-font-family: Arial, sans-serif;
            --ag-font-size: 14px;
        }
        .ag-header-cell-label {
            font-size: 14px;
            font-weight: bold;
            color: #f8f8f8;
        }
        .ag-cell {
            font-size: 13px;
            color: #333;
        }
        .ag-row-hover {
            background-color: #d9d9d9;
        }
        .ag-header {
            font-size: 16px;
        }
        .st-emotion-cache-13ln4jf{
            max-width: 90vw; !important
        }
    </style>
    """

    # Inject the custom CSS into the Streamlit app
    st.markdown(custom_css, unsafe_allow_html=True)

    # Configure grid options for lazy loading
    # print(home_page_content)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)  # Set initial page size
    gb.configure_selection("single")  # Enable row selection
    # gb.configure_grid_options(domLayout='autoHeight')  # Auto adjust grid height

    column_flex = 1  # This flex value can be adjusted to control the width distribution

    for col in df.columns:
        gb.configure_column(col, flex=column_flex)

    # grid_options = {
    # "pagination": True,
    # "sortable": True,
    # "filterable": True,
    # "selection_mode": "multiple",  # Enable multiple row selection
    # "rowSelection": "multiple",    # Specify multiple or single row selection
    # }

    grid_options = gb.build()

    # Create AgGrid component
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        height=600,
        width="100%",
        update_mode="MODEL_CHANGED",
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        key=f"grid_{st.session_state.get('page', 'home')}",
    )

    # Capture selected rows
    selected = grid_response["selected_rows"]
    # print(selected.columns)
    # selected = list(selected) if selected is not None else []
    # print(selected)
    if selected is not None and len(selected) > 0:
        st.write("Selected Row:", selected)
        st.session_state["login_id"] = selected["LOGINID"].tolist()[0]
        st.session_state["outlet_code"] = selected["OUTLET CODE"].tolist()[0]
        print(selected["LOGINID"])
        print(selected["OUTLET CODE"])
        st.session_state["page"] = "orders"
        print(st.session_state.get("login_id"))
        st.rerun()

# Orders Page - Display orders, recommendations, and sales
def orders_page():
    login_id = st.session_state.get("login_id")
    outlet_code = st.session_state.get("outlet_code")

    if st.button("← Back"):
        st.session_state.page = "home"
        st.rerun()
        return

    if login_id and outlet_code:
        st.subheader(f"Orders for Login ID: {login_id}, Outlet Code: {outlet_code}")
        
        user_key = f"{login_id}::{outlet_code}"
        if user_key in st.session_state.order_page_content:
            user_data = st.session_state.order_page_content[user_key]

            # Display orders
            if "orders" in user_data:
                st.write("### Orders")
                st.dataframe(pd.DataFrame(user_data["orders"]))

            # Display recommendations
            if "recommendation" in user_data:
                st.write("### Recommendations")
                st.dataframe(pd.DataFrame(user_data["recommendation"]))

            # Display sales
            if "sales" in user_data:
                st.write("### Sales")
                st.dataframe(pd.DataFrame(user_data["sales"]))
        else:
            st.warning(f"No data found for Login ID: {login_id}, Outlet Code: {outlet_code}")
    else:
        st.error("Login ID or Outlet Code not found. Please return to the home page.")

def user_list():
    st.markdown(
    "<h1 style='text-align: center; color: #4CAF50; font-family: Arial, sans-serif; margin-bottom: 30px'>ResponseG Report Analysis</h1>",
    unsafe_allow_html=True,
    )
    today = date.today()
    # yesterday = (arrow.now().shift(days=-1)).date()
    selected_lob = st.selectbox(
    "Choose lob:",
    lob_list
    )

    selected_date = st.date_input(
    label="📅 Select Date",
    max_value=today,
    value=today
    )

    if st.button(label="Click to view"):
    # Action to perform when button is clicked
        load_data(selected_lob, selected_date)
        st.session_state.page = "home"
        st.rerun()


def no_data_present():
    if st.button("← Back To Form"):
        st.session_state.page = "user-list"
        st.rerun()

    st.image(
    "static/nodatapresent.jpg",  # Replace with the path to your image file
    # caption="This is a static image",
    use_container_width=True  # Adjusts the image to the width of the container
    )


# Main app logic
def main():
    if "page" not in st.session_state:
       st.session_state["page"] = "user-list"  # Default to home page

    if st.session_state["page"] == "home":
        home_page()
    elif st.session_state["page"] == "orders":
        orders_page()
    elif st.session_state["page"] == "user-list":
        user_list()
    elif st.session_state["page"] == "no-data":
        no_data_present()


# Run the app
if __name__ == "__main__":
    main()
