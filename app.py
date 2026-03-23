import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Smart CSV Analyzer", layout="wide") 
st.markdown("""
<style>

/* Main background */
[data-testid="stAppViewContainer"] {
    background: #0e1117;
    color: #ffffff;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1c1f26;
}

/* Title */
h1 {
    color: #ffffff;
    font-weight: 700;
}

/* Subheaders */
h2, h3 {
    color: #e6e6e6;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 8px 16px;
    font-weight: 600;
}

.stButton>button:hover {
    transform: scale(1.05);
}

/* Metrics */
[data-testid="metric-container"] {
    background: #1c1f26;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 10px;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #1c1f26;
    padding: 10px;
    border-radius: 10px;
}

/* Section spacing */
.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)
#st.title("📊 Smart CSV Analyzer") 
st.markdown("<h1>📊 Smart CSV Analyzer</h1>", unsafe_allow_html=True)
#st.markdown("Analyze, clean, and visualize your data interactively.")
st.markdown(
    "<p style='color:#b0b3b8;'>Analyze, clean, and visualize your data interactively.</p>",
    unsafe_allow_html=True
)
st.write("Upload a CSV file and get instant insights!")
st.sidebar.header("📂 Upload & Settings")
# File Upload
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file) 
    if "df_processed" not in st.session_state:
        st.session_state.df_processed = df.copy() 
    if "dropped_columns" not in st.session_state:
        st.session_state.dropped_columns = []

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
    #df_selected = st.session_state.df_processed[selected_columns] 
    df_selected = st.session_state.df_processed[ [col for col in selected_columns if col in st.session_state.df_processed.columns] ]
    # Apply dropped columns (virtual drop)
    # df_selected = df_selected.drop(
    #     columns=st.session_state.dropped_columns,
    #     errors='ignore'
    # )


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

    # st.subheader("🛠️ Data Cleaning & Processing") 
    # if st.button("🔄 Reset Data"):
    #     st.session_state.df_processed = df.copy()
    #     st.success("Data reset to original") 
    #     st.rerun()
    # st.markdown("### Handle Missing Values (Column-wise)")

    # # Select column
    # missing_cols = df_selected.columns[df_selected.isnull().any()]

    # if len(missing_cols) > 0:

    #     selected_col = st.multiselect("Select columns", missing_cols)

    #     method = st.selectbox(
    #         "Choose method",
    #         ["None", "Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode"]
    #     )

    #     if method != "None":

    #         if method == "Drop Rows":
    #             before = df_selected.shape[0]
    #             df_selected = df_selected.dropna(subset=selected_col)
    #             after = df_selected.shape[0]

    #             st.success(f"Dropped {before - after} rows from '{selected_col}'")

    #         elif method == "Fill with Mean":

    #             for col in selected_col:

    #                 # Check type BEFORE doing anything
    #                 if not pd.api.types.is_numeric_dtype(df_selected[col]):
    #                     st.warning(f"'{col}' is categorical → Mean not applied")
    #                     continue

    #                 df_selected[col] = df_selected[col].fillna(df_selected[col].mean())

    #             st.success("Applied mean where valid")


    #         elif method == "Fill with Median":

    #             for col in selected_col:

    #                 if not pd.api.types.is_numeric_dtype(df_selected[col]):
    #                     st.warning(f"'{col}' is categorical → Median not applied")
    #                     continue

    #                 df_selected[col] = df_selected[col].fillna(df_selected[col].median())

    #             st.success("Applied median where valid")

    #         elif method == "Fill with Mode":
    #             for col in selected_col:
    #                 df_selected[col] = df_selected[col].fillna(df_selected[col].mode()[0])

    #             st.success("Applied mode") 
    # else:
    #     st.success("No missing values detected 🎉") 
    # st.session_state.df_processed = df_selected 

    st.subheader("🛠️ Data Cleaning & Processing") 

    # 🔥 INIT OPERATIONS STORAGE
    if "operations" not in st.session_state:
        st.session_state.operations = {}

    # 🔥 RESET ONLY OPERATIONS (NOT FULL DATA LOSS)
    if st.button("🔄 Reset All Cleaning"):
        st.session_state.operations = {}
        st.success("All cleaning operations cleared")
        st.rerun()

    st.markdown("### Handle Missing Values (Column-wise)")

    col_clean = st.selectbox("Select column", df_selected.columns)

    method = st.selectbox(
        "Choose method",
        ["None", "Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode"]
    )

    # 🔥 APPLY BUTTON (IMPORTANT CHANGE)
    if st.button("➕ Apply Operation"):
        if method != "None":
            st.session_state.operations[col_clean] = method
            st.success(f"{method} will be applied to '{col_clean}'")

    # 🔥 SHOW ACTIVE OPERATIONS
    if st.session_state.operations:
        st.write("### 🧾 Active Cleaning Operations")
        st.write(st.session_state.operations)

    # 🔥 APPLY ALL OPERATIONS TO DATA
    df_processed = df_selected.copy()

    for col, op in st.session_state.operations.items():

        if col not in df_processed.columns:
            continue

        if op == "Drop Rows":
            df_processed = df_processed.dropna(subset=[col])

        elif op == "Fill with Mean":
            if pd.api.types.is_numeric_dtype(df_processed[col]):
                df_processed[col] = df_processed[col].fillna(df_processed[col].mean())

        elif op == "Fill with Median":
            if pd.api.types.is_numeric_dtype(df_processed[col]):
                df_processed[col] = df_processed[col].fillna(df_processed[col].median())

        elif op == "Fill with Mode":
            df_processed[col] = df_processed[col].fillna(df_processed[col].mode()[0]) 

    # 🔥 UPDATE SESSION DATA (FINAL OUTPUT)
    st.session_state.df_processed = df_processed
  

#     st.markdown("### Remove Duplicates")

#     if st.checkbox("Remove duplicate rows"):
#         before = df_selected.shape[0]
#         df_selected = df_selected.drop_duplicates()
#         after = df_selected.shape[0]

#         st.success(f"Removed {before - after} duplicate rows") 
    
#     # st.markdown("### Drop Columns")

#     # cols_to_drop = st.multiselect("Select columns to drop", df_selected.columns)

#     # if cols_to_drop:
#     #     df_selected = df_selected.drop(columns=cols_to_drop)
#     #     st.success(f"Dropped columns: {', '.join(cols_to_drop)}") 

#     st.markdown("### Drop Columns")

#     cols_to_drop = st.multiselect(
#         "Select columns to drop",
#         df.columns,   # IMPORTANT: use original dataset
#         default=st.session_state.dropped_columns
#     )

#     # Store selection (NOT dropping immediately)
#     st.session_state.dropped_columns = cols_to_drop

#     if cols_to_drop:
#         st.warning(f"Currently dropped: {', '.join(cols_to_drop)}")


#     st.markdown("### Filter Data")

#     filter_col = st.selectbox("Select column to filter", df_selected.columns)

#     if pd.api.types.is_numeric_dtype(df_selected[filter_col]):
#         min_val = float(df_selected[filter_col].min())
#         max_val = float(df_selected[filter_col].max())

#         selected_range = st.slider(
#             "Select range",
#             min_val,
#             max_val,
#             (min_val, max_val)
#         )

#         df_selected = df_selected[
#             (df_selected[filter_col] >= selected_range[0]) &
#             (df_selected[filter_col] <= selected_range[1])
#         ]

#     else:
#         selected_values = st.multiselect(
#             "Select values",
#             df_selected[filter_col].unique()
#         )

#         if selected_values:
#             df_selected = df_selected[df_selected[filter_col].isin(selected_values)] 
    
#     # 🔥 FINAL DATA AFTER ALL OPERATIONS
#     final_df = df_processed.copy()

#     # Apply column drop
#     final_df = final_df.drop(
#         columns=st.session_state.dropped_columns,
#         errors='ignore'
#     )
    
#     st.markdown("### 📄 Updated Dataset Preview")
#     st.dataframe(df_selected.head())



#     # Download Cleaned Data
#     st.subheader("⬇️ Download Processed Data")
#     #csv = st.session_state.df_processed.to_csv(index=False).encode('utf-8') 
#     #csv = df_processed.to_csv(index=False).encode('utf-8') 
#     final_df = st.session_state.df_processed.drop(
#         columns=st.session_state.dropped_columns,
#         errors='ignore'
#     )

#     csv = final_df.to_csv(index=False).encode('utf-8')  

#     st.download_button(
#         label="📥 Download Cleaned Dataset",
#         data=csv,
#         file_name="cleaned_data.csv",
#         mime="text/csv"
#     ) 

#     st.markdown("---")
#     st.subheader("📊 Final Summary")

#     col1, col2, col3 = st.columns(3)

#     df_final = st.session_state.df_processed

#     col1.metric("Final Rows", df_final.shape[0])
#     col2.metric("Final Columns", df_final.shape[1])
#     col3.metric("Remaining Missing Values", df_final.isnull().sum().sum())


#     # csv = df_selected.to_csv(index=False).encode('utf-8')
#     # st.download_button("Download CSV", csv, "processed_data.csv", "text/csv") 
      # 🔥 FINAL DATA PIPELINE
    final_df = df_processed.copy()

    # ---------------------------
    # Remove Duplicates
    # ---------------------------
    st.markdown("### Remove Duplicates")

    if st.checkbox("Remove duplicate rows"):
        before = final_df.shape[0]
        final_df = final_df.drop_duplicates()
        after = final_df.shape[0]

        st.success(f"Removed {before - after} duplicate rows")

    # ---------------------------
    # Drop Columns (NON-DESTRUCTIVE)
    # ---------------------------
    st.markdown("### Drop Columns")

    cols_to_drop = st.multiselect(
        "Select columns to drop",
        final_df.columns,
        default=st.session_state.dropped_columns
    )

    st.session_state.dropped_columns = cols_to_drop

    # Apply drop to final_df
    final_df = final_df.drop(
        columns=st.session_state.dropped_columns,
        errors='ignore'
    )

    if cols_to_drop:
        st.warning(f"Dropped columns: {', '.join(cols_to_drop)}")

    # ---------------------------
    # Filter Data
    # ---------------------------
    st.markdown("### Filter Data")

    if len(final_df.columns) > 0:
        filter_col = st.selectbox("Select column to filter", final_df.columns)

        if pd.api.types.is_numeric_dtype(final_df[filter_col]):
            min_val = float(final_df[filter_col].min())
            max_val = float(final_df[filter_col].max())

            selected_range = st.slider(
                "Select range",
                min_val,
                max_val,
                (min_val, max_val)
            )

            final_df = final_df[
                (final_df[filter_col] >= selected_range[0]) &
                (final_df[filter_col] <= selected_range[1])
            ]

        else:
            selected_values = st.multiselect(
                "Select values",
                final_df[filter_col].unique()
            )

            if selected_values:
                final_df = final_df[final_df[filter_col].isin(selected_values)]

    # ---------------------------
    # FINAL PREVIEW (ONLY ONE)
    # ---------------------------
    st.markdown("### 📄 Final Processed Dataset")
    st.dataframe(final_df.head())

    # ---------------------------
    # DOWNLOAD (CORRECT DATA)
    # ---------------------------
    st.subheader("⬇️ Download Processed Data")

    csv = final_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download Cleaned Dataset",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )

    # ---------------------------
    # FINAL SUMMARY
    # ---------------------------
    st.markdown("---")
    st.subheader("📊 Final Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Final Rows", final_df.shape[0])
    col2.metric("Final Columns", final_df.shape[1])
    col3.metric("Remaining Missing Values", final_df.isnull().sum().sum())

else:
    st.sidebar.info("👆Please upload a CSV file to get started.") 

st.markdown("---")
st.markdown("✨ Built by Priya | Smart CSV Analyzer")       