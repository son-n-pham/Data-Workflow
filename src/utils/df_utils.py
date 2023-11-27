import pandas as pd
import re


def get_columns_by_mnemonics(df, mnemonics):
    """
    Identifies columns in a DataFrame or a Series of Dataframe.columns that contain any of the specified mnemonics.

    Parameters:
    df (pandas.DataFrame or pandas.Series or list): The DataFrame, Series, or list in which to search for columns.
    mnemonics (list of str or str): The mnemonics to search for.

    Returns:
    list of str: The list of column names that contain any of the mnemonics.
    """
    # If df is a DataFrame, get the columns. If it's a Series, convert it to a list. If it's a list, use it directly.
    if isinstance(df, pd.DataFrame):
        columns_to_search = df.columns
    elif isinstance(df, pd.Series):
        columns_to_search = df.tolist()
    else:  # Assume df is a list
        columns_to_search = df

    # If mnemonics is a string, convert it to a list.
    mnemonics = [mnemonics] if isinstance(mnemonics, str) else mnemonics

    columns = []
    for mnemonic in mnemonics:
        for col in df.columns:
            if mnemonic.lower() in col.lower():
                columns.append(col)
                break
    return columns


def get_bounds_for_cluster(df_with_clusters, X_mnemonics, cluster):
    """
    Computes the bounds for each mnemonic in a specified cluster.

    Parameters:
    df_with_clusters (pandas.DataFrame): The DataFrame containing the data and cluster assignments.
    X_mnemonics (list of str): The mnemonics for which to compute the bounds.
    cluster (int): The cluster for which to compute the bounds.

    Returns:
    dict: A dictionary where the keys are mnemonics and the values are (min, max) pairs representing the bounds.
          The minimum bound is either the minimum value of the mnemonic in the cluster or 0.0001 if the minimum value is less than 0.
          The maximum bound is the maximum value of the mnemonic in the cluster, multiplied by 100 for certain mnemonics.
    """
    bounds = {}
    for mnemonic in X_mnemonics:
        # Convert mnemonic to column header
        column_header = get_columns_by_mnemonics(
            df_with_clusters, [mnemonic])[0]
        data_for_cluster = df_with_clusters[df_with_clusters['cluster']
                                            == cluster][column_header]
        min_value = data_for_cluster.min()
        min_bound = min_value if min_value >= 0 else 0.0001
        bounds[mnemonic] = (min_bound, data_for_cluster.max(
        ) * (100 if mnemonic not in ['Si', 'Shale', 'Dolomite', 'Limestone'] else 1))
    return bounds


def get_header_from_mnemonic(header_patterns, mnemonic):
    """
    Returns the header for a given mnemonic.

    Parameters:
    header_patterns (dict): A dictionary where the keys are mnemonics and the values are regular expressions that match the headers.
    mnemonic (str): The mnemonic for which to get the header.

    Returns:
    str: The header for the mnemonic, or None if no header matches.
    """
    for header, pattern in header_patterns.items():
        if pattern is not None and re.match(pattern, mnemonic, re.IGNORECASE):
            return header
    return None
