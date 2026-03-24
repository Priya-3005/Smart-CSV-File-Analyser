# 📊 Smart CSV Analyzer

An interactive and user-friendly data analysis web application built using **Streamlit** that enables users to upload, clean, analyze, visualize, and download processed datasets — all in one place. 
## 🔗 Live App: https://smart-csv-file-analyser.streamlit.app/
---

## 🚀 Overview

Smart CSV Analyzer is designed to simplify the data exploration and preprocessing workflow. It provides an intuitive interface for performing **Exploratory Data Analysis (EDA)**, **data cleaning**, and **interactive visualizations** without writing complex code.

---

## ✨ Key Features

### 📌 Data Overview
- Displays dataset shape, missing values, and duplicate counts
- Quick preview of uploaded data
- Column-wise data type inspection

### 📊 Exploratory Data Analysis (EDA)
- Statistical summary of numerical features
- Correlation heatmap with selectable columns
- Automatic insights:
  - Missing value detection
  - High variance identification
  - Strong correlation detection

### 📈 Interactive Visualizations
- Histogram, Boxplot, and Countplot
- Dynamic column selection
- Top-N category filtering for better readability

### 🧠 Smart Data Cleaning
- Column-wise missing value handling:
  - Fill with Mean / Median / Mode
  - Drop rows
- Supports multiple operations across columns
- Persistent transformations using session state

### ⚙️ Advanced Data Processing
- Non-destructive column dropping (with undo support)
- Duplicate row removal
- Dynamic data filtering (numerical range & categorical selection)

### 📥 Export Processed Data
- Download fully processed dataset as CSV
- Ensures all transformations are reflected accurately

---

## 🧠 Project Highlights

- ✅ **State Management using Streamlit Session State**
- ✅ **Non-Destructive Data Pipeline Design**
- ✅ **Reversible Operations (Undo Support)**
- ✅ **Dynamic UI-driven Data Transformation**
- ✅ **Clean and Modular Code Structure**

---

## 🛠️ Tech Stack

- **Frontend/UI**: Streamlit  
- **Data Handling**: Pandas  
- **Visualization**: Matplotlib, Seaborn  
- **Language**: Python  

