import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page settings
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# ===== PROFESSIONAL DASHBOARD STYLE =====

st.markdown("""
<style>
/* Main dashboard background */
.stApp {
    background-color: #F4F7FB !important;
}

/* Content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Main title */
h1 {
    color: #17365D !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}

/* Section headings */
h2, h3 {
    color: #24476B !important;
    font-weight: 700 !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    padding: 20px !important;
    border-radius: 14px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 3px 10px rgba(23, 54, 93, 0.06);
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color: #64748B !important;
    font-weight: 600 !important;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color: #17365D !important;
    font-weight: 750 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #EAF0F8 !important;
}

/* Charts and other bordered containers */
[data-testid="stPlotlyChart"],
[data-testid="stAltairChart"] {
    background-color: #FFFFFF;
    border-radius: 14px;
    padding: 10px;
}

/* Buttons */
.stButton > button {
    background-color: #17365D;
    color: #FFFFFF;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #24476B;
    color: #FFFFFF;
    border: none;
}
</style>
""", unsafe_allow_html=True)


st.title("Sales Data Analysis Dashboard")
st.write("Explore sales performance using interactive filters.")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("sales_large.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["TotalSales"] = df["Quantity"] * df["UnitPrice"]
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "sales_large.csv was not found. "
        "Keep it in the same folder as dashboard.py."
    )
    st.stop()

    # --- Data Quality Checks ---
st.subheader("🛡️ Data Quality Checks")

missing_values = int(df.isnull().sum().sum())
duplicate_rows = int(df.duplicated().sum())
negative_sales = int((df["TotalSales"] < 0).sum())

col1, col2, col3 = st.columns(3)

col1.metric("Missing Values", missing_values)
col2.metric("Duplicate Rows", duplicate_rows)
col3.metric("Negative Sales Values", negative_sales)

if missing_values == 0 and duplicate_rows == 0 and negative_sales == 0:
    st.success("No basic data-quality issues detected!")
else:
    st.warning("Please review the data-quality issues above.")

# Sidebar filters
st.sidebar.header("Dashboard Filters")

products = st.sidebar.multiselect(
    "Choose products",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique())
)

regions = st.sidebar.multiselect(
    "Choose regions",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

filtered_df = df[
    df["Product"].isin(products)
    & df["Region"].isin(regions)
].copy()

if filtered_df.empty:
    st.warning("No sales match these filters.")
    st.stop()

# KPI calculations
total_revenue = filtered_df["TotalSales"].sum()
total_orders = filtered_df["OrderID"].nunique()
units_sold = filtered_df["Quantity"].sum()
average_order = total_revenue / total_orders

st.subheader("Sales Performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Units Sold", f"{units_sold:,}")
col4.metric("Avg. Order Revenue", f"₹{average_order:,.0f}")
# PROFESSIONAL KPI CARDS
st.subheader("📊 Sales Overview")

total_revenue = df["TotalSales"].sum()
total_orders = len(df)
total_quantity = df["Quantity"].sum()
average_order_value = (
    total_revenue / total_orders if total_orders else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Revenue", f"{total_revenue:,.2f}")
col2.metric("📦 Total Orders", f"{total_orders:,}")
col3.metric("🛒 Units Sold", f"{total_quantity:,}")
col4.metric("📈 Avg. Order Value", f"{average_order_value:,.2f}")

# Prepare charts
filtered_df["Month"] = (
    filtered_df["Date"].dt.to_period("M").astype(str)
)

monthly_sales = (
    filtered_df.groupby("Month")["TotalSales"]
    .sum()
    .sort_index()
)

product_sales = (
    filtered_df.groupby("Product")["TotalSales"]
    .sum()
    .sort_values()
)

region_sales = (
    filtered_df.groupby("Region")["TotalSales"]
    .sum()
    .sort_values()
)

# Monthly trend
st.subheader("Monthly Revenue Trend")
st.line_chart(monthly_sales)

# Product and region charts
left, right = st.columns(2)

with left:
    st.subheader("Revenue by Product")
    st.bar_chart(product_sales)

with right:
    st.subheader("Revenue by Region")
    st.bar_chart(region_sales)

# Data table
st.subheader("Sales Records")
st.dataframe(
    filtered_df.sort_values("Date"),
    use_container_width=True,
    hide_index=True
)

# Download filtered records
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Sales Data",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv"
)

st.caption(
    "Learning project using sample sales data. "
    "Figures are not actual company results."
)