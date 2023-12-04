# Streamlit sidebar
import streamlit as st
from manage_projects import handle_load_project, handle_save_project, handle_delete_project


def show_sidebar():
    with st.sidebar:

        st.title("✨Data Analysis App")

        st.markdown("---")

        with st.expander("Load Saved Project"):
            handle_load_project()

        with st.expander("Save Your Project"):
            handle_save_project()

        with st.expander("Delete Saved Project"):
            # Create the buttons
            handle_delete_project()

        st.write("---")

        uploaded_files = st.file_uploader(
            "Choose files", type=["csv", "txt"], accept_multiple_files=True)

    return uploaded_files
