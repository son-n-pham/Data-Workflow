<i>This repo is under-development</i>

# Data Processing, Visualizing, Modelling and Analysing Workflow

This project provides a comprehensive workflow for data processing, visualization, modeling, and analysis.

## Project Structure

- `src/`: Contains the main source code for the project.
  - `app.py`: The main application script.
  - `app_interface/`: Contains scripts for creating the application interface.
  - `cluster/`: Contains scripts for data clustering.
  - `config/`: Contains configuration scripts.
  - `data_wrangle/`: Contains scripts for data cleaning and preparation.
  - `feature_registry/`: Contains scripts and configurations for feature registry.
  - `file_handle/`: Contains scripts for file handling.
  - `manage_projects/`: Contains scripts for managing projects.
  - `ml_models/`: Contains scripts for machine learning models.
  - `optimize_for_mse_min/`: Contains scripts for optimization.
  - `optimize_parameters/`: Contains scripts for parameter optimization.
  - `plot/`: Contains scripts for data plotting.
  - `state/`: Contains scripts for managing application state.
  - `utils/`: Contains utility scripts.
- `temp_folder/`: Temporary folder for storing intermediate data.
- `projects/`: Contains individual project folders.
- `main.ipynb`: Jupyter notebook for the main application.
- `app.py`: Python script for the main application written with Streamlit.

## Getting Started

Streamlit is used as the GUI for the app.

To run the main application, use the following command:

```bash
streamlit run src/app.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
