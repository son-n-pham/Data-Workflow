import pandas as pd
from . import headers, units, units_config


def load_file_into_dataframe(file_path):
    """
    Load a file into a pandas DataFrame.

    This function tries to load a file from the given file path into a pandas DataFrame.
    It supports CSV, Excel, and text files, and tries different encodings if necessary.
    If the file cannot be loaded, it returns None.

    Parameters:
    file_path (str): The path to the file to be loaded.

    Returns:
    df (pandas.DataFrame): The DataFrame loaded from the file, or None if the file could not be loaded.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, header=[0, 1])
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path, header=[0, 1])
        elif file_path.endswith('.txt'):
            # adjust delimiter as needed
            df = pd.read_csv(file_path, header=[0, 1], delimiter='\t')
        else:
            print(f"Unsupported file type: {file_path}")
            return None
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, header=[0, 1], encoding='latin1')
        except Exception as e:
            print(f"Could not load file: {e}")
            return None
    except Exception as e:
        print(f"Could not load file: {e}")
        return None

    return df


def load_file_and_merge_headers(file_path):

    # Load the dataset, assuming the first two rows are header and units
    data = load_file_into_dataframe(file_path)

    # Display the first few rows of the dataset to understand its structure
    print("The first few rows of the original dataset are:")
    print(data.head())

    # Extracting headers and units
    headers = [header.strip() for header in data.columns.get_level_values(0)]
    units = [unit.strip() for unit in data.columns.get_level_values(1)]

    # Creating a data dictionary
    data_dictionary = {header: unit for header, unit in zip(headers, units)}

    # Modifying the DataFrame to have a single header row
    # Concatenating mnemonic and unit to create a unique identifier for each column
    new_columns = [f"{header} ({unit})" for header,
                   unit in zip(headers, units)]
    data.columns = new_columns

    return data
