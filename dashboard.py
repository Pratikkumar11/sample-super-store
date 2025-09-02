import streamlit as st
import plotly.express as px
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# ------------------ Page Config ------------------
st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Sample SuperStore EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# ------------------ File Upload ------------------
fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))

def read_input(upl):
    if upl is not None:
        filename = upl.name
        if filename.endswith(".csv") or filename.endswith(".txt"):
            return pd.read_csv(upl, encoding="ISO-8859-1")
        else:
            return pd.read_excel(upl)
    else:
        st.warning("⚠️ Please upload a dataset to continue.")
        st.stop()

df = read_input(fl)

# Show available columns for debugging
st.write("✅ Columns in dataset:", df.columns.tolist())

# ------------------ Date Column Handling ------------------
date_col = None
for candidate in ["Order Date", "Order_Date", "Date", "InvoiceDate"]:
    if candidate in df.columns:
        date_col = candidate
        break

if date_col is None:
    st.error("❌ No valid date column found! Please check your dataset.")
    st.stop()

# Convert to datetime
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ------------------ Date Range Filter ------------------
col1, col2 = st.columns((2))

startDate = df[date_col].min()
endDate = df[date_col].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df[date_col] >= date1) & (df[date_col] <= date2)].copy()

# ------------------ Sidebar Filters ------------------
st.sidebar.header("Choose your filter: ")

region = st.sidebar.multiselect("Pick your Region", df["Region"].unique() if "Region" in df.columns else [])
if region:
    df = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick the State", df["State"].unique() if "State" in df.columns else [])
if state:
    df = df[df["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City", df["City"].unique() if "City" in df.columns else [])
if city:
    df = df[df["City"].isin(city)]

# ------------------ Category-wise Sales ------------------
if "Category" in df.columns and "Sales" in df.columns:
    category_df = df.groupby(by=["Category"], as_index=False)["Sales"].sum()

    col1, col2 = st.columns((2))
    with col1:
        st.subheader("Category wise Sales")
        fig = px.bar(category_df, x="Category", y="Sales",
                     text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                     template="seaborn")
        st.plotly_chart(fig, use_container_width=True, height=200)

    with col2:
        if "Region" in df.columns:
            st.subheader("Region wise Sales")
            fig = px.pie(df, values="Sales", names="Region", hole=0.5)
            st.plotly_chart(fig, use_container_width=True)

# ------------------ Time Series ------------------
if "Sales" in df.columns:
    df["month_year"] = df[date_col].dt.to_period("M")
    st.subheader('Time Series Analysis')
    linechart = pd.DataFrame(df.groupby(df["month_year"].dt.strftime("%Y-%b"))["Sales"].sum()).reset_index()
    fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"},
                   height=500, width=1000, template="gridon")
    st.plotly_chart(fig2, use_container_width=True)

# ------------------ Download Final Dataset ------------------
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="FilteredData.csv", mime="text/csv")
