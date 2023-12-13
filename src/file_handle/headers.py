import re
import pandas as pd
from . import headers_config
import config


def map_mnemonic(mnemonic, unit, rpm_values):
    """
    Map the given mnemonic to a standardized form using regex patterns.
    Case-insensitive matching is used to capture various cases.
    Units are also considered in the mapping process.
    """
    patterns = config.header_patterns

    # Set the pattern for "VOLUME" dynamically based on the unit
    patterns["VOLUME"] = headers_config.get_volume_pattern(unit)

    for std_mnemonic, pattern in patterns.items():
        if pattern and re.match(pattern, mnemonic, re.IGNORECASE):
            return f"{std_mnemonic} ({unit})"

    # For ambiguous RPM cases
    if 'RPM' in mnemonic.upper():
        return analyze_rpm_context(mnemonic, unit, rpm_values)

    return analyze_context(mnemonic, unit)


def analyze_context(mnemonic, unit):
    """
    Analyze the context of the mnemonic for accurate mapping.
    This function is used for mnemonics that require context-based interpretation.
    """
    # Contextual analysis logic goes here
    # Example:
    if "__unidentified" in mnemonic:
        return f"{mnemonic} ({unit})"

    if "TEMP" in mnemonic:
        return "TEMPERATURE (C)" if "c" in unit.lower() else "TEMPERATURE (F)"

    # Mark as unidentified if no contextual rule applies
    return f"{mnemonic}__unidentified ({unit})"


def analyze_rpm_context(mnemonic, unit, rpm_values):
    """
    Analyze the context for RPM-related mnemonics based on values and occurrence.
    """
    avg_rpm_value = rpm_values.get(mnemonic, 0)
    surface_rpm_present = any(re.match(
        r".*SURF.*RPM.*|.*SURFACE.*RPM.*", m, re.IGNORECASE) for m in rpm_values)
    motor_rpm_present = any(
        re.match(r".*MOTOR.*RPM.*", m, re.IGNORECASE) for m in rpm_values)

    if surface_rpm_present and motor_rpm_present:
        # If both Surface RPM and Motor RPM are present, this might be Bit RPM
        return "BIT_RPM (rpm)"
    elif surface_rpm_present:
        # If only Surface RPM is present, it's more likely to be Surface RPM
        return "SURFACE_RPM (rpm)"
    elif motor_rpm_present:
        # If only Motor RPM is present, it's more likely to be Motor RPM
        return "MOTOR_RPM (rpm)"
    else:
        # Fallback assumption if no specific context is available
        # Mark as unidentified if no specific context matches
        return "RPM__unidentified (rpm)"


# def standardize_mnemonics(df):
#     """
#     Apply mnemonic standardization to all column headers in the DataFrame.
#     """
#     # Extract average RPM values for context analysis
#     rpm_values = {col: df[col].mean(
#     ) for col in df.columns if 'RPM' in col.split(' (')[0].upper()}

#     # Update the column headers based on the standardized mnemonics
#     new_columns = [map_mnemonic(col.split(' (')[0], col.split(
#         ' (')[1].rstrip(')'), rpm_values) for col in df.columns]

#     df.columns = new_columns
#     return df
def standardize_mnemonics(df):
    """
    Apply mnemonic standardization to all column headers in the DataFrame.
    """
    # Extract average RPM values for context analysis
    rpm_values = {col: df[col].mean(
    ) for col in df.columns if 'RPM' in col.split(' (')[0].upper()}

    # Update the column headers based on the standardized mnemonics
    new_columns = []
    for col in df.columns:
        mnemonic = col.split(' (')[0]
        unit = col.split(' (')[1].rstrip(')') if ' (' in col else ""
        unit = "" if "Unnamed" in unit else unit
        new_columns.append(map_mnemonic(mnemonic, unit, rpm_values))

    df.columns = new_columns
    return df
