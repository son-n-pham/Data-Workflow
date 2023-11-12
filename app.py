import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import pickle
import os


def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        # Create a directory if it doesn't exist
        directory = 'uploaded_files'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the file to the new directory
        file_path = os.path.join(directory, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Get the absolute path
        absolute_file_path = os.path.abspath(file_path)
        return absolute_file_path

    return None


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
    file_name = file_name.split('.')[-2]
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


def prepare_data_for_plotting(df, columns):
    # Create a copy of the dataframe with only the selected columns
    columns = list(set(columns))
    df_copy = df[columns].copy()

    # Convert columns to numeric and drop rows where any column is NaN
    df_copy = df_copy.apply(pd.to_numeric, errors='coerce').dropna()

    if df_copy.empty:
        st.warning(
            "The selected data for plotting is empty after removing non-numeric or NaN values.")
        return None

    return df_copy


# def plot_3d_scatter(df, x_col, y_col, z_col, color_col=None, size_col=None, width=800, height=800, marker_size=3):
def plot_3d_scatter(df, x=None, y=None, z=None, color=None, size=None, width=800, height=800, marker_size=5, **kwargs):
    columns = [x, y, z, color, size]
    df_copy = prepare_data_for_plotting(df, columns)

    if df_copy is not None:
        # Plotting
        fig = px.scatter_3d(df_copy, x=x, y=y,
                            z=z, color=color, size=size)
        fig.update_traces(marker=dict(size=marker_size))
        fig.update_layout(width=width, height=height)

        # Update the starting point of each axis to 0
        fig.update_scenes(xaxis=dict(range=[0, df_copy[x].max()]),
                          yaxis=dict(range=[0, df_copy[y].max()]),
                          zaxis=dict(range=[0, df_copy[z].max()]))

        # Plotly with Streamlit
        st.plotly_chart(fig)


# def plot_2d_scatter(df, x_col, y_col, color_col=None, size_col=None, width=800, height=800, marker_size=5):
def plot_2d_scatter(df, x=None, y=None, color=None, size=None, width=800, height=800, marker_size=5, **kwargs):
    columns = [x, y, color, size]
    df_copy = prepare_data_for_plotting(df, columns)

    if df_copy is not None:
        # Plotting
        fig = px.scatter(df_copy, x=x, y=y,
                         color=color, size=size)
        fig.update_traces(marker=dict(size=marker_size))
        fig.update_layout(width=width, height=height)

        # Plotly with Streamlit
        st.plotly_chart(fig)


def load_state_file(state_file):
    with open(f"archive/{state_file}", "rb") as f:
        loaded_state = pickle.load(f)

        # Clear st.session_state
        st.session_state.clear()

        # Load the state from saved file
        for key, value in loaded_state.items():
            st.session_state[key] = value

    if 'loaded_count' not in st.session_state:
        st.session_state['loaded_count'] = 0
    st.session_state['loaded_count'] += 1


def main():

    # if archive/temp.pkl exists, load it to session_state
    # then delete that file
    if os.path.exists("archive/temp.pkl"):
        load_state_file("temp.pkl")
        os.remove("archive/temp.pkl")

    columns_to_clean_already = []

    if 'loaded_file' not in st.session_state:
        st.session_state['loaded_file'] = None

    if 'is_df_cleaned' not in st.session_state:
        st.session_state['is_df_cleaned'] = False

    if 'cleaned_columns' not in st.session_state:
        st.session_state['cleaned_columns'] = []
        columns_to_clean_already = []
    else:
        columns_to_clean_already = st.session_state['cleaned_columns']

    if 'removed_outlier_columns' not in st.session_state:
        st.session_state['removed_outlier_columns'] = []
        removed_outlier_columns = []
    else:
        removed_outlier_columns = st.session_state['removed_outlier_columns']

    if "graphs" not in st.session_state:
        st.session_state["graphs"] = []

    with st.sidebar:

        st.title("✨Data Analysis App")

        st.markdown("---")

        # Create the buttons
        with st.expander("Load Saved Work"):
            if not os.path.exists("archive"):
                os.makedirs("archive")
            state_files = os.listdir("archive")
            state_file = st.selectbox(
                "Choose a file", state_files, key="load_work")

            # Check state_file
            if state_file is not None:

                load_state_button = st.button("Load Your Work")

                if load_state_button:
                    load_state_file(state_file)
                    # with open(f"archive/{state_file}", "rb") as f:
                    #     loaded_state = pickle.load(f)

                    #     # Clear st.session_state
                    #     st.session_state.clear()

                    #     # Load the state from saved file
                    #     for key, value in loaded_state.items():
                    #         st.session_state[key] = value

                    # if 'loaded_count' not in st.session_state:
                    #     st.session_state['loaded_count'] = 0
                    # st.session_state['loaded_count'] += 1

        with st.expander("Save Your Work"):
            filename = st.text_input("Enter the filename")
            proceed_to_save_button = st.button("Proceed to Save")

            if proceed_to_save_button:
                # # Save the value of st.session_state['loaded_file']
                # current_session_state = st.session_state
                # st.write(f"current_session_state: {current_session_state}")
                state_file = os.path.join("archive", filename + ".pkl")

                # with open(f"archive/{filename}.pkl", "wb") as f:
                with open(state_file, "wb") as f:
                    pickle.dump(dict(st.session_state), f)

                temp_state_file = os.path.join("archive", "temp.pkl")
                with open(temp_state_file, "wb") as f:
                    pickle.dump(dict(st.session_state), f)

                st.rerun()

                # # Restore the value of st.session_state['loaded_file']
                # st.session_state = current_session_state

                # st.rerun()

        with st.expander("Delete Saved Work"):
            if not os.path.exists("archive"):
                os.makedirs("archive")
            state_files = os.listdir("archive")
            state_file = st.selectbox(
                "Choose a file", state_files, key="delete_work")

            # Check state_file
            if state_file is not None:

                delete_state_button = st.button("Delete Saved Work")

                if delete_state_button:
                    os.remove(f"archive/{state_file}")
                    st.success(f"Deleted {state_file}!")
                    st.rerun()

        st.write("---")

        uploaded_file = st.file_uploader(
            "Choose a CSV file", type=["csv", "txt"])

    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        if file_path:
            st.session_state['loaded_file'] = file_path

    if st.session_state['loaded_file'] is not None:
        st.write(f"Uploaded file is: {st.session_state['loaded_file']}")

        st.markdown("---")

        file_type = st.session_state['loaded_file'].split('.')[-1]

        df = read_file(st.session_state['loaded_file'], file_type)

        st.write(df)

        col1, col2 = st.columns(2)

        with col1:
            columns_to_clean = st.multiselect(
                "Select columns to clean", df.columns, columns_to_clean_already)

        with col2:
            removed_outlier_columns = [
                column for column in removed_outlier_columns if column in columns_to_clean]
            column_to_remove_outliers = st.multiselect(
                "Select columns to remove outliers", columns_to_clean, removed_outlier_columns, disabled=not columns_to_clean)

        column_to_clean_diff = list(
            set(columns_to_clean) - set(columns_to_clean_already))

        if len(column_to_clean_diff) > 0:
            st.session_state['is_df_cleaned'] = False

        proceed_clicked = st.button(
            "Proceed", disabled=st.session_state['is_df_cleaned'])

        if proceed_clicked:
            with st.spinner("Cleaning data..."):
                st.session_state['cleaned_columns'] = columns_to_clean
                st.session_state['removed_outlier_columns'] = column_to_remove_outliers

                if not st.session_state['is_df_cleaned']:
                    df = clean_df(df, column_to_clean_diff)
                    columns_to_clean_already = columns_to_clean

                    # Get the base name and extension of the loaded file
                    base_name, extension = os.path.splitext(
                        st.session_state['loaded_file'])

                    # Convert the new file name to the format: <base_name>_cleaned.<extension>
                    new_file_name = base_name + "_cleaned" + extension

                    # Save the cleaned df to the new file
                    df.to_csv(new_file_name, index=False)

                    # Delete the old file and update st.session_state['loaded_file'] to new file
                    os.remove(st.session_state['loaded_file'])
                    st.session_state['loaded_file'] = new_file_name

                st.session_state['is_df_cleaned'] = True
                st.success("Data cleaned successfully!")

            if len(column_to_remove_outliers) > 0:
                with st.spinner("Removing outliers..."):
                    df = remove_outliers(df, column_to_remove_outliers)
                    st.success("Outliers removed successfully!")

    if st.session_state.get('is_df_cleaned', False):

        columns_to_clean = st.session_state['cleaned_columns']

        st.markdown("---")

        for i, graph in enumerate(st.session_state["graphs"]):
            with st.container():
                st.markdown(f"### Graph {i}")
                graph["id"] = i
                graph["type"] = st.radio("Select graph type", [
                    "2D Scatter Plot", "3D Scatter Plot"], key=f"graph_type_{i}")

                if 'columns' in graph:
                    selected_plot_params = graph['columns']
                else:
                    selected_plot_params = None

                graph["columns"] = select_columns(
                    columns_to_clean, plot_types[graph["type"]], selected_plot_params, i)

                if "plot_clicked" not in graph:
                    graph["plot_clicked"] = False

                plot_clicked = st.button(
                    "Plot", key=f"plot_graph_{st.session_state['loaded_count']}_{i}")

                if plot_clicked:
                    graph["plot_clicked"] = True

                if graph["plot_clicked"]:
                    with st.spinner(f"Plotting {graph['type']}..."):
                        if graph["type"] == "2D Scatter Plot":
                            plot_2d_scatter(df, **graph["columns"])
                        elif graph["type"] == "3D Scatter Plot":
                            plot_3d_scatter(df, **graph["columns"])

                st.markdown("---")  # Separator after each graph

        # Initialize 'loaded_count' if it doesn't exist
        if 'loaded_count' not in st.session_state:
            st.session_state['loaded_count'] = 0

        # Create the "Add Graph" button with a unique key derived from the length of the 'graphs' list
        if st.button("Add Graph", key=f"add_graph_button_{st.session_state['loaded_count']}_{len(st.session_state['graphs'])}"):
            # Append a new graph configuration to the list in session_state
            st.session_state['graphs'].append({})

            # Force a rerun of the app to reflect the updated state
            st.rerun()


def select_columns(columns, plot_params, selected_plot_params, index):
    selected_columns = {}
    cols = st.columns(len(plot_params))  # Create a row of columns

    for i, param in enumerate(plot_params):
        # Place each select box in a separate column
        if selected_plot_params is None or param not in selected_plot_params:
            selected_columns[param] = cols[i].selectbox(
                f"Select {param} column", columns, key=f"{param}_{index}_{i}"
            )
        else:
            default_index = columns.index(
                selected_plot_params[param]) if selected_plot_params[param] in columns else 0
            selected_columns[param] = cols[i].selectbox(
                f"Select {param} column", columns, index=default_index, key=f"{param}_{index}_{i}"
            )
    return selected_columns


plot_types = {
    "2D Scatter Plot": ["x", "y", "color", "size"],
    "3D Scatter Plot": ["x", "y", "z", "color", "size"],
    # Add more plot types and their parameters here
}


if __name__ == "__main__":
    main()
