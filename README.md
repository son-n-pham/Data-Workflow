# Data Workflow Application

This application provides a workflow for loading, cleaning, analyzing, and visualizing drilling data using Streamlit. It allows users to upload data files, perform various data wrangling tasks, apply machine learning models, optimize parameters, and visualize results through interactive plots.

## Features

*   **File Handling:** Supports loading data from CSV, Excel (.xlsx, .xls), and text (.txt) files. Handles multi-level headers and specific NaN values (-999.25, -999).
*   **Data Cleaning:** Removes rows with all zero values, handles non-numeric entries, replaces negative/zero values with NaN, and drops rows with missing values in specified columns.
*   **Outlier Removal:** Identifies and removes outliers based on the Interquartile Range (IQR) method.
*   **Feature Engineering:** Adds calculated columns relevant to drilling analysis (e.g., Mechanical Specific Energy - MSE).
*   **Data Visualization:** Generates interactive 2D and 3D scatter plots using Plotly.
*   **Machine Learning:**
    *   Clustering: Applies clustering algorithms to identify patterns.
    *   Modelling: Builds predictive models.
    *   Prediction: Predicts MSE minimum values.
*   **Parameter Optimization:** Optimizes drilling parameters based on defined criteria.
*   **Project Management:** Allows saving and loading analysis sessions/projects.
*   **Interactive UI:** Built with Streamlit for easy interaction and workflow management.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd Data-Workflow
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt 
    # (Note: You might need to create a requirements.txt file first if it doesn't exist)
    # pip freeze > requirements.txt 
    ```

## Usage

To run the Streamlit application:

```bash
streamlit run src/app.py
```

Navigate to the URL provided by Streamlit (usually `http://localhost:8501`) in your web browser.

1.  Use the sidebar to upload your data file.
2.  Select the desired features/analyses (e.g., Clean Data, Plot Data, Cluster, Optimize).
3.  Configure the parameters for each selected feature in the main panel.
4.  View the results, including cleaned data, plots, and model outputs.
5.  Optionally, save the current project state for later use.

## Project Structure

```
Data-Workflow/
├── .gitignore              # Git ignore configuration
├── LICENSE                 # Project License (MIT)
├── README.md               # This file
├── data/                   # Sample/raw data files (e.g., *.csv, *.WCL)
├── projects/               # Saved project states
│   └── README.md
├── requirements.txt        # Python dependencies (ensure this is created/updated)
├── src/                    # Source code
│   ├── __init__.py
│   ├── app.py              # Main Streamlit application entry point
│   ├── main.py             # Potential alternative entry point
│   ├── main.ipynb          # Development notebook
│   ├── app_interface/      # UI modules (e.g., sidebar)
│   │   ├── __init__.py
│   │   └── create_sidebar.py
│   ├── config/             # Configuration files
│   │   ├── __init__.py
│   │   └── config.py       # Paths, constants, header patterns
│   ├── data_wrangle/       # Data cleaning and preparation
│   │   ├── __init__.py
│   │   ├── add_columns.py
│   │   ├── clean_df.py
│   │   └── prepare_plot_data.py
│   ├── feature_registry/   # Feature definitions and management
│   │   ├── __init__.py
│   │   ├── clustering_feature.py
│   │   ├── feature_registry.py
│   │   ├── features.py     # Base Feature class
│   │   ├── graph_feature.py
│   │   ├── modelling_feature.py
│   │   ├── optimizing_parameters_feature.py
│   │   └── predicting_mse_min_feature.py
│   ├── file_handle/        # File loading, saving, header merging
│   │   ├── __init__.py
│   │   ├── headers.py      # Header handling
│   │   ├── load_file.py    # File loading with NaN handling
│   │   ├── save_file.py    # File saving
│   │   ├── file_handling.py # General file operations
│   │   ├── standardize_single_dataset.py # Dataset standardization
│   │   ├── headers_config.py # Header configuration
│   │   ├── units.py        # Unit handling
│   │   └── units_config.py # Unit configuration
│   ├── ml_models/          # Machine learning model implementations
│   │   ├── __init__.py
│   │   └── ml_models.py
│   ├── optimize_for_mse_min/ # MSE minimization logic
│   │   ├── __init__.py
│   │   ├── optimize_config.py
│   │   ├── optimize_for_mse_min.py
│   │   ├── optimize_for_mse_min_multi_start.py
│   │   └── README.md
│   ├── optimize_parameters/ # Parameter optimization logic
│   │   ├── __init__.py
│   │   └── optimize_parameters.py
│   ├── plot/               # Plotting functions (Plotly)
│   │   ├── __init__.py
│   │   ├── plot.py         # Plotting wrapper/interface
│   │   ├── plot_2d_scatter.py
│   │   └── plot_3d_scatter.py
│   ├── state/              # Application state management
│   │   ├── __init__.py
│   │   └── state.py
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── df_utils.py     # DataFrame utilities
│   │   ├── drilling_utils.py # Drilling calculations (MSE, etc.)
│   │   └── misc.py         # Miscellaneous utilities (file system, etc.)
│   ├── cluster/            # Clustering algorithms/scripts
│   │   ├── __init__.py
│   │   └── cluster.py
│   └── manage_projects/    # Project loading/saving logic
│       ├── __init__.py
│       └── manage_projects.py
└── temp_folder/            # Temporary file storage
    ├── cleaned_data_folder/
    └── raw_data_folder/
```

## Key Modules

*   **`src/app.py`**: Orchestrates the application flow and UI.
*   **`src/file_handle/load_file.py`**: Handles loading and initial processing of various file types, including treating -999.25 and -999 as NaN values.
*   **`src/data_wrangle`**: Contains core data cleaning, transformation, and outlier removal logic.
*   **`src/feature_registry`**: Defines the different analysis capabilities (plotting, clustering, modeling, optimization) as modular features.
*   **`src/plot`**: Provides functions for generating interactive visualizations.
*   **`src/config/config.py`**: Centralizes configuration settings like paths and constants.
*   **`src/utils`**: Offers helper functions used across different modules.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
