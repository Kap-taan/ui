import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

st.markdown(
    """
    <style>
    .stApp {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='color: #4CAF50; font-family: Arial, sans-serif;'>Dynamic CrossSell Analysis</h1>",
    unsafe_allow_html=True,
)

lob_options = ["bepensa", "jnjaiph"]

selected_lob = st.selectbox("Select LOB", lob_options, index=0)
show_data_button = st.button(f"Show Data for {selected_lob}")

if show_data_button:
    file_path = Path(f"data/{selected_lob}_CrossSellAnalysisData.csv")

    if file_path.exists():
        df = pd.read_csv(file_path)

        if "Hit-Ratio%" in df.columns:
            avg_hit_ratio = df["Hit-Ratio%"].mean()

            st.metric(
                label="Average Hit-Ratio%",
                value=f"{avg_hit_ratio:.2f}%",
                help="Hit-Ratio% is calculated as: (Count of login-outlet with at least 1 matched cross-sell) / (Total login-outlets ordered)*100."
            )
        else:
            st.error("The column 'Hit-Ratio%' is missing in the dataset.")

        st.markdown(
            f"<h2 style='font-size: 18px; color: #4CAF50;'>Data for LOB: {selected_lob}</h2>", 
            unsafe_allow_html=True
        )
        
        st.dataframe(df)

        if "Date" in df.columns and "Hit-Ratio%" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values(by="Date")

            fig = px.bar(
                df, 
                x="Date", 
                y="Hit-Ratio%", 
                title=f"Hit-Ratio% V/S Time for {selected_lob}",
                labels={"Date": "Date", "Hit-Ratio%": "Hit-Ratio%"},
                color="Date", 
                color_continuous_scale="viridis"
            )

            fig.update_layout(
                xaxis_tickangle=90,
                xaxis_title="Date",
                yaxis_title="Hit-Ratio%",
                title_font=dict(size=14, family="Arial, sans-serif", color="#4CAF50"),
                xaxis=dict(tickmode="linear", ticks="outside", tickfont=dict(size=10)),
                yaxis=dict(tickfont=dict(size=10))
            )

            st.plotly_chart(fig)
        else:
            st.error("The required columns 'Date' and 'Hit-Ratio%' are not present in the dataset.")
    else:
        st.error(f"CSV file not found for LOB: {selected_lob}")
