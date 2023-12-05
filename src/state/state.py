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

    """Save the current session state to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(dict(st.session_state), file, default=serialize_feature_obj)


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


# def deserialize_state(serialized_state):
#     # This function should be adapted based on how you serialized your state
#     state = {}
#     for key, value in serialized_state.items():
#         # Implement custom deserialization for complex objects
#         if is_custom_object(value):
#             # Assuming you've implemented a deserialize method
#             state[key] = GraphFeature.deserialize(value)
#         else:
#             state[key] = value
#     return state


# def load_state_file_from_json(state_file='state.json',
#                               state_folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
#     json_file_path = os.path.join(state_folder, state_file)
#     if not os.path.exists(json_file_path):
#         st.error(
#             f"State file {state_file} does not exist in the directory {state_folder}")
#         return

#     with open(json_file_path, "r") as f:
#         state_dict = json.load(f)

#     for key, value in state_dict.items():
#         if isinstance(value, dict) and "plot_type" in value:  # This is a GraphFeature
#             state_dict[key] = GraphFeature.from_dict(value)
#         elif isinstance(value, list) and all(isinstance(item, dict) and "plot_type" in item for item in value):
#             state_dict[key] = [GraphFeature.from_dict(item) for item in value]
#     st.session_state.update(state_dict)

#     # if 'loaded_count' not in st.session_state:
#     #     st.session_state['loaded_count'] = 0
#     st.session_state['loaded_count'] += 1


# def serialize_state(state):
#     # This function should be adapted based on the content of your session_state
#     serialized_state = {}
#     for key, value in state.items():
#         # Implement custom serialization for complex objects, ie.GraphFeature
#         if isinstance(value, GraphFeature):
#             # Assuming you've implemented a serialize method
#             serialized_state[key] = value.to_dict()
#         else:
#             serialized_state[key] = value
#     return serialized_state


# def save_state_file_to_json(state_file='state.json', folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
#     # Function implementation...
#     file_path = os.path.join(folder, state_file)
#     # Create folder if it does not exist
#     ensure_directory_exists(folder)

#     with open(file_path, "w") as f:
#         json.dump(serialize_state(st.session_state), f)


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
