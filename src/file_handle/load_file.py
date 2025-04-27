import pandas as pd
from . import headers, units, units_config
import streamlit as st


def load_file_into_dataframe(file_path):
    """
    Load a file into a pandas DataFrame.

    This function tries to load a file from the given file path into a pandas DataFrame.
    It supports CSV, Excel, and text files, and tries different encodings if necessary.
    It also treats -999.25 and -999 as NaN values.
    If the file cannot be loaded, it returns None.

    Parameters:
    file_path (str): The path to the file to be loaded.

    Returns:
    df (pandas.DataFrame): The DataFrame loaded from the file, or None if the file could not be loaded.
    """
    na_vals = [-999.25, -999]  # Define values to treat as NaN
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, header=[0, 1], na_values=na_vals)
        elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            df = pd.read_excel(file_path, header=[0, 1], na_values=na_vals)
        elif file_path.endswith(".txt"):
            # adjust delimiter as needed
            df = pd.read_csv(
                file_path, header=[0, 1], delimiter="\t", na_values=na_vals
            )
        else:
            print(f"Unsupported file type: {file_path}")
            return None
    except UnicodeDecodeError:
        try:
            # Attempt with latin1 encoding if default fails
            df = pd.read_csv(
                file_path, header=[0, 1], encoding="latin1", na_values=na_vals
            )
        except Exception as e:
            print(f"Could not load file with latin1 encoding: {e}")
            return None
    except Exception as e:
        print(f"Could not load file: {e}")
        return None

    return df


def load_file_and_merge_headers(file_path):
    # Load the dataset, assuming the first two rows are header and units
    data = load_file_into_dataframe(file_path)

    # Check if data loading was successful
    if data is None:
        return None

    # Extracting headers and units
    headers = [str(header).strip() for header in data.columns.get_level_values(0)]
    units = [str(unit).strip() for unit in data.columns.get_level_values(1)]

    # Modifying the DataFrame to have a single header row
    # Concatenating mnemonic and unit to create a unique identifier for each column
    new_columns = [f"{header} ({unit})" for header, unit in zip(headers, units)]
    data.columns = new_columns

    return data


def st_read_file(file_path):
    st.write(f"From st_read_file function, Uploaded file is: {file_path}")

    st.markdown("---")

    df = load_file_and_merge_headers(file_path)

    return df
