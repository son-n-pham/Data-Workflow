import numpy as np
import pandas as pd


def clean_df(df, columns):
    df = df.replace(-999.25, np.nan).dropna(subset=columns)
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

# Function to remove outliers from the DataFrame


def remove_outliers(df, columns):
    for column in columns:
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df[column] >= Q1 - 1.5*IQR) & (df[column] <= Q3 + 1.5*IQR)]
    return df


def prepare_data_for_plotting(df, columns):
    # Create a copy of the dataframe with only the selected columns
    columns = list(set(columns))
    df_copy = df[columns].copy()

    # Convert columns to numeric and drop rows where any column is NaN
    df_copy = df_copy.apply(pd.to_numeric, errors='coerce').dropna()

    if df_copy.empty:
        st.warning(
            "The selected data for plotting is empty after removing non-numeric or NaN values.")
        return None

    return df_copy
