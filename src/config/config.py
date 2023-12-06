import os
from utils import ensure_directory_exists

current_file_path = os.path.abspath(__file__)
root_directory = os.path.dirname(
    os.path.dirname(os.path.dirname(current_file_path)))

temp_directory = os.path.join(root_directory, "temp_folder")
projects_directory = os.path.join(root_directory, "projects")

each_project_folders = {
    'state_folder': 'state_folder',
    'raw_data_folder': 'raw_data_folder',
    'cleaned_data_folder': 'cleaned_data_folder',
    'output_folder': 'output_folder',
    'trained_models_folder': 'trained_models_folder'
}

config_constants = {
    'bit_diameter': 8.5
}


# app_system_folders = {
#     'state_folder': f"../app_system/state_folder",
#     'uploaded_folder': f"../app_system/uploaded_folder",
#     'output_folder': f"../app_system/output_folder",
#     'temp_folder': f"../app_system/temp_folder",
# }


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
    "VOLUME": None,
    # We'll set this dynamically in the get_volume_pattern function
    # ... rest of your patterns ...
    "cluster": r".*cluster.*"
}


def setup_temp_folder():
    for k, v in each_project_folders.items():
        ensure_directory_exists(os.path.join(temp_directory, v))
