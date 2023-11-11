import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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

# Function to clean the DataFrame


def clean_df(df, columns):
    df = df.replace(-999.25, np.nan).dropna(subset=columns)
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

# Function to remove outliers from the DataFrame


def remove_outliers(df, columns):
    for column in columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df[column] >= Q1 - 1.5*IQR) & (df[column] <= Q3 + 1.5*IQR)]
    return df

# Function to prepare data for plotting


def preprocess_for_plotting(df, columns):
    df_copy = df[columns].dropna()
    df_copy = df_copy.apply(pd.to_numeric, errors='coerce').dropna()
    return df_copy

# Function to plot scatter plots


def plot_scatter(df, x_col, y_col, z_col=None, color_col=None, size_col=None, plot_type='2D Scatter Plot', width=800, height=800, marker_size=5):
    if df.empty:
        st.warning(
            "The selected data for plotting is empty after removing non-numeric or NaN values.")
        return
    if plot_type == '3D Scatter Plot':
        fig = px.scatter_3d(df, x=x_col, y=y_col, z=z_col,
                            color=color_col, size=size_col)
    elif plot_type == '2D Scatter Plot':
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col)
    fig.update_traces(marker=dict(size=marker_size))
    fig.update_layout(width=width, height=height)
    st.plotly_chart(fig)


# Main function for Streamlit app
def main():
    st.title("Data Analysis App")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Choose a CSV file", type=["csv", "txt", "xlsx"])

    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]
        try:
            df = read_file(uploaded_file, file_type)
        except UnicodeDecodeError:
            st.error("Failed to read the file with the provided encodings.")

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

            # Initialize session state variables if they don't exist
            if 'plot_type' not in st.session_state:
                st.session_state['plot_type'] = "2D Scatter Plot"
            # Display the radio buttons for selecting plot type
            plot_types = ["2D Scatter Plot", "3D Scatter Plot"]
            print("------------------")
            print(st.session_state['plot_type'])
            st.session_state["plot_type"] = st.radio(
                "Select graph type", plot_types, index=plot_types.index(st.session_state['plot_type']))
            print(st.session_state['plot_type'])

            # Display the column selectors based on the selected plot_type
            cols = st.columns(
                4 if st.session_state["plot_type"] == "2D Scatter Plot" else 5)
            x_col = cols[0].selectbox("Select x column", columns_to_clean)
            y_col = cols[1].selectbox("Select y column", columns_to_clean)
            color_col = cols[2].selectbox(
                "Select color column", columns_to_clean)

            if st.session_state["plot_type"] == "2D Scatter Plot":
                size_col = cols[3].selectbox(
                    "Select size column", columns_to_clean)
            else:  # For 3D Scatter Plot
                z_col = cols[3].selectbox(
                    "Select z column", columns_to_clean)
                size_col = cols[4].selectbox(
                    "Select size column", columns_to_clean)

            # Button to trigger plotting
            plot_clicked = st.button("Plot")

            # The plotting logic is triggered only when the plot button is clicked
            if plot_clicked:
                if st.session_state['is_df_cleaned']:
                    # Check if the required columns are selected before plotting
                    if x_col and y_col and ((st.session_state["plot_type"] == "2D Scatter Plot") or (st.session_state["plot_type"] == "3D Scatter Plot" and z_col)):
                        # Call the plot_scatter function with the selected values
                        if st.session_state["plot_type"] == "2D Scatter Plot":
                            plot_scatter(
                                df,
                                x_col=x_col,
                                y_col=y_col,
                                color_col=color_col if color_col else None,
                                size_col=size_col if size_col else None,
                                plot_type='2D',
                                width=800,
                                height=800,
                                marker_size=5
                            )
                        elif st.session_state["plot_type"] == "3D Scatter Plot":
                            plot_scatter(
                                df,
                                x_col=x_col,
                                y_col=y_col,
                                z_col=z_col,
                                color_col=color_col if color_col else None,
                                size_col=size_col if size_col else None,
                                plot_type='3D',
                                width=800,
                                height=800,
                                marker_size=5
                            )
                    else:
                        st.warning(
                            "Please select the required columns for plotting.")
                else:
                    st.warning("Please clean the data before plotting.")


if __name__ == "__main__":
    main()
