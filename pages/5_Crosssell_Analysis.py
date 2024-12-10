import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import arrow
from s3 import isKeyExist, getDfFromS3

lob_list = ['marssfain', 'jnjaiph', 'bepensa']

# Title with custom styling and an icon
st.markdown("<h1 style='text-align: center; color: #4CAF50; font-family: Arial, sans-serif;'>Crosssell Analysis</h1>", unsafe_allow_html=True)
# st.markdown("<h3 style='text-align: center; color: #333333;'>Analyze Product Trends Across Orders and Machine Learning Recommendations</h3>", unsafe_allow_html=True)

today = arrow.now()
yesterday = today.shift(days=-1).date()

# Form for input
with st.form(key="trending_data_form"):
    lob = st.selectbox(
        label="Select LOB",
        options=lob_list,
        index=lob_list.index("marssfain")
    )
    date = st.date_input(label="Enter the date of recommendation")

    submit_button = st.form_submit_button("Submit")

# Dynamically generate the file path
fileNameS3 = f'dumps/trendingcrosssellorder_responseG_data_{lob}_{date}.csv'

# Check if file exists and is not empty
if isKeyExist(fileNameS3):
    # st.balloons()   

    # Define columns
    columns = [
        "LOGINID","OUTLETCODE","CROSSSELL_IN_ORDERS","CROSSSELL_IN_RECOMMENDATIONS","MATCHED_CROSSSELL"
    ]

    # Read the file into a dataframe
    # df = getDfFromS3(fileNameS3, 1, columns, 13, True)
    range_value = len(columns)
    # df = pd.read_csv("data/trendingorder_responseG_data_marssfain_2024-12-04.csv",header=None, names=columns,usecols=range(range_value),skiprows=1)
    df = getDfFromS3(fileNameS3, 1,columns, range_value,True)

    # Check if the dataframe is empty
    if df.empty:
        st.warning("The file is empty. No data to display.")
    # if True:
    else:
        st.subheader("Metrics")
        # filted_skus = df.query("IS_TRENDING_CROSSSELL_IN_RECOMMENDATION_AND_ORDERS == True")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="No. of outlets ordered", value=len(df))
            st.metric(label="Average Crosssell in orders", value=f"{round(df['CROSSSELL_IN_ORDERS'].mean())}")
            # st.metric(label = "Outlets where trending crosssell is purchased", value = f"{filted_skus.shape[0]}")

        with col2:
            st.metric(label="Average Crosssell in recommendations", value=f"{round(df['CROSSSELL_IN_RECOMMENDATIONS'].mean())}")
            # st.metric(label = "Outlets where crossell matched", value = f"{df.query('MATCHED_CROSSSELL >= 1').shape[0]}")
    

        st.markdown("---")

        # Effect of trending products on orders
        st.subheader("Effect of Crosssell Products on Orders")
        # df_without = df.drop(['IS_TRENDING_CROSSSELL_IN_RECOMMENDATION_AND_ORDERS'], axis=1)
        st.dataframe(df)  # Display the dataframe

else:
    # If file doesn't exist or is empty, show a placeholder image
    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        st.image(os.path.join(os.getcwd(), "static", "nodatapresent.jpg"), width=1700)
