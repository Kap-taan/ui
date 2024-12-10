import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import arrow
from s3 import isKeyExist, getDfFromS3

lob_list = ['marssfain']

# Title with custom styling and an icon
st.markdown("<h1 style='text-align: center; color: #4CAF50; font-family: Arial, sans-serif;'>Trending Product Analysis</h1>", unsafe_allow_html=True)
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
fileNameS3 = f'dumps/trendingorder_responseG_data_{lob}_{date}.csv'

# Check if file exists and is not empty
if isKeyExist(fileNameS3):
    # st.balloons()   

    # Define columns
    columns = [
        "LOGINID", "OUTLETCODE", "TOTAL_ORDERS", "ORDERS_AND_(SALES_OR_RECOMMENDATION)", "TRENDING_IN_ORDERS", 
        "TRENDING_IN_RECOMMENDATIONS", "TOTAL_RECOMMENDATIONS", "MATCHED_TRENDING_RECOMMENDATIONS", 
        "TRENDING_RECALL", "TRENDING_COVERAGE"
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
        df['TRENDING_PRECISION'] = (df['MATCHED_TRENDING_RECOMMENDATIONS'] / df['TRENDING_IN_RECOMMENDATIONS']) * 100
        df['TRENDING_PRECISION'] = df['TRENDING_PRECISION'].fillna(0)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="No. of outlets ordered", value=len(df))
            st.metric(label="Average trending_recall", value=f"{round(df['TRENDING_RECALL'].mean())}%")
            # st.metric(label="Average harsh_ratio", value=f"{(df.query('HARSH_RATIO == 1').shape[0] / df.shape[0]) * 100:.2f}%")
            st.metric(label="Average of trending_coverage", value=f"{round(df['TRENDING_COVERAGE'].mean())}%")
            st.metric(label = "Average of trending_precision", value = f"{round(df['TRENDING_PRECISION'].mean())}%")

        with col2:
            st.metric(label = "Loginid-outlet pairs having trending_recall above 60%", value=f"{df.query('TRENDING_RECALL >= 60').shape[0]}")
            # st.metric(label = "Loginid-outlet pairs having harsh ratio as 1 ", value=f"{df.query('HARSH_RATIO == 1').shape[0]}")
            # st.metric(label = "Loginid-outlet pairs having trending_coverage >= 20%", value=f"{df.query('TRENDING_COVERAGE >= 20').shape[0]}")
            st.metric(label = "Loginid-outlet pairs having trending_coverage >= 50%", value=f"{df.query('TRENDING_COVERAGE >= 50').shape[0]}")
            st.metric(label = "Loginid-outlet pairs having trending_precision >= 70%", value = f"{df.query('TRENDING_PRECISION >= 30').shape[0]}")

        st.markdown("---")

        # st.subheader("Model Performance Analysis")

        # **Harsh Ratio** : The space we are giving in recommendation is worth or not.

        # st.write("""
        # **Prince Ratio** : Shows our model's choosing capacity.

        # **Vanshika Ratio** : Indicates whether we are choosing the correct products as trending products.
        # """)

        # Display the formulas and ratios
        # st.write("### Ratios Calculations:")

        # Prince Ratio formula and metric
        # st.write("""
        # - **Prince Ratio**: (Matched trending products in orders and recommendations / Trending products in order) * 100
        # """)

        # Vanshika Ratio formula and metric
        # st.write("""
        # - **Vanshika Ratio**: (Trending products in orders / Ordered items only from past sales and recommendations) * 100
        # """)

        # Harsh Ratio formula and metric
        # st.write("""
        # - **Harsh Ratio**: Matched trending products in orders and recommendations / Trending products in recommendations >= Matched recommendations other than matched trending products / Total recommendation other than trending products ? 1 : 0
        # """)

        # st.markdown("---")

        # Effect of trending products on orders
        st.subheader("Effect of Trending Products on Orders")
        st.dataframe(df)  # Display the dataframe

        # Prince ratio graph
        st.subheader("Trending Recall Analysis")
        st.write("Interactive bar chart showing No. of Outlets vs Trending Recall.")
        filtered_df_prince = df[df["TRENDING_RECALL"] >= 0]

        bin_edges = np.arange(0, filtered_df_prince["TRENDING_RECALL"].max() + 20, 20)
        bin_labels = [f"{int(edge)}-{int(edge+20)}" for edge in bin_edges[:-1]]
        filtered_df_prince["PRINCE_RATIO_BIN"] = pd.cut(
            filtered_df_prince["TRENDING_RECALL"], bins=bin_edges, labels=bin_labels, right=True, include_lowest=True
        )


        print(filtered_df_prince[['TRENDING_RECALL', 'PRINCE_RATIO_BIN']])

        # Group by bins and count outlets
        prince_ratio_counts = (
            filtered_df_prince.groupby("PRINCE_RATIO_BIN")["OUTLETCODE"]
            .count()
            .reset_index()
            .rename(columns={"OUTLETCODE": "No_of_outlets"})
        )

        # Set bin labels as index for the chart
        prince_ratio_counts.set_index("PRINCE_RATIO_BIN", inplace=True)

        # Create the bar chart
        st.bar_chart(prince_ratio_counts["No_of_outlets"])

        # Vanshika ratio graph
        st.subheader("Trending coverage Analysis")
        st.write("Interactive bar chart showing No. of Outlets vs TRENDING_COVERAGE.")
        filtered_df_vanshika = df[df["TRENDING_COVERAGE"] >= 0]

        bin_edges = np.arange(0, filtered_df_vanshika["TRENDING_COVERAGE"].max() + 20, 20)
        filtered_df_vanshika["VANSHIKA_RATIO_BIN"] = pd.cut(
            filtered_df_vanshika["TRENDING_COVERAGE"], bins=bin_edges, labels=bin_labels, right=True, include_lowest=True
        )

        vanshika_ratio_counts = (
                filtered_df_vanshika.groupby("VANSHIKA_RATIO_BIN")["OUTLETCODE"]
                .count()
                .reset_index()
                .rename(columns={"OUTLETCODE": "No_of_outlets"})
        )

        vanshika_ratio_counts.set_index("VANSHIKA_RATIO_BIN", inplace=True)

        st.bar_chart(vanshika_ratio_counts["No_of_outlets"])

        # Harsh ratio graph
        # st.subheader("Harsh ratio Analysis")
        # st.write("Interactive bar chart showing No. of Outlets vs HARSH_RATIO.")
        # filtered_df_harsh = df[df["HARSH_RATIO"] >= 0]

        # harsh_ratio_counts = (
        #         filtered_df_harsh.groupby("HARSH_RATIO")["OUTLETCODE"]
        #         .count()
        #         .reset_index()
        #         .rename(columns={"OUTLETCODE": "No_of_outlets"})
        #         .sort_values(by="HARSH_RATIO", ascending=False)
        # )

        # harsh_ratio_counts.set_index("HARSH_RATIO", inplace=True)

        # st.bar_chart(harsh_ratio_counts["No_of_outlets"])


        # Footer caption with style
        # st.markdown("<p style='text-align: center; color: gray; font-style: italic;'>Made and designed by The Mechanic</p>", unsafe_allow_html=True)

else:
    # If file doesn't exist or is empty, show a placeholder image
    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        st.image(os.path.join(os.getcwd(), "static", "nodatapresent.jpg"), width=1700)
