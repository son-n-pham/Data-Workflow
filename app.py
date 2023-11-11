import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np
from collections import Counter


# Function to read and process file with multiple encodings
def read_file(file_name, file_type='csv'):
    # List of encodings to try
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'utf-16']
    read_funcs = {
        'csv': pd.read_csv,
        'excel': pd.read_excel,
        'txt': lambda file, enc: pd.read_csv(file, header=None, delimiter='\t', encoding=enc)
    }
    read_args = {
        'csv': {'header': None},
        'excel': {'header': None},
        'txt': {'header': None}
    }
    # Loop through encodings until the file is read successfully
    for encoding in encodings:
        try:
            df = read_funcs[file_type](
                file_name, **read_args[file_type], encoding=encoding)
            return set_header(df, file_name)
        except UnicodeDecodeError as e:
            last_exception = e
            continue
    # If all encodings fail, raise the last exception
    raise last_exception

# Function to set the header of the DataFrame


def set_header(df, file_name):
    df = df.copy()  # Create a copy of the DataFrame
    header = df.iloc[0].str.strip() + '__' + df.iloc[1].str.strip()
    header = pd.Series(header).apply(lambda x: x if header.tolist().count(x) == 1
                                     else x + '_' + str(header.tolist().index(x)))
    df = df.iloc[2:]  # Remove the first two rows
    df.columns = header  # Set the new header
    # Get the file name (without extension)
    file_name = file_name.name.split('.')[0]
    df.loc[:, "well"] = file_name

    return df


def clean_df(df, columns):
    # Drop rows where all specified columns are 0
    for column in columns:
        df = df[df[column] != 0]

    # Convert specified columns to numeric and handle non-numeric values
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Replace -999.25 with NaN
    df = df.replace(-999.25, np.nan)

    # Drop rows where any specified column is NaN
    df = df.dropna(subset=columns)

    return df


def remove_outliers(df, columns_to_remove_outliers):

    for column in columns_to_remove_outliers:
        # Convert specified columns to numeric and handle non-numeric values
        df[column] = pd.to_numeric(df[column], errors='coerce')

        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df[column] >= Q1 - 1.5*IQR) &
                (df[column] <= Q3 + 1.5*IQR)]

    return df


def plot_3d_scatter(df, x_col, y_col, z_col, color_col=None, size_col=None, width=800, height=800, marker_size=3):
    # Create a copy of the dataframe with only the selected columns
    columns = [x_col, y_col, z_col]
    if color_col:
        columns.append(color_col)
    if size_col:
        columns.append(size_col)

    columns = list(set(columns))
    df_copy = df[columns].copy()

    # Convert columns to numeric and drop rows where any column is NaN
    df_copy = df_copy.apply(pd.to_numeric, errors='coerce').dropna()

    if df_copy.empty:
        st.warning(
            "The selected data for plotting is empty after removing non-numeric or NaN values.")
        return

    # Plotting
    fig = px.scatter_3d(df_copy, x=x_col, y=y_col, z=z_col,
                        color=color_col, size=size_col)
    fig.update_traces(marker=dict(size=marker_size))
    fig.update_layout(width=width, height=height)

    # Update the starting point of each axis to 0
    fig.update_scenes(xaxis=dict(range=[0, df_copy[x_col].max()]),
                      yaxis=dict(range=[0, df_copy[y_col].max()]),
                      zaxis=dict(range=[0, df_copy[z_col].max()]))

    # Plotly with Streamlit
    st.plotly_chart(fig)


def plot_2d_scatter(df, x_col, y_col, color_col=None, size_col=None, width=800, height=800, marker_size=5):
    # Create a copy of the dataframe with only the selected columns
    columns = [x_col, y_col]
    if color_col:
        columns.append(color_col)
    if size_col:
        columns.append(size_col)

    columns = list(set(columns))
    df_copy = df[columns].copy()

    # Convert columns to numeric and drop rows where any column is NaN
    df_copy = df_copy.apply(pd.to_numeric, errors='coerce').dropna()

    # Display DataFrame in Streamlit
    st.dataframe(df_copy)

    if df_copy.empty:
        st.warning(
            "The selected data for plotting is empty after removing non-numeric or NaN values.")
        return

    # Plotting
    if color_col and size_col:
        fig = px.scatter(df_copy, x=x_col, y=y_col,
                         color=color_col, size=size_col)
    elif color_col:
        fig = px.scatter(df_copy, x=x_col, y=y_col, color=color_col)
    elif size_col:
        fig = px.scatter(df_copy, x=x_col, y=y_col, size=size_col)
    else:
        fig = px.scatter(df_copy, x=x_col, y=y_col)

    fig.update_traces(marker=dict(size=marker_size))
    fig.update_layout(width=width, height=height)

    # Plotly with Streamlit
    st.plotly_chart(fig)


def main():
    st.title("Data Analysis App")

    st.markdown("---")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv", "txt"])

    if uploaded_file is not None:
        st.write(f"Uploaded file is: {uploaded_file.name}")
        # st.write("hello")
        st.markdown("---")

        file_type = uploaded_file.name.split('.')[-1]

        df = read_file(uploaded_file, file_type)

        col1, col2 = st.columns(2)

        with col1:
            columns_to_clean = st.multiselect(
                "Select columns to clean", df.columns)

        with col2:
            column_to_remove_outliers = st.multiselect(
                "Select columns to remove outliers", columns_to_clean, disabled=not columns_to_clean)

        proceed_clicked = st.button("Proceed", disabled=not columns_to_clean)

        if 'is_df_cleaned' not in st.session_state:
            st.session_state['is_df_cleaned'] = False

        if proceed_clicked:
            with st.spinner("Cleaning data..."):
                df = clean_df(df, columns_to_clean)
                st.session_state['is_df_cleaned'] = True
                st.success("Data cleaned successfully!")

            if len(column_to_remove_outliers) > 0:
                with st.spinner("Removing outliers..."):
                    df = remove_outliers(
                        df, column_to_remove_outliers)
                    st.success("Outliers removed successfully!")

        if st.session_state['is_df_cleaned']:
            st.markdown("---")
            graph_type = st.radio("Select graph type",
                                  ("2D Scatter Plot", "3D Scatter Plot"))

            if graph_type == "2D Scatter Plot":
                x_col = st.selectbox("Select x column", columns_to_clean)
                y_col = st.selectbox("Select y column", columns_to_clean)
                color_col = st.selectbox(
                    "Select color column", columns_to_clean)
                size_col = st.selectbox("Select size column", columns_to_clean)
            elif graph_type == "3D Scatter Plot":
                x_col = st.selectbox("Select x column", columns_to_clean)
                y_col = st.selectbox("Select y column", columns_to_clean)
                z_col = st.selectbox("Select z column", columns_to_clean)
                color_col = st.selectbox(
                    "Select color column", columns_to_clean)
                size_col = st.selectbox("Select size column", columns_to_clean)

            plot_clicked = st.button("Plot")

            if plot_clicked:
                with st.spinner(f"Proceed {graph_type}..."):
                    if graph_type == "2D Scatter Plot":
                        plot_2d_scatter(df, x_col, y_col, color_col, size_col)
                    elif graph_type == "3D Scatter Plot":
                        plot_3d_scatter(df, x_col, y_col, z_col,
                                        color_col, size_col)


if __name__ == "__main__":
    main()
