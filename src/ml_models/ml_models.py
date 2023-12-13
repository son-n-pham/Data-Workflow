from typing import List, Tuple, Callable, Union
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import numpy as np
import pandas as pd

from utils import get_columns_by_mnemonics


def evaluate_models(model_list: List[Tuple[str, BaseEstimator]], features: np.ndarray, targets: np.ndarray, cross_validator: KFold, progress_callback: Callable[[str], None] = print) -> Tuple[BaseEstimator, float]:
    """
    Evaluate a list of models using cross-validation and return the best model and its mean squared error.

    Parameters:
    model_list (List[Tuple[str, BaseEstimator]]): A list of tuples, where each tuple contains a model name and a model instance.
    features (np.ndarray): The input data for the models.
    targets (np.ndarray): The target data for the models.
    cross_validator (KFold): The cross-validation splitting strategy.
    progress_callback (Callable[[str], None]): A callback function for reporting progress. The function should accept a string argument. Defaults to print.

    Returns:
    Tuple[BaseEstimator, float]: The best model and its mean squared error.
    """
    best_mean_squared_error = float('inf')
    best_model = None

    for model_name, model in model_list:
        model.fit(features, targets)
        cross_val_scores = - \
            cross_val_score(model, features, targets,
                            cv=cross_validator, scoring='neg_mean_squared_error')

        progress_callback(
            f"Cross-validation MSE scores for {model_name}: {cross_val_scores}")

        mean_squared_error = cross_val_scores.mean()

        progress_callback(
            f"Average MSE for {model_name}: {mean_squared_error}\n")

        if mean_squared_error < best_mean_squared_error:
            best_mean_squared_error = mean_squared_error
            best_model = model

    return best_model, best_mean_squared_error


def perform_optimization(dataframe: pd.DataFrame, X_mnemonics: List[str] = ['WOB', 'BIT_RPM', 'TORQUE', 'Mu'], y_mnemonic: Union[str, List[str]] = 'ROP', k: int = 7, progress_callback: Callable[[str], None] = print) -> dict:
    """
    Performs optimization on a given dataframe using various machine learning models.

    This function takes a dataframe and a list of mnemonics for the features (X) and the target (y).
    It performs k-fold cross-validation on various machine learning models for each unique cluster in the dataframe.
    The best model (with the lowest mean squared error) is selected for each cluster. Additionally, it returns the 
    StandardScaler instances used for each cluster.

    Parameters:
    dataframe (pandas.DataFrame): The dataframe to perform optimization on.
    X_mnemonics (list of str): The mnemonics for the features. Default is ['WOB', 'BIT_RPM', 'TORQUE', 'Mu'].
    y_mnemonic (str or list of str): The mnemonic for the target. Default is 'ROP'.
    k (int): The number of folds for k-fold cross-validation. Default is 7.
    progress_callback (Callable[[str], None]): A callback function for reporting progress. The function should accept a string argument. Defaults to print.

    Returns:
    dict: A dictionary where the keys are the unique clusters and the values are another dictionary containing 
    'scaler' and 'model' keys. The 'scaler' key corresponds to the StandardScaler instance used for the cluster and 
    the 'model' key corresponds to the best model for the cluster.
    """
    # If y_mnemonic is a string, convert it to a list
    if isinstance(y_mnemonic, str):
        y_mnemonic = [y_mnemonic]

    progress_callback("##### X_mnemonics #####")
    progress_callback(X_mnemonics)

    X_cols = get_columns_by_mnemonics(dataframe, X_mnemonics)
    progress_callback("##### X_cols #####")
    progress_callback(X_cols)

    y_col = get_columns_by_mnemonics(dataframe, y_mnemonic)[0]

    # Rename column with name of 'cluster ()' to 'cluster'
    if 'cluster ()' in dataframe.columns:
        dataframe.rename(columns={'cluster ()': 'cluster'}, inplace=True)

    clusters = dataframe['cluster'].unique()
    scalers_best_models = {}

    kfold = KFold(n_splits=k, shuffle=True, random_state=1)

    models_list = [
        ('rf', RandomForestRegressor(n_estimators=100)),
        ('xgb', XGBRegressor()),
        ('svr', SVR()),
        ('gbm', GradientBoostingRegressor()),
        ('lgbm', LGBMRegressor(verbose=-1)),  # Turn off LightGBM warnings
        ('catboost', CatBoostRegressor(silent=True)),
    ]

    for cluster in clusters:
        progress_callback(f"Evaluating cluster {cluster}")
        cluster_data = dataframe[dataframe['cluster'] == cluster]

        progress_callback(
            f" ####### X shape is: {len(cluster_data[X_cols].columns)} #########")
        progress_callback(
            f" ####### X columns are: {cluster_data[X_cols].columns} #########")

        scaler = StandardScaler()  # Create a new scaler for this cluster
        X = scaler.fit_transform(cluster_data[X_cols])  # Scale the data

        y = cluster_data[y_col]

        best_model, best_mse = evaluate_models(
            models_list, X, y, kfold, progress_callback)

        # Store the scaler and model for this cluster
        scalers_best_models[cluster] = {'scaler': scaler, 'model': best_model}

    return scalers_best_models
