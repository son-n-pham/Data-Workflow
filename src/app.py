
import streamlit as st
import pandas as pd


import config
from config import temp_directory, each_project_folders, projects_directory, root_directory
from file_handle import save_uploaded_file, save_cleaned_df_to_file_and_update_session_state, load_file_and_merge_headers, st_read_file, load_file_standardize_header
# from file_handle import save_uploaded_file, read_file, st_read_file
from data_wrangle import clean_df, prepare_data_for_plotting, remove_outliers
from manage_projects import handle_load_project, handle_save_project, handle_delete_project
from state import load_state_file_from_json, ensure_key_in_session_state
from app_interface import show_sidebar
from feature_registry import GraphFeature, ClusteringFeature, ModellingFeature, PredictingMSEMinFeature, OptimizingParametersFeature, FEATURE_REGISTRY
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
    ensure_key_in_session_state('features', [])

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

        for i, feature in enumerate(st.session_state["features"]):
            with st.container():
                st.markdown(f"### Feature {i}")

                # Check if feature is GraphFeature
                if isinstance(feature, GraphFeature):
                    feature.select_plot_type()
                    feature.set_feature_parameters(columns_to_clean)

                    # Plot button
                    button_key_plot = f"plot_{feature.created_at}_{st.session_state['loaded_count']}_{i}"
                    plot_clicked = st.button("Plot", key=button_key_plot)

                    if plot_clicked:
                        # Update the feature in the session state
                        st.session_state["features"][i] = feature
                        feature.activated = True

                    if feature.activated:
                        with st.spinner(f"Plotting {feature.plot_type}..."):
                            feature.execute(df)

                st.markdown("---")  # Separator after each feature

        col1, col2 = st.columns(2)

        selected_feature_name = st.selectbox(
            "Select feature to add", list(FEATURE_REGISTRY.keys()))

        if selected_feature_name:

            selected_feature_class = FEATURE_REGISTRY[selected_feature_name]

            # Create the "Add Graph" button with a unique key derived from the length of the 'graphs' list
            if st.button("Add Analysis Feature", key=f"add_feature_button_{st.session_state['loaded_count']}_{len(st.session_state['features'])}"):

                selected_feature = selected_feature_class(
                    name=selected_feature_name)

                # Append a new feature configuration to the list in session_state
                st.session_state['features'].append(selected_feature)

                # # Append a new graph configuration to the list in session_state
                # st.session_state['features'].append({})

                # Force a rerun of the app to reflect the updated state
                st.rerun()


# plot_types = {
#     "2D Scatter Plot": ["x", "y", "color", "size"],
#     "3D Scatter Plot": ["x", "y", "z", "color", "size"],
#     # Add more plot types and their parameters here
# }


# def set_feature_parameters(columns, plot_params, selected_plot_params, index):
#     selected_columns = {}
#     cols = st.columns(len(plot_params))  # Create a row of columns

#     for i, param in enumerate(plot_params):
#         # Place each select box in a separate column
#         if selected_plot_params is None or param not in selected_plot_params:
#             selected_columns[param] = cols[i].selectbox(
#                 f"Select {param} column", columns, key=f"{param}_{index}_{i}"
#             )
#         else:
#             default_index = columns.index(
#                 selected_plot_params[param]) if selected_plot_params[param] in columns else 0
#             selected_columns[param] = cols[i].selectbox(
#                 f"Select {param} column", columns, index=default_index, key=f"{param}_{index}_{i}"
#             )
#     return selected_columns


if __name__ == "__main__":
    main()
