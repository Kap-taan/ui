import streamlit as st
import json
import pandas as pd

# Load the initial JSON data
json_filename = "data/analysisSummaryBepensa.json"

# Use st.cache_data to cache the loading of the JSON data

# def load_outlet_data():
#     with open(json_filename, "r") as file:
#         outlet_data = json.load(file)
#     return outlet_data

# # Convert JSON data to a DataFrame, splitting the key into separate columns
# data = [
#     {
#         "Login ID": key.split("::")[0],
#         "Outlet Code": key.split("::")[1],
#         "New SKU Count": value
#     }
#     for key, value in load_outlet_data().items()
# ]
# df = pd.DataFrame(data)

# # Streamlit UI
# st.title("Outlet Data Viewer")
# st.write("This app displays outlet data with a button to view details for each row.")

# # Display headers explicitly
# st.subheader("Data Table")
# header_cols = st.columns((1, 1, 1, 1))
# header_cols[0].write("Login ID")
# header_cols[1].write("Outlet Code")
# header_cols[2].write("New SKU Count")
# header_cols[3].write("Actions")

# # Iterate through rows to add a button for each
# for index, row in df.iterrows():
#     cols = st.columns((1, 1, 1, 1))  # Create columns for layout
#     cols[0].write(row["Login ID"])  # Login ID column
#     cols[1].write(row["Outlet Code"])  # Outlet Code column
#     cols[2].write(row["New SKU Count"])  # New SKU Count column
#     if cols[3].button("Show Details", key=f"details_{index}"):
#         # Action to display detailed information
#         st.write(f"Details for Login ID: {row['Login ID']}, Outlet Code: {row['Outlet Code']}, New SKU Count: {row['New SKU Count']}")

json_filename = "data/analysisSummaryBepensa.json"

# Function to load outlet data from JSON
def load_outlet_data():
    with open(json_filename, "r") as file:
        outlet_data = json.load(file)
    return outlet_data

# def go_to_orders(login_id=None, outlet_code=None):
#     """This function receives arguments and displays details based on them."""
#     if login_id and outlet_code:
#         st.write(f"Displaying details for Order ID: {login_id} and Outlet Code: {outlet_code}")
#     else:
#         st.write("No order or outlet code passed.")


# Function to convert JSON data into a DataFrame
def convert_json_to_df():
    data = json.loads(json_data)

# Convert JSON data into DataFrame
    df = pd.DataFrame(data)
    return df

def home_page():
    st.title("Outlet Data Viewer")
    st.write("This app displays outlet data with a button to view details for each row.")
    
    # Fetch data and display
    df = convert_json_to_df()

    # Display headers explicitly (this part ensures better control over layout)
    st.subheader("Data Table")
    header_cols = st.columns([1] * 13) 
    header_cols[0].write("OUTLET CODE")
    header_cols[1].write("LOGINID")
    header_cols[2].write("CommonSKU ORderRec")
    header_cols[3].write("ORDER_SKUCOUNT")
    header_cols[4].write("RECOMENDED_ALL_COUNT")
    header_cols[5].write("NEW SKU COUNT")
    header_cols[6].write("RECALL")
    header_cols[7].write("PRECESSION")
    header_cols[8].write("CROSSELL_MATCH")
    header_cols[9].write("do manual ANALYSIS")
    header_cols[10].write("WHAT is REASON")
    header_cols[11].write("CROSSELL_DETAILS")
    header_cols[12].write("Actions")

    # Iterate through rows to add a button for each
    for index, row in df.iterrows():
        cols = st.columns([1] * 13)   # Create columns for layout
        cols[0].write("OUTLET CODE")
        cols[1].write("LOGINID")
        cols[2].write("CommonSKU ORderRec")
        cols[3].write("ORDER_SKUCOUNT")
        cols[4].write("RECOMENDED_ALL_COUNT")
        cols[5].write("NEW SKU COUNT")
        cols[6].write("RECALL")
        cols[7].write("PRECESSION")
        cols[8].write("CROSSELL_MATCH")
        cols[9].write("do manual ANALYSIS")
        cols[10].write("WHAT is REASON")
        cols[11].write("CROSSELL_DETAILS")
        cols[12].write("Actions")

        # Creating a unique key using index, Login ID, and Outlet Code
        # Adding the index to the key for uniqueness
        button_key = f"details_{index}_{row['Login ID']}_{row['Outlet Code']}_{row['New SKU Count']}"
        
        # Debugging: Print the button_key to check for duplicates
        st.write(f"Generated button key: {button_key}")  # Debugging line
        
        if cols[12].button("Show Details", key=button_key):
            # # Action to display detailed information when button is clicked
            login_id = row["Login ID"]  # Get the Login ID from the current row
            outlet_code = row["Outlet Code"]  # Get the Outlet Code from the current row
            
            # Store in session state to pass to another page
            st.session_state.login_id = login_id
            st.session_state.outlet_code = outlet_code
            st.session_state.page = "orders"
            print("button")



# home_page();