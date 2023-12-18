import objgraph
from datetime import datetime
import os
import streamlit as st
import json

from config import temp_directory, each_project_folders
from utils import ensure_directory_exists
from feature_registry import GraphFeature, Feature, FEATURE_REGISTRY


def serialize_feature_obj(obj):
    """
    Serialize a Feature object to a dictionary.

    This function converts a Feature object to a dictionary using the .dict() method provided by Pydantic's BaseModel.
    If the object is a datetime, it converts it to an ISO 8601 string.
    If the object is not a Feature or a datetime, it returns the object as is.

    Args:
        obj (Feature or datetime or any type): The object to serialize.

    Returns:
        dict or str or any type: The serialized object. If obj is a Feature, this is a dictionary.
        If obj is a datetime, this is a string. Otherwise, this is the original object.
    """
    if isinstance(obj, Feature):
        return obj.dict()
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def clear_session_state_values():
    keys = list(st.session_state.keys())
    st.session_state.clear()
    for key in keys:
        st.session_state[key] = None


# def save_state_file_to_json(state_file='state.json', folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
#     """
#     Save the current session state to a JSON file.

#     This function serializes the state to a JSON string using the json.dumps function,
#     with the default parameter set to serialize_feature_obj to handle Feature objects.

#     Args:
#         state_file (str, optional): The name of the file to save the state to. Defaults to 'state.json'.
#         folder (str, optional): The folder to save the file in. Defaults to the state folder in the temp directory.
#     """
#     file_path = os.path.join(folder, state_file)
#     ensure_directory_exists(folder)
#     dict_session_state = dict(st.session_state)

#     with open(file_path, "w") as file:
#         json.dump(dict_session_state, file, default=serialize_feature_obj)


def find_circular_ref(obj):
    # Show the top 10 objects that have the most references to them
    objgraph.show_most_common_types(limit=10)

    # Show a graph of all objects that reference `obj` and lead to a circular reference
    objgraph.show_backrefs([obj], max_depth=10, filename='backrefs.png')
# def save_state_file_to_json(state_file='state.json', folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
#     """
#     Save the current session state to a JSON file.

#     This function serializes the state to a JSON string using the json.dumps function,
#     with the default parameter set to serialize_feature_obj to handle Feature objects.

#     Args:
#         state_file (str, optional): The name of the file to save the state to. Defaults to 'state.json'.
#         folder (str, optional): The folder to save the file in. Defaults to the state folder in the temp directory.
#     """
#     file_path = os.path.join(folder, state_file)
#     ensure_directory_exists(folder)
#     dict_session_state = dict(st.session_state)

#     # Use the function before json.dumps
#     find_circular_ref(dict_session_state)

#     try:
#         json_str = json.dumps(dict_session_state,
#                               default=serialize_feature_obj)
#         print(json_str)
#     except Exception as e:
#         # Write e to log file with date and time
#         print("***********************************")
#         print("Error during JSON serialization:", e)
#         print("***********************************")
#         st.write("Error during JSON serialization:", e)
#         return

#     with open(file_path, "w") as file:
#         file.write(json_str)


def feature_to_dict(feature):
    # Replace this with your actual conversion logic
    return feature.__dict__


def save_state_file_to_json(state_file='state.json', folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
    """
    Save the current session state to a JSON file.

    This function serializes the state to a JSON string using the json.dumps function,
    with the default parameter set to serialize_feature_obj to handle Feature objects.

    Args:
        state_file (str, optional): The name of the file to save the state to. Defaults to 'state.json'.
        folder (str, optional): The folder to save the file in. Defaults to the state folder in the temp directory.
    """
    file_path = os.path.join(folder, state_file)
    ensure_directory_exists(folder)

    # Create a shallow copy of st.session_state
    dict_session_state = dict(st.session_state)

    # Convert the 'features' list to a list of dictionaries
    if 'features' in dict_session_state:
        dict_session_state['features'] = [feature_to_dict(
            feature) for feature in dict_session_state['features']]

    # Print out the session state for debugging
    print("********** SESSION STATE START **********")
    print(dict_session_state)
    print("********** SESSION STATE END **********")

    # # Use the function before json.dumps
    # find_circular_ref(dict_session_state)

    # Remove state.json in state_folder in temp_folder
    if os.path.exists(file_path):
        os.remove(file_path)
    # Write the session state to a JSON file
    try:
        with open(file_path, 'w') as f:
            json.dump(dict_session_state, f, default=serialize_feature_obj)
    except Exception as e:
        # Write e to log file with date and time
        print("***********************************")
        print("Error during JSON serialization:", e)
        print("***********************************")
        st.write("Error during JSON serialization:", e)
        return


def deserialize_feature_obj(dct):
    if 'name' in dct and 'feature_type' in dct:
        feature_type = dct['feature_type']
        if feature_type in FEATURE_REGISTRY:
            FeatureClass = FEATURE_REGISTRY[feature_type]
            return FeatureClass(name=dct['name'], parameters=dct.get('parameters'), created_at=dct.get('created_at'), activated=dct.get('activated'))
    return dct


def load_state_file_from_json(state_file='state.json', state_folder=os.path.join(temp_directory, each_project_folders["state_folder"])):
    """
    Load the session state from a JSON file.

    This function deserializes the state from a JSON string using the json.loads function,
    with the object_hook parameter set to deserialize_feature_obj to handle Feature objects.

    Args:
        state_file (str, optional): The name of the file to load the state from. Defaults to 'state.json'.
        state_folder (str, optional): The folder to load the file from. Defaults to the state folder in the temp directory.

    Returns:
        dict: The loaded state.
    """
    json_file_path = os.path.join(state_folder, state_file)
    if not os.path.exists(json_file_path):
        st.error(
            f"State file {state_file} does not exist in the directory {state_folder}")
        return

    clear_session_state_values()

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
