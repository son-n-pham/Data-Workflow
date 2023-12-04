
import streamlit as st
import pandas as pd
import os
import shutil
import pickle
import json

from plot import plot_2d_scatter, plot_3d_scatter

import config
from config import temp_directory, each_project_folders, projects_directory, root_directory
from file_handle import save_uploaded_file, save_cleaned_df_to_file_and_update_session_state, load_file_and_merge_headers, st_read_file, load_file_standardize_header
# from file_handle import save_uploaded_file, read_file, st_read_file
from data_wrangle import clean_df, prepare_data_for_plotting, remove_outliers
from manage_projects import handle_load_project, handle_save_project, handle_delete_project
from state import load_state_file_from_json, ensure_key_in_session_state
from app_interface import show_sidebar
from utils import ensure_directory_exists, list_sub_folders, copy_folder, delete_folder, load_pickle_file_to_dict


st.set_page_config(
    page_title="MSE Analysis", layout="wide", page_icon=":bar_chart:"
)


def main():

    # Create a button, when clicking, the session state will be shown by st.write()
    if st.button("Show Session State"):
        st.write(st.session_state)

    ensure_key_in_session_state('loaded_file', None)
    ensure_key_in_session_state('is_df_cleaned', False)
    ensure_key_in_session_state('graphs', [])
    ensure_key_in_session_state('clusters', [])
    ensure_key_in_session_state('loaded_count', 0)

    columns_to_clean_already = ensure_key_in_session_state(
        'cleaned_columns', [])
    if len(columns_to_clean_already) > 0:
        columns_to_clean = st.session_state['cleaned_columns']

    removed_outlier_columns = ensure_key_in_session_state(
        'removed_outlier_columns', [])

    uploaded_files = show_sidebar()

    if uploaded_files is not None:

        # When uploading 1 file, save the file to uploaded_fodler first
        # then update session_state['loaded_file']
        # TODO: Consider to ask for well name and save the file to uploaded_folder/well_name
        if len(uploaded_files) == 1:
            uploaded_file = uploaded_files[0]
            file_path = save_uploaded_file(uploaded_file)
            if file_path:
                st.session_state['loaded_file'] = file_path

    if st.session_state['loaded_file'] is not None:

        # # Re-assign st.session_state['loaded_file'] to the cleaned file
        # if st.session_state['is_df_cleaned']:
        #     st.session_state['loaded_file'] = os.path.join(os.path.join(
        #         temp_directory,
        #         each_project_folders['cleaned_data_folder']),
        #         os.path.basename(st.session_state['loaded_file']))

        # For debug
        st.write(
            f"From upload saved work, Uploaded file is: {st.session_state['loaded_file']}")

        st.markdown("---")

        df = load_file_standardize_header(
            st.session_state['loaded_file'])

        st.write(df)

        st.markdown("---")

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

        if proceed_clicked or st.session_state['is_df_cleaned']:
            with st.spinner("Cleaning data..."):
                st.session_state['cleaned_columns'] = columns_to_clean
                st.session_state['removed_outlier_columns'] = column_to_remove_outliers

                if not st.session_state['is_df_cleaned']:
                    # Clean df based on the columns not cleaned yet
                    df = clean_df(df, column_to_clean_diff)
                    # Update the columns already cleaned
                    columns_to_clean_already = columns_to_clean

                st.success("Data cleaned successfully!")

            if len(column_to_remove_outliers) > 0:
                with st.spinner("Removing outliers..."):
                    df = remove_outliers(df, column_to_remove_outliers)
                    st.success("Outliers removed successfully!")

            st.session_state['is_df_cleaned'] = True
            save_cleaned_df_to_file_and_update_session_state(df)

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

                button_key_plot = f"plot_{st.session_state['loaded_count']}_{i}"
                plot_clicked = st.button(
                    "Plot", key=button_key_plot)
                # plot_clicked = st.button(
                #     "Plot", key=f"plot_graph_{st.session_state['loaded_count']}_{i}")

                if plot_clicked:
                    graph["plot_clicked"] = True

                if graph["plot_clicked"]:
                    with st.spinner(f"Plotting {graph['type']}..."):
                        if graph["type"] == "2D Scatter Plot":
                            plot_2d_scatter(df, **graph["columns"])
                        elif graph["type"] == "3D Scatter Plot":
                            plot_3d_scatter(df, **graph["columns"])

                st.markdown("---")  # Separator after each graph

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
