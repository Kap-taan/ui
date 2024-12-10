import pandas as pd
import streamlit as st
import plotly.express as px
import arrow
from s3 import isKeyExist, getDfFromS3
from lob_names import lob_list

# Configure page and styling
st.set_page_config(page_title="Supplier Data Visualization", layout="wide", page_icon="📊")
st.markdown("""
    <style>
        .main { background-color: #f5f5f5; }
        h1 { color: #4CAF50; text-align: center; }
        .stDateInput { text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Load the data from the CSV file
@st.cache_data(ttl=600)
def load_data(fileName):
    df = getDfFromS3(fileName, 0, 0, 0, False)
    # Optimize column data types
    df = df.astype({
        'supplier': 'category',
        'type': 'category',
        'factorToConsider': 'category',
        'product_code': 'category',
        'factor_value': 'float32'
    })
    return df

# Streamlit title
st.markdown("<h1>📊 Supplier Data Visualization Dashboard</h1>", unsafe_allow_html=True)

# Get today's and yesterday's dates using Arrow
today = arrow.now().date()
yesterday = (arrow.now().shift(days=-1)).date()

# Section: Date Input
st.markdown("### Select Date")
date = st.date_input(
    label="📅 Select Date",
    max_value=today,
    value=today
)
lob = st.selectbox(
    label="Select LOB",
    options=lob_list,
    index=lob_list.index("jnjaiph")
)

# Construct S3 file path
fileNameS3 = f"dumps/top_products_{lob}_{date}.csv"

print(fileNameS3)

# Check if the file exists in S3
if isKeyExist(fileNameS3):
    st.success(f"✅ Data file for **{date}** found: `{fileNameS3}`")

    # Load DataFrame
    df = load_data(fileNameS3)

    # Dynamic Filter Fields
    st.markdown("### Apply Filters")
    with st.form(key="filter_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            supplier = st.selectbox('Select Supplier', sorted(df['supplier'].unique()), key="supplier")

        with col2:
            data_type = st.selectbox('Select Type', sorted(df['type'].unique()), key="type")

        with col3:
            factor_to_consider = st.selectbox('Select Factor', sorted(df['factorToConsider'].unique()), key="factor")

        # Submit Button
        submit_button = st.form_submit_button("Apply Filters")

    # Filter and Display Data
    if submit_button:
        filtered_data = df[
            (df['supplier'] == supplier) &
            (df['type'] == data_type) &
            (df['factorToConsider'] == factor_to_consider)
        ]

        st.markdown(f"### Filtered Data: Supplier **{supplier}**, Type **{data_type}**, Factor **{factor_to_consider}**")
        if not filtered_data.empty:
            st.dataframe(filtered_data.style.set_properties(**{'background-color': '#f9f9f9', 'color': 'black'}))

            # Visualization Section
            st.markdown("### 📊 Interactive Visualization")

            # Create the bar plot for filtered data
            fig = px.bar(
                filtered_data,
                x='product_code',
                y='factor_value',
                color='product_code',
                title=f"{factor_to_consider} for Supplier: {supplier} and Type: {data_type}",
                labels={'product_code': 'Product Code', 'factor_value': 'Factor Value'},
                template='plotly_white'
            )
            fig.update_layout(
                xaxis_title="Product Code",
                yaxis_title="Factor Value",
                title_x=0.5,
                font=dict(family="Arial", size=14),
                title_font=dict(color="#1e3d59")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected filters.")
else:
    st.error(f"❌ No data available for the date **{date}**. Please select another date.")

# Footer
st.markdown("""
    <hr style='border: 1px solid #dcdcdc;' />
    <div style='text-align: center; font-size: 12px; color: #888;'>
        Developed by <strong>The Mechanic</strong>
    </div>
""", unsafe_allow_html=True)
