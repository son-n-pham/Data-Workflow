import os
import shutil
import pickle


def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def list_sub_folders(directory):
    ensure_directory_exists(directory)
    return [f.name for f in os.scandir(directory) if f.is_dir()]


def copy_folder(original_folder_path, new_folder_path):
    """
    Copy a project folder. Overwrites the new folder if it already exists.

    Parameters
    ----------
    original_folder_path : str
        The path to the original project folder.
    new_folder_path : str
        The path to the new project folder.

    Returns
    -------
    None
    """
    # List of subfolders to copy
    sub_folders = list_sub_folders(original_folder_path)

    # Check if the directory exists, and if it does, remove it
    if os.path.exists(new_folder_path):
        shutil.rmtree(new_folder_path)

    shutil.copytree(original_folder_path, new_folder_path, dirs_exist_ok=True)


def delete_folder(folder_path):
    """
    Delete a project folder.

    Parameters
    ----------
    folder_path : str
        The path to the project folder.

    Returns
    -------
    None
    """
    shutil.rmtree(folder_path)


def load_pickle_file_to_dict(file_path):
    """
    Load a pickle file to a dictionary.

    Parameters
    ----------
    file_path : str
        The path to the pickle file.

    Returns
    -------
    dict
        The dictionary containing the data from the pickle file.
    """
    with open(file_path, "rb") as f:
        return pickle.load(f)
