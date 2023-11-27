#######################################
# Unit mapping

unit_patterns = {
    "ft": r"^(feet|foot|ft|f)$",
    "m": r"^(meters|meter|m)$",
    "in": r"^(inches|inch|in)$",
    "mm": r"^(millimeters|millimeter|mm)$",
    "klbs": r"^(klbs|kilopounds|kips)$",
    "tf": r"^(tonsforce|tf)$",
    "kN": r"^(kilonewton|kN)$",
    "lbf": r"^(poundsforce|lbf)$",
    "kgf": r"^(kilogramforce|kgf)$",
    "psi": r"^(psi|poundpersquareinch)$",
    "kPa": r"^(kilopascal|kPa)$",
    "MPa": r"^(megapascal|MPa)$",
    "bar": r"^(bar)$",
    "bbl": r"^(barrels|bbl)$",
    "L": r"^(liters|liter|L)$",
    "gal": r"^(gallons|gallon|gal)$",
    "m3": r"^(cubicmeters|cubicmeter|m3)$",
    "ft3": r"^(cubicfeet|cubicfoot|ft3)$",
    "gpm": r"^(gallonsperminute|gpm)$",
    "l/m": r"^(litersperminute|l/m|lpm)$",
    "l/s": r"^(literspersecond|l/s|lps)$",
    "m3/h": r"^(cubicmetersperhour|m3/h)$",
    "ft3/h": r"^(cubicfeetperhour|ft3/h)$",
    "ppg": r"^(poundspergallon|ppg)$",
    "sg": r"^(specificgravity|sg)$",
    "kg/m3": r"^(kilogramspercubicmeter|kg/m3)$",
    "C": r"^(celsius|c|centigrade|degC)$",
    "F": r"^(fahrenheit|f|degF)$",
    # Add more patterns as needed
}

#########################################
# Unit conversion


def safe_convert(value, conversion_func):
    """ Safely perform the conversion, handling non-numeric values. """
    try:
        # Convert to float if possible and apply the conversion function
        return conversion_func(float(value))
    except (ValueError, TypeError):
        # Return None or some default value if conversion isn't possible
        return None


def feet_to_meters(feet):
    """Convert feet to meters."""
    return safe_convert(feet, lambda x: x * 0.3048)


def tf_to_klbs(tf):
    """Convert tons-force to kilopounds."""
    return safe_convert(tf, lambda x: x * 2.20462)


def kN_to_klbs(kN):
    """Convert kilonewtons to kilopounds."""
    return safe_convert(kN, lambda x: x * 0.000225)


def ft_per_hour_to_m_per_hour(ft_per_hour):
    """Convert feet per hour to meters per hour."""
    return safe_convert(ft_per_hour, lambda x: x * 0.3048)


def knm_to_klbfft(knm):
    """Convert kilonewtons-meter to kilopounds-feet."""
    return safe_convert(knm, lambda x: x * 0.737562)


def kPa_to_psi(kPa):
    """Convert kilopascals to pounds per square inch."""
    return safe_convert(kPa, lambda x: x * 0.145038)


def MPa_to_psi(MPa):
    """Convert megapascals to pounds per square inch."""
    return safe_convert(MPa, lambda x: x * 145.038)


def bar_to_psi(bar):
    """Convert bar to pounds per square inch."""
    return safe_convert(bar, lambda x: x * 14.5038)


def bbl_to_gal(bbl):
    """Convert barrels to gallons."""
    return safe_convert(bbl, lambda x: x * 42)


def L_to_gal(L):
    """Convert liters to gallons."""
    return safe_convert(L, lambda x: x * 0.264172)


def m3_to_gal(m3):
    """Convert cubic meters to gallons."""
    return safe_convert(m3, lambda x: x * 264.172)


def m3_per_h_to_gpm(m3_per_h):
    """Convert cubic meters per hour to gallons per minute."""
    return safe_convert(m3_per_h, lambda x: x * 4.40287)


def ft3_per_h_to_gpm(ft3_per_h):
    """Convert cubic feet per hour to gallons per minute."""
    return safe_convert(ft3_per_h, lambda x: x * 0.124676)


def C_to_F(C):
    """Convert Celsius to Fahrenheit."""
    return safe_convert(C, lambda x: (x * 9/5) + 32)


def lpm_to_gpm(lpm):
    """Convert liters per minute to gallons per minute."""
    return safe_convert(lpm, lambda x: x * 0.264172)


def lps_to_gpm(lps):
    """Convert liters per second to gallons per minute."""
    return safe_convert(lps, lambda x: x * 60 * 0.264172)


def sg_to_ppg(sg):
    """Convert specific gravity to pounds per gallon."""
    return safe_convert(sg, lambda x: x * 8.345404)


# Define unit conversion mappings
unit_conversion_mappings = {
    'ft': {'conversion_function': feet_to_meters, 'new_unit': 'm'},
    'tf': {'conversion_function': tf_to_klbs, 'new_unit': 'klbs'},
    'kN': {'conversion_function': kN_to_klbs, 'new_unit': 'klbs'},
    'ft/h': {'conversion_function': ft_per_hour_to_m_per_hour, 'new_unit': 'm/h'},
    'kN.m': {'conversion_function': knm_to_klbfft, 'new_unit': 'kLbf.ft'},
    'kPa': {'conversion_function': kPa_to_psi, 'new_unit': 'psi'},
    'MPa': {'conversion_function': MPa_to_psi, 'new_unit': 'psi'},
    'bar': {'conversion_function': bar_to_psi, 'new_unit': 'psi'},
    'bbl': {'conversion_function': bbl_to_gal, 'new_unit': 'gal'},
    'L': {'conversion_function': L_to_gal, 'new_unit': 'gal'},
    'm3': {'conversion_function': m3_to_gal, 'new_unit': 'gal'},
    'm3/h': {'conversion_function': m3_per_h_to_gpm, 'new_unit': 'gpm'},
    'ft3/h': {'conversion_function': ft3_per_h_to_gpm, 'new_unit': 'gpm'},
    'C': {'conversion_function': C_to_F, 'new_unit': 'F'},
    'l/m': {'conversion_function': lpm_to_gpm, 'new_unit': 'gpm'},
    'l/s': {'conversion_function': lps_to_gpm, 'new_unit': 'gpm'},
    'sg': {'conversion_function': sg_to_ppg, 'new_unit': 'ppg'},
    # Add more unit mappings as needed
}
