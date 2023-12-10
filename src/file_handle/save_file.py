import os
import pandas as pd
import numpy as np
import streamlit as st
from config import temp_directory, each_project_folders
from utils import ensure_directory_exists


def save_uploaded_file(uploaded_file,
                       uploaded_folder=os.path.join(temp_directory, each_project_folders["raw_data_folder"])):
    """
    Save an uploaded file to a specified folder.

    This function takes an uploaded file and saves it to a specified folder.
    If the folder does not exist, it is created. The file is saved with the
    same name it had when it was uploaded.

    Saving the uploaded file before reading from it provides better control
    over file handling. It ensures that the file is correctly received and
    stored before any operations are performed on it.

    Parameters
    ----------
    uploaded_file : UploadedFile
        The file uploaded by the user.
    uploaded_folder : str, optional
        The directory where the uploaded file will be saved. By default, this is
        set to the value of folder["uploaded_folder"].

    Returns
    -------
    str
        The absolute path to the saved file. If no file was uploaded, returns None.
    """
    if uploaded_file is not None:
        # Create a uploaded_folder if it doesn't exist
        ensure_directory_exists(uploaded_folder)

        # Write the file to the new uploaded_folder
        file_path = os.path.join(uploaded_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Get the absolute path
        absolute_file_path = os.path.abspath(file_path)
        return absolute_file_path

    return None


def save_cleaned_df_to_file_and_update_session_state(cleaned_df):
    """
    Save a cleaned DataFrame to a CSV file and update the session state.

    This function takes a cleaned DataFrame as input. It saves the DataFrame to a CSV file
    in the "cleaned_data_folder" in temp_folder, and updates the session state of loaded_file
    to reflect the new file path.

    Parameters:
    cleaned_df (pandas.DataFrame): The cleaned DataFrame to be saved.

    Returns:
    None
    """
    # Save the cleaned df to a new file
    # with the same name, but in cleaned_data_folder
    cleaned_file_path = os.path.join(os.path.join(
        temp_directory,
        each_project_folders['cleaned_data_folder']),
        os.path.basename(st.session_state['loaded_file']))

    ensure_directory_exists(os.path.join(os.path.join(
        temp_directory,
        each_project_folders['cleaned_data_folder'])))

    # Save cleaned df to cleaned_data_folder in temp_folder
    df = unmerge_df_headers_and_save_file(cleaned_df, cleaned_file_path)

    # Update st.session_state['loaded_file'] to the cleaned file
    st.session_state['loaded_file'] = cleaned_file_path

    return df


def save_clustered_df_to_file_and_update_session_state(clustered_df):
    """
    Clustering is applied to the cleaned DataFrame and the clustered DataFrame is saved to a CSV file.

    As clustering is only added clustered columns but not change the original cleaned DataFrame, it is fine to save the clustered DataFrame to a CSV file
    with the same name as the cleaned DataFrame.

    Parameters:
    clustered_df (pandas.DataFrame): The clustered DataFrame to be saved.

    Returns:
    None
    """
    return save_cleaned_df_to_file_and_update_session_state(clustered_df)


def unmerge_df_headers_and_save_file(df, file_path):
    """
    Splits the headers of a DataFrame and saves the DataFrame to a CSV file.

    This function takes a DataFrame and a file path as input. It splits the headers of the DataFrame
    into separate parts, creates a new DataFrame with the split headers, and saves the new DataFrame
    to a CSV file at the given path.

    Parameters:
    df (pandas.DataFrame): The input DataFrame with headers to be split.
    file_path (str): The path where the new DataFrame should be saved as a CSV file.

    Returns:
    None
    """
    new_df = pd.DataFrame(index=df.index)

    for column in df.columns:
        header = column.split("(")[0].strip()
        new_df[header] = df[column]

    new_df.loc[0] = [column.split("(")[-1].split(")")[0].strip() if ")" in column else np.nan
                     for column in df.columns]

    new_df.sort_index(inplace=True)

    new_df.to_csv(file_path, index=False)

    return new_df
