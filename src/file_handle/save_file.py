import os
import pandas as pd
import numpy as np
import streamlit as st
from config import temp_directory, each_project_folders
from utils import ensure_directory_exists


def save_uploaded_file(
    uploaded_file,
    uploaded_folder=os.path.join(
        temp_directory, each_project_folders["raw_data_folder"]
    ),
):
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
    cleaned_file_path = os.path.join(
        os.path.join(temp_directory, each_project_folders["cleaned_data_folder"]),
        os.path.basename(st.session_state["loaded_file"]),
    )

    ensure_directory_exists(
        os.path.join(
            os.path.join(temp_directory, each_project_folders["cleaned_data_folder"])
        )
    )

    # Save cleaned df to cleaned_data_folder in temp_folder
    df = unmerge_df_headers_and_save_file(cleaned_df, cleaned_file_path)

    # Update st.session_state['loaded_file'] to the cleaned file
    st.session_state["loaded_file"] = cleaned_file_path

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
    Unmerges the headers of a DataFrame (e.g., "Header (Unit)") into two rows:
    one for the header and one for the unit. Saves the modified DataFrame to a file.

    Args:
        df (pd.DataFrame): The DataFrame with merged headers.
        file_path (str): The path where the modified DataFrame should be saved.

    Returns:
        pd.DataFrame: The DataFrame with unmerged headers.
    """
    new_df = pd.DataFrame()
    # Keep track of the original column name associated with each new header
    # This handles cases where duplicate base headers might cause overwrites.
    # We map the final header to the *last* original column that generated it.
    header_to_original_col = {}

    for column in df.columns:
        # Extract the main header part (before the parenthesis)
        header = column.split("(")[0].strip()
        # Assign the original column data to the new header in new_df
        new_df[header] = df[column]
        # Store the mapping from the potentially simplified header back to its original full name
        header_to_original_col[header] = column

    # Generate the units row based on the actual columns in new_df
    units_row = []
    for header in new_df.columns:
        original_column = header_to_original_col[header]
        unit = ""
        # Extract unit from the original column name if parentheses are present
        if "(" in original_column and ")" in original_column:
            try:
                unit = original_column.split("(")[-1].split(")")[0].strip()
            except IndexError:
                unit = ""  # Handle cases where splitting might fail unexpectedly
        units_row.append(unit)

    # Assign the units row (now guaranteed to match the number of columns in new_df)
    # Ensure the index exists before assigning; inserting might be safer.
    # Temporarily add a dummy row if df was empty, then replace it.
    if 0 not in new_df.index:
        # If the original df was empty, new_df might be too.
        # Or if index doesn't start at 0. Let's use insert for safety.
        # Create a temporary DataFrame for the units row
        units_df = pd.DataFrame([units_row], columns=new_df.columns, index=[0])
        # Concatenate and sort to place the units row at index 0
        new_df = pd.concat([units_df, new_df]).sort_index()
    else:
        # If index 0 already exists (e.g., from original data), overwrite it.
        # This assumes the original data doesn't meaningfully use index 0.
        # A safer approach might be to shift existing indices up first.
        # Let's stick to the original intent of using loc[0] for units.
        new_df.loc[0] = units_row
        new_df.sort_index(inplace=True)  # Ensure row 0 is at the top

    # Save the DataFrame using the provided file_path
    # Example saving logic (replace with your actual saving method if different)
    try:
        # Assuming saving to Excel, adjust if saving to CSV or other formats
        new_df.to_excel(file_path, index=False)
        print(f"Successfully saved unmerged DataFrame to {file_path}")
    except Exception as e:
        print(f"Error saving DataFrame to {file_path}: {e}")
        # Optionally re-raise the exception or handle it as needed
        raise

    return new_df
