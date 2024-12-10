import streamlit as st
from datetime import date
from lob_names import lob_list
from datetime import date, timedelta
from convert_to_utc import convert_to_utc;
from time_zone import time_zone_map;
from targetAnalysis import target_pjp_compliance
from s3 import isKeyExist
import pandas as pd
import numpy as np
import plotly.express as px

userList = {};

def home_page():
    st.markdown(
    "<h1 style='text-align: center; color: #4CAF50; font-family: Arial, sans-serif; margin-bottom: 30px'>Target Competition Analysis</h1>",
    unsafe_allow_html=True,
    )
    today = date.today()
    # yesterday = (arrow.now().shift(days=-1)).date()
    selected_lob = st.selectbox(
    "Choose lob:",
    lob_list
    )

    if st.button(label="Click to view"):
    # Action to perform when button is clicked
        targetList(selected_lob)
        # st.session_state.page = "home"
        # st.rerun()


# String name="dailyTargetReport/dailyUserTarget"+ ApplicationContext.get().getLob()+"_"+clientDate+".csv";

def generate_key(lob, clientDate):
    return f"dailyTargetReport/dailyUserTarget{lob}_{clientDate}.csv"


def targetList(lob):
    for i in range(10,30):  # range(start, stop) where stop is exclusive
        date_obj = date.today() - timedelta(i)
        utc_time = convert_to_utc(date_obj, time_zone_map[lob]["tz"])
        # print(utc_time.split("+")[0])
        key = generate_key(lob, utc_time);
        isKeyPresent = isKeyExist(key);
        # print(key)
        if(isKeyPresent):
            user = target_pjp_compliance(key, 0.3)
            # print(user)
            # print("------------------------------------")
            for user_name, details in user.items():
    # Extract the date part of the utc_time
                date_part = utc_time.split(" ")[0]
                
                # If the user already exists in userList, append to the list; otherwise, create a new list
                if user_name not in userList:
                    userList[user_name] = []  # Initialize a list if the user is not in userList

                # Append the new status entry with the date
                # print(details.user2use)
                userList[user_name].append({
                    date_part: details.user2use
                })
        # else:
        #     print("file not present")
    # print(userList)
    st.session_state.user_list = userList
    st.session_state.page4 = "user-list";
    st.rerun();
    

def user_list():
    # Initialize a list to store formatted data
    formatted_data = []
    all_dates = set()

    if st.button("← Back"):
        st.session_state.page4 = "home"
        st.rerun()

    # Iterate through each user and their associated date-status mappings
    for user, date_status in st.session_state["user_list"].items():
        for entry in date_status:
            for date, status in entry.items():
                formatted_data.append({'User': user, 'Date': date, 'Status': status})
                all_dates.add(date)

    # Print intermediate formatted data to debug
    # print("Formatted Data:", formatted_data)

    # Check if the formatted_data list is not empty
    if not formatted_data:
        st.warning("No data found to display.")
        return

    # Create a DataFrame from the formatted data
    df = pd.DataFrame(formatted_data)

    # Print the DataFrame to debug
    # print("DataFrame:", df)

    # summary_df = df.groupby(['Date', 'Status']).size().unstack(fill_value=0)
    # summary_df['total_pjp_outlet'] = summary_df['PJP'] + summary_df['ML'] + summary_df['BOTH'];

    # summary_df['pjp_win%'] = (summary_df['PJP'] * 100 )/ summary_df['total_pjp_outlet'];
    # summary_df['ml_win%'] = (summary_df['ML'] * 100 )/ summary_df['total_pjp_outlet'];

    # summary_df['pjp_win%'] = summary_df['pjp_win%'].fillna(0)
    # summary_df['ml_win%'] = summary_df['ml_win%'].fillna(0)

    # # Optionally, round to two decimal places
    # summary_df['pjp_win%'] = summary_df['pjp_win%'].round(2)
    # summary_df['ml_win%'] = summary_df['ml_win%'].round(2)

    # print(summary_df)

    # Pivot the table so that 'Date' becomes columns
    pivot_df = df.pivot(index='User', columns='Date', values='Status')

    # Ensure all dates are present as columns
    pivot_df = pivot_df.reindex(columns=sorted(all_dates, reverse=True))

    # Display the pivoted table using Streamlit
    st.markdown(
        "<p style='text-align: end; font-size: 13px; color: #555;'>Considered the Threshold of 30%</p>",
        unsafe_allow_html=True
    )
    st.write("### User Status Table", pivot_df)



    st.markdown("<br></br><br></br>", unsafe_allow_html=True)
    # fig = px.line(summary_df, x='Date', y=['pjp_win%', 'ml_win%'], 
    #           title="Win Percentage Over Time",
    #           labels={'value': 'Win%', 'variable': 'Type'},
    #           markers=True)

    summary_df = df.groupby(['Date', 'Status']).size().unstack(fill_value=0)

# Calculating total_pjp_outlet and win percentages
    summary_df['total_pjp_outlet'] = summary_df['PJP'] + summary_df['ML'] + summary_df['BOTH']
    summary_df['pjp_win%'] = (summary_df['PJP'] * 100) / summary_df['total_pjp_outlet']
    summary_df['ml_win%'] = (summary_df['ML'] * 100) / summary_df['total_pjp_outlet']

    # Fill NaN values with 0 and round percentages
    summary_df['pjp_win%'] = summary_df['pjp_win%'].fillna(0).round(2)
    summary_df['ml_win%'] = summary_df['ml_win%'].fillna(0).round(2)

    # Reset index to make 'Date' a column
    summary_df.reset_index(inplace=True)

    # Plot using Plotly
    fig = px.line(
        summary_df,
        x='Date',  # Ensure Date is treated as a column, not an index
        y=['pjp_win%', 'ml_win%'],
        title="Win Percentage Over Time",
        labels={'value': 'Win%', 'variable': 'Type'},
        markers=True
    )
    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            dtick="D1",  # Show every day (D1 = daily)
            tickformat="%Y-%m-%d",  # Format the date as "YYYY-MM-DD"
        )
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)


    # Custom CSS for increasing size
    

def main():
    if "page4" not in st.session_state:
       st.session_state["page4"] = "home"  # Default to home page
    # print(st.session_state["page4"])
    if st.session_state["page4"] == "home":
        home_page()
    elif st.session_state["page4"] == "orders":
        orders_page()
    elif st.session_state["page4"] == "user-list":
        user_list()
    elif st.session_state["page4"] == "no-data":
        no_data_present()
    


# Run the app
if __name__ == "__main__":
    main()