import pandas as pd
import numpy as np

# Remove 'headers' if it's not used from the import below
from . import units, units_config
import streamlit as st

# Define the core values to be treated as NaN
NA_VALUES_LIST = [-999.25, -999, "nodata"]
# Separate numeric and string representations
NUMERIC_NA_SET = {val for val in NA_VALUES_LIST if isinstance(val, (int, float))}
# Store string representations, stripped, for comparison
STRING_NA_SET = {str(val).strip() for val in NA_VALUES_LIST}


def robust_nan_conversion(value, numeric_na_set, string_na_set):
    """
    Helper function to robustly convert values to NaN.

    Checks for:
    1. Pre-existing NaNs.
    2. Direct numeric match with values in numeric_na_set.
    3. String match (after stripping) with values in string_na_set.
    """
    # Keep existing NaNs
    if pd.isna(value):
        return np.nan

    # 1. Check for direct numeric match
    # Use isinstance to avoid comparing numbers with strings directly
    if isinstance(value, (int, float)):
        # Direct comparison should be okay for -999 and -999.25
        # Use np.isclose if very high precision matching is needed later
        if value in numeric_na_set:
            return np.nan
        # Explicitly check if -999.0 should map to -999
        # This handles cases where integer -999 might be loaded as float -999.0
        elif value == -999.0 and -999 in numeric_na_set:
            return np.nan

    # 2. Check for string match (handles 'nodata' and numbers read as strings)
    try:
        # Convert value to string, strip whitespace
        stripped_value = str(value).strip()
        # Check if the stripped string is in our set of NaN string representations
        if stripped_value in string_na_set:
            return np.nan
    except Exception:
        # In case of error during conversion/stripping, proceed without converting to NaN
        pass

    # Return the original value if no NaN condition matched
    return value


def load_file_into_dataframe(file_path):
    """
    Load a file into a pandas DataFrame.

    This function tries to load a file from the given file path into a pandas DataFrame.
    It supports CSV, Excel, and text files, and tries different encodings if necessary.
    It robustly treats values matching NA_VALUES_LIST (handling types and whitespace) as NaN *after* loading.
    If the file cannot be loaded, it returns None.

    Parameters:
    file_path (str): The path to the file to be loaded.

    Returns:
    df (pandas.DataFrame): The DataFrame loaded from the file with specified values converted to NaN,
                           or None if the file could not be loaded.
    """
    df = None  # Initialize df
    try:
        # Load data WITHOUT na_values initially. We'll handle NaNs robustly after loading.
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, header=[0, 1])
        elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            df = pd.read_excel(file_path, header=[0, 1])
        elif file_path.endswith(".txt"):
            # adjust delimiter as needed
            df = pd.read_csv(file_path, header=[0, 1], delimiter="\t")
        else:
            print(f"Unsupported file type: {file_path}")
            return None
    except UnicodeDecodeError:
        try:
            # Attempt with latin1 encoding if default fails
            df = pd.read_csv(file_path, header=[0, 1], encoding="latin1")
        except Exception as e:
            print(f"Could not load file with latin1 encoding: {e}")
            return None
    except Exception as e:
        print(f"Could not load file: {e}")
        return None

    # Post-processing: Apply robust NaN conversion across the entire DataFrame
    if df is not None:
        # Pass the pre-calculated sets to the function via lambda
        df = df.map(lambda x: robust_nan_conversion(x, NUMERIC_NA_SET, STRING_NA_SET))

    return df


def load_file_and_merge_headers(file_path):
    # Load the dataset, assuming the first two rows are header and units
    data = load_file_into_dataframe(file_path)

    # Check if data loading was successful
    if data is None:
        return None

    # Extracting headers and units
    # Ensure column levels are treated as strings before stripping
    headers_level = data.columns.get_level_values(0)
    units_level = data.columns.get_level_values(1)

    headers = [str(header).strip() for header in headers_level]
    units = [str(unit).strip() for unit in units_level]

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
