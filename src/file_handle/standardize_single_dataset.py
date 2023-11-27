import pandas as pd
from . import headers, units, units_config, load_file


def load_file_standardize_header(file_path):
    """
    Load a file, standardize the headers, and convert the units.

    This function performs three main operations:

    1. File Loading and Header Merging: It first loads a file from the given file path into a pandas DataFrame using the `load_file_and_merge_headers` function. This function also merges the header and unit rows into a single header row.

    2. Header Standardization: After the file is loaded, the function standardizes the headers of the DataFrame using the `standardize_mnemonics` function. This involves mapping the headers to a standard set of mnemonics, which makes the data easier to work with.

    3. Unit Conversion: Finally, the function converts the units of the DataFrame columns using the `standardize_units` function. This is done using a set of predefined conversion mappings. Each column's unit is mapped to a standard unit, and a conversion function is applied to convert the data in the column to the standard unit.

    Parameters:
    file_path (str): The path to the file to be loaded. This should be a full path, including the file name and extension.

    Returns:
    df (pandas.DataFrame): The DataFrame with standardized headers and units.
    """
    df = load_file.load_file_and_merge_headers(file_path)
    df = headers.standardize_mnemonics(df)
    df = units.standardize_units(df, units_config.unit_conversion_mappings)
    return df


if __name__ == '__main__':
    file_path = r'c:/development/MSE_analysis/data_to_work/well_1.csv'
    df = load_file_standardize_header(file_path)