import pandas as pd
import re
from . import units_config


def map_unit(unit):
    """
    Standardize unit representations to a consistent set using regex.
    """
    unit_patterns = units_config.unit_patterns

    # Check each pattern and return the standardized unit
    for std_unit, pattern in unit_patterns.items():
        if re.match(pattern, unit, re.IGNORECASE):
            return std_unit

    # Return the original unit if no pattern matches
    return unit


def standardize_units(df, unit_conversion_mappings):
    """
    Standardize units in the DataFrame.
    Map units to a standard representation and apply conversion functions based on the unit of each column.
    Apply conversion functions based on the unit of each column.
    """
    # Convert keys in unit_conversion_mappings to lowercase
    unit_conversion_mappings = {
        k.lower(): v for k, v in unit_conversion_mappings.items()}

    for col in df.columns:
        mnemonic, unit = col.split(' (')
        unit = unit.rstrip(')')

        # Map the unit to a standard representation
        unit = map_unit(unit.lower()).lower()

        if unit in unit_conversion_mappings:
            conversion_function = unit_conversion_mappings[unit]['conversion_function']
            new_unit = unit_conversion_mappings[unit]['new_unit']
            df[col] = df[col].apply(conversion_function)
            df.rename(columns={col: f"{mnemonic} ({new_unit})"}, inplace=True)

    return df
