import numpy as np
import pandas as pd
from utils import get_columns_by_mnemonics
import config


def add_columns(df):

    if 'BIT_DIAMETER (in)' not in df.columns:
        df['BIT_DIAMETER (in)'] = config.config_constants['bit_diameter']

    def add_column_if_not_exists(mnemonics, new_column, calculation):
        columns = get_columns_by_mnemonics(df, mnemonics)
        if len(columns) == len(mnemonics) and not get_columns_by_mnemonics(df, [new_column]):
            columns_dict = dict(zip(mnemonics, columns))
            df[new_column] = calculation(df, columns_dict)

    add_column_if_not_exists(['ROP', 'BIT_RPM'], 'DOC (in/rev)',
                             lambda df, cols: df[cols['ROP']] * 39.3701 / 60 / df[cols['BIT_RPM']])

    add_column_if_not_exists(['WOB', 'TORQUE', 'BIT_DIAMETER'], 'Mu ()',
                             lambda df, cols: df[cols['TORQUE']] / (df[cols['WOB']] * df[cols['BIT_DIAMETER']] / 36))

    add_column_if_not_exists(['WOB', 'TORQUE', 'BIT_RPM', 'ROP', 'BIT_DIAMETER'], 'MSE (ksi)',
                             lambda df, cols: (df[cols['WOB']] / np.pi * (df[cols['BIT_DIAMETER']] / 2)**2) +
                             480 * df[cols['TORQUE']] * df[cols['BIT_RPM']] /
                             (df[cols['BIT_DIAMETER']]**2 * df[cols['ROP']]))

    return df
