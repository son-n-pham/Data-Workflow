import pandas as pd
import numpy as np

from tqdm import tqdm

from utils import compute_mu, compute_mse
from utils import get_columns_by_mnemonics
from config import config_constants

import warnings

# Disable the specific warning
warnings.filterwarnings(
    "ignore", message="X does not have valid feature names, but StandardScaler was fitted with feature names")


def sample_rock_components(cluster_df, mnemonics):
    """
    Samples rock components uniformly within their min-max range in the cluster.

    Parameters:
    cluster_df (DataFrame): DataFrame of a specific cluster.
    mnemonics (list): List of mnemonics to sample.

    Returns:
    dict: A dictionary of sampled values normalized to sum up to 1.
    """
    components = {}
    for mnemonic in mnemonics:
        col_name = get_columns_by_mnemonics(cluster_df, mnemonic)[0]
        components[mnemonic] = np.random.uniform(
            cluster_df[col_name].min(), cluster_df[col_name].max())
    total = sum(components.values())
    return {k: v*100 / total for k, v in components.items()}


def monte_carlo_optimization(df, X_mnemonics, scalers_best_models, bounds, mse_tolerance=None, iterations=100):
    """
    Perform Monte Carlo optimization over different clusters in the dataset.

    Parameters:
    df (DataFrame): The dataset containing the clusters and other information.
    X_mnemonics (list): List of mnemonics to be used in the optimization.
    scalers_best_models (dict): Dictionary of scalers and models for each cluster.
    bounds (dict): Dictionary of bounds for different parameters.
    mse_tolerance (float): Tolerance level for MSE.
    iterations (int): Number of iterations per cluster.

    Returns:
    DataFrame: A DataFrame containing the results of the optimization.
    """
    result_df_columns = get_columns_by_mnemonics(
        df, X_mnemonics) + ['ROP (m/h)', 'MSE (ksi)', 'MSE_min (ksi)', 'cluster']
    results = []

    for cluster in df['cluster'].unique():
        cluster_df = df[df['cluster'] == cluster]
        for _ in tqdm(range(iterations), desc=f"Cluster {cluster}"):
            # Sample parameters
            params = {param: np.random.uniform(
                *bounds[param]) for param in bounds}
            params['mu'] = compute_mu(
                params['wob'], params['torque'], config_constants['bit_diameter'])

            # Sample and normalize rock components
            rock_mnemonics = ['si', 'dolomite', 'limestone', 'shale']
            rock_components = sample_rock_components(
                cluster_df, rock_mnemonics)
            params.update(rock_components)
            params['cluster'] = cluster

            # Create input feature vector
            X = [params.get(mnemonic.lower(), None)
                 for mnemonic in X_mnemonics]
            if None in X:
                print(
                    "Not enough data to predict ROP, check if all mnemonics are present")
                break

            X = np.array(X).reshape(1, -1)
            X_scaled = scalers_best_models[cluster]['scaler'].transform(X)
            rop = scalers_best_models[cluster]['model'].predict(X_scaled)[0]
            params['rop'] = rop

            # Calculate MSE and MSE_min
            params['mse'] = compute_mse(
                params['wob'], params['rpm'], params['torque'], rop, config_constants['bit_diameter'])
            params['mse_min'] = cluster_df['MSE_min (ksi)'].min()

            if params['mse'] <= params['mse_min'] * (1 + mse_tolerance):
                params = {get_columns_by_mnemonics(
                    df, k)[0]: v for k, v in params.items()}
                results.append({column: params.get(column, None)
                                for column in result_df_columns})

    return pd.DataFrame(results, columns=result_df_columns)
