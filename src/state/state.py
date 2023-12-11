from datetime import datetime
import os
import streamlit as st
import json

from config import temp_directory, each_project_folders
from utils import ensure_directory_exists, load_pickle_file_to_dict
from feature_registry import GraphFeature, Feature, FEATURE_REGISTRY


def serialize_feature_obj(obj):
    """Serialize custom objects to a dictionary, including the class name."""
    if hasattr(obj, "__dict__"):
        obj_dict = {key: serialize_feature_obj(
            value) for key, value in obj.__dict__.items()}
        # Include the class name for deserialization
        obj_dict["__class__"] = obj.__class__.__name__
        return obj_dict
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def deserialize_feature_obj(d):
    feature_classes = FEATURE_REGISTRY

    if 'type' in d and d['type'] in feature_classes:
        return feature_classes[d['type']].from_dict(d)
    else:
        return d


def save_state_file_to_json(state_file='state.json', folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
    file_path = os.path.join(folder, state_file)
    # Create folder if it does not exist
    ensure_directory_exists(folder)

    dict_session_state = dict(st.session_state)

    """Save the current session state to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(dict_session_state, file, default=serialize_feature_obj)


def clear_session_state_values():
    keys = list(st.session_state.keys())
    st.session_state.clear()
    for key in keys:
        st.session_state[key] = None


def load_state_file_from_json(state_file='state.json',
                              state_folder=os.path.join(temp_directory, each_project_folders["state_folder"])):

    json_file_path = os.path.join(state_folder, state_file)
    if not os.path.exists(json_file_path):
        st.error(
            f"State file {state_file} does not exist in the directory {state_folder}")
        return

    clear_session_state_values()

    """Load the session state from a JSON file."""
    with open(json_file_path, "r") as file:
        state_dict = json.load(file, object_hook=deserialize_feature_obj)
        for key, value in state_dict.items():
            if key in st.session_state:
                st.session_state[key] = value


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
