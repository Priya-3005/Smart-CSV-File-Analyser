import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Smart CSV Analyzer", layout="wide")

st.title("📊 Smart CSV Analyzer")
st.markdown("Analyze, clean, and visualize your data interactively.")
st.write("Upload a CSV file and get instant insights!")
st.sidebar.header("📂 Upload & Settings")
# File Upload
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📌 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())
    col4.metric("Duplicate Rows", df.duplicated().sum())

    # DATA PREVIEW
    st.subheader("🔍 Data Preview")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.dataframe(df.head())

    with col2:
        st.write("### Column Info")
        st.write(df.dtypes)

    # Column Selection
    st.sidebar.subheader("📌 Select Columns to Analyse")
    selected_columns = st.sidebar.multiselect("Choose columns", df.columns, default=df.columns)
    df_selected = df[selected_columns]

    st.markdown("---")

    # Missing Values
    st.subheader("❗ Missing Value Analysis")
    missing = df_selected.isnull().sum()
    st.write(missing[missing > 0])

    # Fill Missing Values Option
    if st.checkbox("Fill missing values with mean (numeric only)"):
        df_selected = df_selected.fillna(df_selected.mean(numeric_only=True))
        st.success("Missing values filled!")

    st.markdown("---")

    # Statistical Summary
    st.subheader("📊 Statistical Summary")
    st.write(df_selected.describe()) 

    st.markdown("---")

    # Correlation Heatmap
    st.subheader("🔥 Correlation Heatmap")
    numeric_df = df_selected.select_dtypes(include=['float64', 'int64'])

    if not numeric_df.empty:
        st.markdown("### Select columns for correlation")

        heatmap_cols = st.multiselect(
            "Choose columns",
            numeric_df.columns,
            default=numeric_df.columns[:5]  # limit default to first 5
        )
        if len(heatmap_cols) > 1:
            fig, ax = plt.subplots(figsize=(10, 6))

            sns.heatmap(
                numeric_df[heatmap_cols].corr(),
                annot=True,
                cmap="coolwarm",
                ax=ax,
                annot_kws={"size": 8}
            )

            plt.xticks(rotation=45)
            plt.yticks(rotation=0)
            st.pyplot(fig) 
        else:
            st.warning("Please select at least 2 columns for correlation.")       
    else:
        st.warning("No numeric columns available for correlation heatmap.")

    # Download Cleaned Data
    st.subheader("⬇️ Download Processed Data")
    csv = df_selected.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "processed_data.csv", "text/csv")

else:
    st.info("👆 Please upload a CSV file to get started.") 

st.markdown("---")
st.markdown("✨ Built by Priya | Smart CSV Analyzer")       