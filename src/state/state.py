import os
import streamlit as st
import pickle
import json

from config import temp_directory, each_project_folders
from utils import ensure_directory_exists, load_pickle_file_to_dict


def load_state_file_from_json(state_file='state.json',
                              state_folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
    json_file_path = os.path.join(state_folder, state_file)
    if not os.path.exists(json_file_path):
        st.error(
            f"State file {state_file} does not exist in the directory {state_folder}")
        return

    with open(json_file_path, "r") as f:
        loaded_state = json.load(f)

        # Clear st.session_state
        st.session_state.clear()

        for key, value in loaded_state.items():
            st.session_state[key] = value

    # if 'loaded_count' not in st.session_state:
    #     st.session_state['loaded_count'] = 0
    st.session_state['loaded_count'] += 1


# def load_state_file(state_file='state.pkl',
#                     state_folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
#     """
#     Load a saved state from a file and update the Streamlit session state.

#     This function loads a pickled Python object from a file and updates the
#     Streamlit session state with the loaded state. If the file does not exist,
#     an error message is displayed in the Streamlit app.

#     Parameters
#     ----------
#     state_file : str
#         The name of the state file to load.
#     folder : str, optional
#         The directory where the state file is located. By default, this is
#         set to os.path.join(temp_directory,each_project_folders["state_folder"]).

#     Returns
#     -------
#     None
#     """
#     # Function implementation...
#     file_path = os.path.join(state_folder, state_file)
#     if not os.path.exists(file_path):
#         st.error(
#             f"State file {state_file} does not exist in the directory {state_folder}")
#         return

#     # with open(file_path, "rb") as f:
#     #     loaded_state = pickle.load(f)

#     print("#############################################")

#     print(f"LOAD STATE FILE: current session state: {st.session_state}")

#     loaded_state = load_pickle_file_to_dict(file_path)

#     print(
#         f"LOAD STATE FILE: loaded_state from file {file_path}: {loaded_state}")

#     # Clear st.session_state
#     st.session_state.clear()

#     # Load the state from saved file into session state
#     for key, value in loaded_state.items():
#         print(f"LOAD STATE FILE __ k and v: {key} and {value}")
#         st.session_state[key] = value

#     if 'loaded_count' not in st.session_state:
#         st.session_state['loaded_count'] = 0
#     st.session_state['loaded_count'] += 1

#     print(
#         f"LOAD STATE FILE: After loading, current session state: {st.session_state}")


def save_state_file_to_json(state_file='state.json', folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
    """
    Save the current Streamlit session state to a file.

    This function saves the current Streamlit session state to a file. If the
    file already exists, the user is prompted to confirm overwriting the file.

    Parameters
    ----------
    state_file : str
        The name of the state file to save.
    folder : str, optional
        The directory where the state file is located. By default, this is
        set to os.path.join(temp_directory,each_project_folders["state_folder"]).

    Returns
    -------
    None
    """

    print("*****save_state_file is running*****")
    # Function implementation...
    file_path = os.path.join(folder, state_file)

    # Create folder if it does not exist
    ensure_directory_exists(folder)

    with open(file_path, "w") as f:
        json.dump(dict(st.session_state), f)


# def save_state_file(state_file='state.pkl', folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
#     """
#     Save the current Streamlit session state to a file.

#     This function saves the current Streamlit session state to a file. If the
#     file already exists, the user is prompted to confirm overwriting the file.

#     Parameters
#     ----------
#     state_file : str
#         The name of the state file to save.
#     folder : str, optional
#         The directory where the state file is located. By default, this is
#         set to os.path.join(temp_directory,each_project_folders["state_folder"]).

#     Returns
#     -------
#     None
#     """

#     print("*****save_state_file is rusnning*****")
#     # Function implementation...
#     file_path = os.path.join(folder, state_file)

#     # Create folder if it does not exist
#     ensure_directory_exists(folder)

#     with open(file_path, "wb") as f:
#         pickle.dump(st.session_state, f)

#     state_from_saved_pickle_file = load_pickle_file_to_dict(file_path)
#     print(
#         f"IMPORTANT!!! SAVE STATE FILE: state_from_saved_pickle_file: {state_from_saved_pickle_file}")

#     st.success(f"State saved to {file_path}")


def delete_state_file(state_file,
                      state_folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
    """
    Delete a saved state file.

    Parameters
    ----------
    state_file : str
        The name of the state file to delete.
    state_folder : str, optional
        The directory where the state file is located. By default, this is
        set to "state_folder".

    Returns
    -------
    None
    """
    file_path = os.path.join(state_folder, state_file)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    else:
        return False


def ensure_key_in_session_state(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value
        return default_value
    return st.session_state[key]
