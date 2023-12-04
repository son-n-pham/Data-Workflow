import streamlit as st
import os

from state import load_state_file_from_json, save_state_file_to_json
from utils import list_sub_folders, copy_folder, delete_folder, load_pickle_file_to_dict

from config import temp_directory, projects_directory


def handle_load_project(projects_directory=projects_directory):

    projects = list_sub_folders(projects_directory)
    project = st.selectbox("Choose a saved project",
                           projects, key="load_project")

    if project is not None:
        load_project_button = st.button("Load Saved Project")
        if load_project_button:
            copy_folder(os.path.join(projects_directory, project),
                        temp_directory)
            load_state_file_from_json()
            st.success(f"Loaded {project}!")
            st.rerun()


def handle_save_project(temp_directory=temp_directory, projects_directory=projects_directory):
    project_name = st.text_input("Enter the project name")
    proceed_to_save_button = st.button("Proceed to Save")

    if proceed_to_save_button:

        save_state_file_to_json()

        new_project_directory = os.path.join(projects_directory, project_name)
        copy_folder(temp_directory, new_project_directory)

        st.success(f"The {project_name} is saved!")

        st.rerun()


def handle_delete_project(projects_directory=projects_directory):
    projects = list_sub_folders(projects_directory)
    project = st.selectbox("Choose a saved project",
                           projects, key="delete_project")

    if project is not None:
        delete_state_button = st.button("Delete Saved Project")

        if delete_state_button:
            if delete_folder(os.path.join(projects_directory, project)):
                st.success(f"Deleted {project}!")
            else:
                st.error(
                    f"Failed to delete {project}.")
            st.rerun()
