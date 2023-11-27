import pandas as pd
import os
from pandas.errors import EmptyDataError
import streamlit as st


def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        # Create a directory if it doesn't exist
        directory = 'uploaded_files'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the file to the new directory
        file_path = os.path.join(directory, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Get the absolute path
        absolute_file_path = os.path.abspath(file_path)
        return absolute_file_path

    return None


def read_file(file_name, file_type='csv'):
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'utf-16']
    delimiters = [',', '\t', ';', ' ']
    read_funcs = {
        'csv': pd.read_csv,
        'excel': pd.read_excel,
        'txt': lambda file, encoding, header, delimiter: pd.read_csv(file, encoding=encoding, header=header, delimiter=delimiter)
    }
    read_args = {
        'csv': {'header': None},
        'excel': {'header': None},
        'txt': {'header': None}
    }

    last_unicode_exception = None
    last_empty_data_exception = None

    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = read_funcs[file_type](
                    file_name, encoding=encoding, header=read_args[file_type]['header'], delimiter=delimiter)
                return set_header(df, file_name)
            except UnicodeDecodeError as e:
                last_unicode_exception = e
                continue
            except EmptyDataError as e:
                last_empty_data_exception = e
                continue

        if last_empty_data_exception:
            raise last_empty_data_exception
        if last_unicode_exception:
            raise last_unicode_exception

    raise last_empty_data_exception if last_empty_data_exception else last_unicode_exception


# Function to set the header of the DataFrame
def set_header(df, file_name):
    df = df.copy()  # Create a copy of the DataFrame
    header = df.iloc[0].str.strip() + '__' + df.iloc[1].str.strip()
    header = pd.Series(header).apply(lambda x: x if header.tolist().count(x) == 1
                                     else x + '_' + str(header.tolist().index(x)))
    df = df.iloc[2:]  # Remove the first two rows
    df.columns = header  # Set the new header
    # Get the file name (without extension)
    try:
        file_name = file_name.split('.')[-2]
    except AttributeError:
        file_name = file_name.name.split('.')[-2]
    df.loc[:, "well"] = file_name

    return df


def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        # Create a directory if it doesn't exist
        directory = 'uploaded_files'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the file to the new directory
        file_path = os.path.join(directory, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Get the absolute path
        absolute_file_path = os.path.abspath(file_path)
        return absolute_file_path

    return None


def read_file(file_name, file_type='csv'):
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'utf-16']
    delimiters = [',', '\t', ';', ' ']
    read_funcs = {
        'csv': pd.read_csv,
        'excel': pd.read_excel,
        'txt': lambda file, encoding, header, delimiter: pd.read_csv(file, encoding=encoding, header=header, delimiter=delimiter)
    }
    read_args = {
        'csv': {'header': None},
        'excel': {'header': None},
        'txt': {'header': None}
    }

    last_unicode_exception = None
    last_empty_data_exception = None

    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = read_funcs[file_type](
                    file_name, encoding=encoding, header=read_args[file_type]['header'], delimiter=delimiter)
                return set_header(df, file_name)
            except UnicodeDecodeError as e:
                last_unicode_exception = e
                continue
            except EmptyDataError as e:
                last_empty_data_exception = e
                continue

        if last_empty_data_exception:
            raise last_empty_data_exception
        if last_unicode_exception:
            raise last_unicode_exception

    raise last_empty_data_exception if last_empty_data_exception else last_unicode_exception


# Function to set the header of the DataFrame
def set_header(df, file_name):
    df = df.copy()  # Create a copy of the DataFrame
    header = df.iloc[0].str.strip() + '__' + df.iloc[1].str.strip()
    header = pd.Series(header).apply(lambda x: x if header.tolist().count(x) == 1
                                     else x + '_' + str(header.tolist().index(x)))
    df = df.iloc[2:]  # Remove the first two rows
    df.columns = header  # Set the new header
    # Get the file name (without extension)
    try:
        file_name = file_name.split('.')[-2]
    except AttributeError:
        file_name = file_name.name.split('.')[-2]
    df.loc[:, "well"] = file_name

    return df


def st_read_file(file_object):
    st.write(f"From st_read_file function, Uploaded file is: {file_object}")

    st.markdown("---")

    file_type = file_object.name.split('.')[-1]

    df = read_file(file_object, file_type)

    return df
