import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm
from scipy.stats import norm

# === PAGE SETUP ===
st.set_page_config(layout="wide")

# === HEADER ===
username = st.text_input("Enter Your Name", "Zohaib Muaz")
st.title("📊 STAT-402 Data Analysis App")
st.markdown(f"""
**Student:** {username}  
**Course:** STAT-402  
**Instructor:** Mam Kiran Iftikhar  
**University:** University of Agriculture, Faisalabad
""")

# === FILE UPLOAD AND DEFAULT LOAD ===
st.sidebar.header("Step 1: Upload File")
uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

data = None

if not uploaded_file:
    if st.sidebar.button("📂 Load 'data.csv' from directory"):
        try:
            data = pd.read_csv("data.csv")
            st.success("Loaded 'data.csv' from the current directory.")
        except FileNotFoundError:
            st.sidebar.error("⚠️ 'data.csv' not found in the directory.")
else:
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

# === PREVIEW DATA ===
if data is not None:
    st.subheader("📄 Dataset Preview")
    st.dataframe(data.head())
else:
    st.warning("⚠️ No dataset loaded. Please upload a file or click the button to load 'data.csv'.")

# === CONTINUE ONLY IF DATA EXISTS ===
if data is not None:

    # === PLOT SELECTION ===
    st.sidebar.header("Step 2: Select Graph Type")
    plot_type = st.sidebar.selectbox("Choose a plot type", [
        "Line Plot", "Bar Chart", "Histogram", "Scatter Plot", "Box Plot",
        "Correlation Heatmap", "Normal Distribution Curve", "OLS Regression",
        "Correlation Between Two Columns"
    ])

    # === SELECT COLUMNS ===
    st.sidebar.header("Step 3: Select Columns")
    x_col = st.sidebar.selectbox("X-axis", data.columns)
    y_col = st.sidebar.selectbox("Y-axis", data.columns, index=1 if len(data.columns) > 1 else 0)
    hue_col = st.sidebar.selectbox("Group / Hue (optional)", ["None"] + list(data.select_dtypes(include=[object]).columns))

    use_single_col = st.sidebar.checkbox("Use just one column for plot", value=False)
    if use_single_col:
        single_column = st.sidebar.selectbox("Select Column for Single Plot", data.columns)
        y_col = None  # Clear y_col for single-col plots
        single_column_label = st.sidebar.text_input("Custom Label for the Column", single_column)
    else:
        single_column_label = None

    # === LABELS ===
    st.sidebar.header("Step 4: Customize Labels")
    default_title = f"{plot_type} of {x_col} vs {y_col}" if not use_single_col else f"{plot_type} of {single_column_label}"
    plot_title = st.sidebar.text_input("Plot Title", default_title)
    xlabel = st.sidebar.text_input("X-axis Label", x_col)
    ylabel = st.sidebar.text_input("Y-axis Label", y_col if not use_single_col else single_column_label)

    # === PLOT OUTPUT ===
    st.subheader("📊 Plot Output")

    if plot_type == "Line Plot":
        if use_single_col:
            fig = px.line(data, x=data.index, y=single_column, title=plot_title)
        else:
            fig = px.line(data, x=x_col, y=y_col, title=plot_title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
        st.plotly_chart(fig)

    elif plot_type == "Bar Chart":
        if use_single_col:
            fig = px.bar(data, x=data.index, y=single_column, title=plot_title)
        else:
            fig = px.bar(data, x=x_col, y=y_col, title=plot_title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
        st.plotly_chart(fig)

    elif plot_type == "Histogram":
        if use_single_col:
            fig = px.histogram(data, x=single_column, title=plot_title)
        else:
            fig = px.histogram(data, x=x_col, y=y_col, title=plot_title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
        st.plotly_chart(fig)

    elif plot_type == "Scatter Plot":
        fig = px.scatter(data, x=x_col, y=y_col, title=plot_title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
        st.plotly_chart(fig)

    elif plot_type == "Box Plot":
        if use_single_col:
            fig = px.box(data, y=single_column, title=plot_title)
        else:
            fig = px.box(data, x=x_col, y=y_col, title=plot_title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
        st.plotly_chart(fig)

    elif plot_type == "Correlation Heatmap":
        corr = data.corr()
        fig = px.imshow(corr, title="Correlation Heatmap")
        st.plotly_chart(fig)

    elif plot_type == "Normal Distribution Curve":
        x = np.linspace(-3, 3, 100)
        fig = px.line(x=x, y=norm.pdf(x), title=plot_title)
        fig.update_layout(xaxis_title=xlabel, yaxis_title=ylabel)
        st.plotly_chart(fig)

    elif plot_type == "OLS Regression":
        if not use_single_col and x_col and y_col and x_col != y_col:
            try:
                X = sm.add_constant(data[x_col])
                model = sm.OLS(data[y_col], X).fit()
                predictions = model.predict(X)

                # Plotly scatter + regression line
                fig = px.scatter(data, x=x_col, y=y_col, title=plot_title)
                fig.add_scatter(x=data[x_col], y=predictions, mode="lines", name="OLS Line", line=dict(color='red'))
                fig.update_layout(title=plot_title, xaxis_title=xlabel, yaxis_title=ylabel)
                st.plotly_chart(fig)

                # Model summary
                st.subheader("📄 OLS Regression Summary")
                st.text(model.summary())
            except Exception as e:
                st.error(f"❌ Error fitting OLS model: {e}")
        else:
            st.warning("⚠️ Please select two **different** columns and uncheck 'Use just one column for plot'.")


    elif plot_type == "Correlation Between Two Columns":
        if not use_single_col and x_col and y_col and x_col != y_col:
            try:
                correlation_value = data[x_col].corr(data[y_col])
                st.success(f"✅ Correlation between **{x_col}** and **{y_col}**: `{correlation_value:.4f}`")
            except Exception as e:
                st.error(f"❌ Error computing correlation: {e}")
        else:
            st.warning("⚠️ Please make sure you selected two **different** columns and unchecked 'Use just one column for plot'.")

    # === STATISTICS ===
    st.subheader("📈 Statistical Summary")
    st.write(data.describe())
