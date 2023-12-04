import numpy as np
import pandas as pd
from utils import get_columns_by_mnemonics


def clean_df(df, columns, bit_diameter=8.5):
    """
    Cleans the DataFrame by handling zero values, non-numeric values, specific outliers, and missing values in specified columns.

    This function drops rows where all specified columns are 0, converts the specified columns to numeric (handling non-numeric values by coercing them to NaN), replaces negative numbers or 0 with NaN, drops rows where any specified column is NaN, and adds a 'BIT_DIAMETER (in)' column if it doesn't exist.

    Parameters:
    df (pandas.DataFrame): The input DataFrame to be cleaned.
    columns (list of str): A list of column names to be cleaned.
    bit_diameter (float, optional): The bit diameter to be used in the cleaning process. Defaults to 8.5.

    Returns:
    pandas.DataFrame: The cleaned DataFrame.
    """
    # Drop rows where all specified columns are 0
    df = df.loc[~(df[columns] == 0).all(axis=1)]

    # Convert specified columns to numeric and handle non-numeric values
    df[columns] = df[columns].apply(pd.to_numeric, errors='coerce')

    # Replace negative numbers with NaN
    df[columns] = df[columns].map(lambda x: np.nan if x <= 0 else x)

    # Drop rows where any specified column is NaN
    df = df.dropna(subset=columns)

    # Add bit_diameter column
    df["BIT_DIAMETER (in)"] = df.get("BIT_DIAMETER (in)", bit_diameter)

    return df


def clean_df_by_mnemonics(df, mnemonics, bit_diameter=8.5):
    """
    Cleans the DataFrame based on specified mnemonics.

    This function identifies columns that contain the specified mnemonics (disregarding units and case-sensitivity),
    and then cleans those columns.

    Parameters:
    df (pandas.DataFrame): The input DataFrame to be cleaned.
    mnemonics (list of str): A list of mnemonics. Columns containing these mnemonics will be cleaned.
    bit_diameter (float, optional): The bit diameter to be used in the cleaning process. Defaults to 8.5.

    Returns:
    pandas.DataFrame: The cleaned DataFrame.
    """
    # # Identify columns contain mnemonic disregarding units and case-sensitive
    # columns = []
    # for mnemonic in mnemonics:
    #     columns += [col for col in df.columns if mnemonic.lower()
    #                 in col.lower()]
    columns = get_columns_by_mnemonics(df, mnemonics)

    # Clean the DataFrame
    df = clean_df(df, columns, bit_diameter)

    return df


def remove_outliers(df, columns, cleaned_df=False):
    """
    Removes outliers from specified columns in the DataFrame.

    This function converts the specified columns to numeric (handling non-numeric values by coercing them to NaN),
    and then removes rows where the column value is an outlier, defined as being below Q1 - 1.5*IQR or above Q3 + 1.5*IQR,
    where Q1 and Q3 are the first and third quartiles, respectively, and IQR is the interquartile range.

    Parameters:
    df (pandas.DataFrame): The input DataFrame from which outliers should be removed.
    columns (list of str): A list of column names from which outliers should be removed.
    cleaned_df (bool, optional): If True, the function will not clean the DataFrame before removing outliers. Defaults to False.

    Returns:
    pandas.DataFrame: The DataFrame with outliers removed from the specified columns.
    """
    if not cleaned_df:
        df = clean_df(df, columns)

    # Convert specified columns to numeric and handle non-numeric values
    df[columns] = df[columns].apply(pd.to_numeric, errors='coerce')

    for column in columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df[column] >= Q1 - 1.5*IQR) & (df[column] <= Q3 + 1.5*IQR)]

    return df


def remove_outliers_by_mnemonics(df, mnemonics, cleaned_df=False):
    """
    Removes outliers from the DataFrame based on specified mnemonics.

    This function identifies columns that contain the specified mnemonics (disregarding units and case-sensitivity),
    and then removes outliers from those columns.

    Parameters:
    df (pandas.DataFrame): The input DataFrame from which outliers should be removed.
    mnemonics (list of str): A list of mnemonics. Columns containing these mnemonics will have their outliers removed.
    cleaned_df (bool, optional): If True, the function will return a cleaned DataFrame. Defaults to False.

    Returns:
    pandas.DataFrame: The DataFrame with outliers removed from the specified columns.
    """
    # Identify columns contain mnemonic disregarding units and case-sensitive
    columns = get_columns_by_mnemonics(df, mnemonics)

    # Remove outliers
    df = remove_outliers(df, columns, cleaned_df)

    return df
