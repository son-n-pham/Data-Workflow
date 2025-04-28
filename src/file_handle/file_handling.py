import pandas as pd
import os
from pandas.errors import EmptyDataError
import streamlit as st
from collections import Counter  # Import Counter for duplicate handling


def read_file(file_path_or_buffer, file_type="csv"):
    """
    Reads a file (CSV, Excel, TXT) into a pandas DataFrame, trying different encodings and delimiters.

    Args:
        file_path_or_buffer: The path to the file or a file-like object.
        file_type (str): The type of file ('csv', 'excel', 'txt').

    Returns:
        pandas.DataFrame: The processed DataFrame with a combined header.

    Raises:
        ValueError: If the file type is unsupported.
        FileNotFoundError: If the file path does not exist.
        EmptyDataError: If the file is empty after trying all options.
        UnicodeDecodeError: If the file cannot be decoded with tried encodings.
        Exception: For other pandas or file reading errors.
    """
    encodings = ["utf-8", "latin-1", "ISO-8859-1", "utf-16"]
    delimiters = [",", "\t", ";", " "]  # Define delimiters relevant for CSV/TXT

    read_funcs = {
        "csv": pd.read_csv,
        "excel": pd.read_excel,
        "txt": pd.read_csv,  # Treat txt like csv for reading purposes
    }

    if file_type not in read_funcs:
        raise ValueError(
            f"Unsupported file type: {file_type}. Supported types are: {list(read_funcs.keys())}"
        )

    read_func = read_funcs[file_type]
    last_exception = None

    # Common arguments for read functions
    common_args = {"header": None}

    for encoding in encodings:
        # Arguments specific to this iteration
        current_args = common_args.copy()
        current_args["encoding"] = encoding

        # Only iterate through delimiters for text-based formats
        if file_type in ["csv", "txt"]:
            for delimiter in delimiters:
                try:
                    current_args["delimiter"] = delimiter
                    # Use low_memory=False for potentially mixed type columns often seen in CSVs
                    if file_type == "csv":
                        current_args["low_memory"] = False
                    df = read_func(file_path_or_buffer, **current_args)
                    # Reset buffer position if it's a file-like object for the next try
                    if hasattr(file_path_or_buffer, "seek"):
                        file_path_or_buffer.seek(0)
                    if not df.empty:
                        # Check if DataFrame has enough rows before setting header
                        if len(df) < 2:
                            # Handle files with less than 2 rows (e.g., only header or empty)
                            # Option 1: Return as is (or with minimal processing)
                            # return df # Or apply alternative processing
                            # Option 2: Raise an error if this structure is invalid
                            raise ValueError(
                                f"File '{get_base_filename(file_path_or_buffer)}' has less than 2 rows required for header generation."
                            )
                        return set_header(df, file_path_or_buffer)
                    else:
                        # Store EmptyDataError but continue trying other options
                        if not isinstance(last_exception, EmptyDataError):
                            last_exception = EmptyDataError(
                                f"No columns to parse from file '{get_base_filename(file_path_or_buffer)}' with encoding '{encoding}' and delimiter '{delimiter}'"
                            )
                except (UnicodeDecodeError, EmptyDataError, pd.errors.ParserError) as e:
                    last_exception = e
                    # Reset buffer position if it's a file-like object
                    if hasattr(file_path_or_buffer, "seek"):
                        file_path_or_buffer.seek(0)
                    continue  # Try next delimiter/encoding
                except Exception as e:  # Catch other potential pandas errors
                    last_exception = e
                    if hasattr(file_path_or_buffer, "seek"):
                        file_path_or_buffer.seek(0)
                    continue
        elif file_type == "excel":
            try:
                # Don't pass delimiter to read_excel
                df = read_func(
                    file_path_or_buffer, encoding=encoding, header=common_args["header"]
                )
                # Reset buffer position if it's a file-like object
                if hasattr(file_path_or_buffer, "seek"):
                    file_path_or_buffer.seek(0)
                if not df.empty:
                    if len(df) < 2:
                        raise ValueError(
                            f"File '{get_base_filename(file_path_or_buffer)}' has less than 2 rows required for header generation."
                        )
                    return set_header(df, file_path_or_buffer)
                else:
                    if not isinstance(last_exception, EmptyDataError):
                        last_exception = EmptyDataError(
                            f"No columns to parse from file '{get_base_filename(file_path_or_buffer)}' (Excel) with encoding '{encoding}'"
                        )
            except (
                UnicodeDecodeError,
                EmptyDataError,
            ) as e:  # Add other relevant Excel errors if needed
                last_exception = e
                if hasattr(file_path_or_buffer, "seek"):
                    file_path_or_buffer.seek(0)
                continue  # Try next encoding
            except Exception as e:
                last_exception = e
                if hasattr(file_path_or_buffer, "seek"):
                    file_path_or_buffer.seek(0)
                continue

    # If loop finishes without returning, raise the last encountered exception
    if last_exception:
        raise last_exception
    else:
        # Should not happen if input is valid, but as a fallback
        raise Exception(
            f"Could not read file '{get_base_filename(file_path_or_buffer)}' with any tried encoding/delimiter combination."
        )


def get_base_filename(file_path_or_buffer):
    """Safely extracts the base filename without extension."""
    try:
        # Handle file path strings
        if isinstance(file_path_or_buffer, str):
            return os.path.splitext(os.path.basename(file_path_or_buffer))[0]
        # Handle file-like objects (e.g., from Streamlit upload)
        elif hasattr(file_path_or_buffer, "name"):
            return os.path.splitext(os.path.basename(file_path_or_buffer.name))[0]
        else:
            return "unknown_file"
    except Exception:
        return "unknown_file"


def generate_unique_header(header_list):
    """Makes header names unique by appending counts to duplicates."""
    counts = Counter(header_list)
    new_header = []
    seen_counts = Counter()
    for col in header_list:
        if counts[col] > 1:
            seen_counts[col] += 1
            new_header.append(f"{col}_{seen_counts[col]}")
        else:
            new_header.append(col)
    return new_header


# Function to set the header of the DataFrame
def set_header(df, file_path_or_buffer):
    """
    Sets a combined header from the first two rows and adds a 'well' column.

    Args:
        df (pandas.DataFrame): The DataFrame to process (must have at least 2 rows).
        file_path_or_buffer: The original file path or buffer to extract the filename.

    Returns:
        pandas.DataFrame: DataFrame with new header, first two rows removed, and 'well' column.
    """
    if len(df) < 2:
        # This check is now also in read_file, but kept here for direct use safety
        raise ValueError("DataFrame must have at least two rows to generate header.")

    df = df.copy()  # Create a copy to avoid SettingWithCopyWarning
    # Combine first two rows, stripping whitespace
    header_row1 = df.iloc[0].astype(str).str.strip()
    header_row2 = df.iloc[1].astype(str).str.strip()
    combined_header = (header_row1 + "__" + header_row2).tolist()

    # Make header names unique
    unique_header = generate_unique_header(combined_header)

    df = df.iloc[2:].reset_index(drop=True)  # Remove the first two rows and reset index
    df.columns = unique_header  # Set the new unique header

    # Get the base file name (without extension) safely
    base_file_name = get_base_filename(file_path_or_buffer)
    df["well"] = (
        base_file_name  # Use .loc potentially if needed, but direct assignment is often fine here
    )

    return df


# Streamlit-specific function remains largely the same, but calls the improved read_file
def st_read_file(uploaded_file):
    """
    Reads an uploaded file via Streamlit and displays status.

    Args:
        uploaded_file: The file object from st.file_uploader.

    Returns:
        pandas.DataFrame or None: The processed DataFrame, or None if upload is invalid.
    """
    if uploaded_file is None:
        st.warning("Please upload a file.")
        return None

    # Display info (optional, can be moved outside this function)
    # st.write(f"Processing uploaded file: {uploaded_file.name}")
    # st.markdown("---")

    try:
        file_type = uploaded_file.name.split(".")[-1].lower()
        # Pass the file object (buffer) directly to read_file
        df = read_file(uploaded_file, file_type)
        # st.success(f"Successfully processed file: {uploaded_file.name}") # Optional success message
        return df
    except (ValueError, FileNotFoundError, EmptyDataError, UnicodeDecodeError) as e:
        st.error(f"Error reading file '{uploaded_file.name}': {e}")
        return None
    except Exception as e:  # Catch any other unexpected errors
        st.error(
            f"An unexpected error occurred while processing '{uploaded_file.name}': {e}"
        )
        # Consider logging the full traceback here for debugging
        # import traceback
        # st.error(traceback.format_exc())
        return None
