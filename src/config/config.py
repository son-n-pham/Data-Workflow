config_constants = {
    'bit_diameter': 8.5
}

header_patterns = {
    "MD": r".*DEPMD.*|.*DEPTH.*|.*MD.*",
    "TVD": r".*TVD.*",
    "ROP": r".*ROP.*|.*PENETRATE.*",
    "DOC": r".*DOC.*",
    "WOB": r".*WOB.*|.*BITLOAD.*",
    "MSE": r".*MSE.*|SE.*",
    "SURFACE_RPM": r".*SURF.*RPM.*|.*SURFACE.*RPM.*",
    "MOTOR_RPM": r".*MOTOR.*RPM.*",
    "BIT_RPM": r".*BIT.*RPM.*|.*TOTAL.*RPM.*|.*RPM.*TOTAL|.*RPM.*BIT.*|.*RPM.*",
    "SPP": r".*SPP.*|.*STANDPIPE.*",
    "TORQUE": r".*TORQ.*|.*TWIST.*|TQ_Table.*",
    "FLOW": r".*FLOW.*|.*FLUIDRATE.*",
    "TEMP": r".*TEMP.*|.*HEAT.*",
    "PRESSURE": r".*PRESS.*|.*PSI.*",
    "Si": r".*Si.*",
    "Shale": r".*Shale.*",
    "Dolomite": r".*Dolomite.*",
    "Limestone": r".*Limestone.*",
    "BIT_DIAMETER": r"BIT_DIAMETER",
    "Mu": r".*Mu.*",
    "VOLUME": None,  # We'll set this dynamically in the get_volume_pattern function
    # ... rest of your patterns ...
}
