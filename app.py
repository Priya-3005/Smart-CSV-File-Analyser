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
    if "df_processed" not in st.session_state:
        st.session_state.df_processed = df.copy()

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
    #df_selected = df[selected_columns]
    df_selected = st.session_state.df_processed[selected_columns]

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

    st.markdown("---")

    st.subheader("📊 Interactive Visualizations") 
    col1, col2 = st.columns(2)

    with col2:
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Histogram", "Boxplot", "Countplot"]
        )

    # Filter columns based on chart type
    if chart_type in ["Histogram", "Boxplot"]:
        st.caption("📌 Only numeric columns are available for this chart")
        valid_cols = df_selected.select_dtypes(include=['float64', 'int64']).columns
    else:
        st.caption("📌 Works best with categorical columns")
        valid_cols = df_selected.columns

    with col1:
        selected_col = st.selectbox("Select Column", valid_cols)
    
    fig, ax = plt.subplots(figsize=(12, 6))

    # Histogram
    if chart_type == "Histogram":
        if pd.api.types.is_numeric_dtype(df_selected[selected_col]):
            sns.histplot(df_selected[selected_col], kde=True, ax=ax)
            ax.set_title(f"Distribution of {selected_col}")
        else:
            st.warning("Histogram only works with numeric columns.")

    # Boxplot
    elif chart_type == "Boxplot":
        if pd.api.types.is_numeric_dtype(df_selected[selected_col]):
            sns.boxplot(x=df_selected[selected_col], ax=ax)
            ax.set_title(f"Boxplot of {selected_col}")
        else:
            st.warning("Boxplot only works with numeric columns.")

    # Countplot
    elif chart_type == "Countplot":
        top_n = st.slider("Select number of top categories", 5, 20, 10)
        top_categories = df_selected[selected_col].value_counts().nlargest(top_n).index
        sns.countplot(
            y=df_selected[selected_col],
            order=top_categories,
            ax=ax
        )
        ax.set_title(f"Top {top_n} categories in {selected_col}")

    st.pyplot(fig) 

    st.markdown("---") 

    st.subheader("🧠 Auto Insights") 

    # Missing values insight
    missing = df_selected.isnull().sum()
    missing_cols = missing[missing > 0].index.tolist()

    # High variance (numeric)
    numeric_df = df_selected.select_dtypes(include=['float64', 'int64'])
    high_variance_cols = [] 

    for col in numeric_df.columns:
        if numeric_df[col].std() > numeric_df[col].mean(): 
            high_variance_cols.append(col)
            #insights.append(f"📊 High variance detected in '{col}'")

    # Strong correlation 
    strong_corr_pairs = []
    if len(numeric_df.columns) > 1:
        corr_matrix = numeric_df.corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if abs(corr_matrix.iloc[i, j]) > 0.7:
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    strong_corr_pairs.append(f"{col1} ↔ {col2}")
                    #insights.append(f"🔗 Strong correlation between '{col1}' and '{col2}'")

    # Display insights
    if missing_cols:
        st.warning(f"⚠️ Missing values in: {', '.join(missing_cols)}")

    if high_variance_cols:
        st.info(f"📊 High variance detected in: {', '.join(high_variance_cols)}")

    if strong_corr_pairs:
        st.success("🔗 Strong correlations:")
        for pair in strong_corr_pairs:
            st.write(f"• {pair}")

    if not (missing_cols or high_variance_cols or strong_corr_pairs):
        st.success("✅ No major issues detected in dataset") 

    st.markdown("---")
    st.subheader("🚨 Outlier Detection")
    if not numeric_df.empty:
        outlier_col = st.selectbox("Select column for outlier detection", numeric_df.columns)

        Q1 = numeric_df[outlier_col].quantile(0.25)
        Q3 = numeric_df[outlier_col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = numeric_df[(numeric_df[outlier_col] < lower_bound) | (numeric_df[outlier_col] > upper_bound)]

        st.write(f"Number of outliers in '{outlier_col}': {outliers.shape[0]}")

        fig, ax = plt.subplots()
        sns.boxplot(x=numeric_df[outlier_col], ax=ax)
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("📌 Column Analysis") 

    col_analysis = st.selectbox("Select column for detailed analysis", df_selected.columns)

    if pd.api.types.is_numeric_dtype(df_selected[col_analysis]):
        st.write("### Numerical Summary")
        st.write(df_selected[col_analysis].describe())

        fig, ax = plt.subplots()
        sns.histplot(df_selected[col_analysis], kde=True, ax=ax)
        st.pyplot(fig)

    else:
        st.write("### Categorical Summary")
        st.write(df_selected[col_analysis].value_counts())

        fig, ax = plt.subplots(figsize=(10, 5))
        top_vals = df_selected[col_analysis].value_counts().nlargest(10)
        sns.barplot(x=top_vals.values, y=top_vals.index, ax=ax)
        st.pyplot(fig) 

    
    st.markdown("---") 

    st.subheader("🛠️ Data Cleaning & Processing") 
    if st.button("🔄 Reset Data"):
        st.session_state.df_processed = df.copy()
        st.success("Data reset to original") 
        st.rerun()
    st.markdown("### Handle Missing Values (Column-wise)")

    # Select column
    missing_cols = df_selected.columns[df_selected.isnull().any()]

    if len(missing_cols) > 0:

        selected_col = st.multiselect("Select columns", missing_cols)

        method = st.selectbox(
            "Choose method",
            ["None", "Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode"]
        )

        if method != "None":

            if method == "Drop Rows":
                before = df_selected.shape[0]
                df_selected = df_selected.dropna(subset=selected_col)
                after = df_selected.shape[0]

                st.success(f"Dropped {before - after} rows from '{selected_col}'")

            elif method == "Fill with Mean":

                for col in selected_col:

                    # Check type BEFORE doing anything
                    if not pd.api.types.is_numeric_dtype(df_selected[col]):
                        st.warning(f"'{col}' is categorical → Mean not applied")
                        continue

                    df_selected[col] = df_selected[col].fillna(df_selected[col].mean())

                st.success("Applied mean where valid")


            elif method == "Fill with Median":

                for col in selected_col:

                    if not pd.api.types.is_numeric_dtype(df_selected[col]):
                        st.warning(f"'{col}' is categorical → Median not applied")
                        continue

                    df_selected[col] = df_selected[col].fillna(df_selected[col].median())

                st.success("Applied median where valid")

            elif method == "Fill with Mode":
                for col in selected_col:
                    df_selected[col] = df_selected[col].fillna(df_selected[col].mode()[0])

                st.success("Applied mode") 
    else:
        st.success("No missing values detected 🎉") 
    st.session_state.df_processed = df_selected 

    st.markdown("### Remove Duplicates")

    if st.checkbox("Remove duplicate rows"):
        before = df_selected.shape[0]
        df_selected = df_selected.drop_duplicates()
        after = df_selected.shape[0]

        st.success(f"Removed {before - after} duplicate rows") 
    
    st.markdown("### Drop Columns")

    cols_to_drop = st.multiselect("Select columns to drop", df_selected.columns)

    if cols_to_drop:
        df_selected = df_selected.drop(columns=cols_to_drop)
        st.success(f"Dropped columns: {', '.join(cols_to_drop)}") 


    st.markdown("### Filter Data")

    filter_col = st.selectbox("Select column to filter", df_selected.columns)

    if pd.api.types.is_numeric_dtype(df_selected[filter_col]):
        min_val = float(df_selected[filter_col].min())
        max_val = float(df_selected[filter_col].max())

        selected_range = st.slider(
            "Select range",
            min_val,
            max_val,
            (min_val, max_val)
        )

        df_selected = df_selected[
            (df_selected[filter_col] >= selected_range[0]) &
            (df_selected[filter_col] <= selected_range[1])
        ]

    else:
        selected_values = st.multiselect(
            "Select values",
            df_selected[filter_col].unique()
        )

        if selected_values:
            df_selected = df_selected[df_selected[filter_col].isin(selected_values)]
    
    st.markdown("### 📄 Updated Dataset Preview")
    st.dataframe(df_selected.head())



    # Download Cleaned Data
    st.subheader("⬇️ Download Processed Data")
    csv = df_selected.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "processed_data.csv", "text/csv")

else:
    st.sidebar.info("👆Please upload a CSV file to get started.") 

st.markdown("---")
st.markdown("✨ Built by Priya | Smart CSV Analyzer")       