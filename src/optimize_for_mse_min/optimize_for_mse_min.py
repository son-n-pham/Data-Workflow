from scipy.optimize import Bounds
import numpy as np
from scipy.optimize import minimize
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
from tqdm import tqdm

# from .optimize_config import bounds, BIT_DIAMETER
from config import config_constants
from utils import get_columns_by_mnemonics, compute_mu, compute_mse

import warnings
# Disable the specific warning
warnings.filterwarnings(
    "ignore", message="X does not have valid feature names, but StandardScaler was fitted with feature names")

# Suppress only the RuntimeWarning from scipy.optimize
warnings.filterwarnings(
    "ignore", message="Values in x were outside bounds during a minimize step, clipping to bounds", category=RuntimeWarning)


def get_random_initial_guess(bounds, X_mnemonics):
    initial_guess = []
    lithologies = ['si', 'shale', 'dolomite', 'limestone']
    for mnemonic in X_mnemonics:
        # IMPORTANT to control the lower bound of WOB and Torque
        # Ensure lower bound is never 0 by using max(0.0001, lower_bound)
        low_bound = max(bounds[mnemonic][0], 1)
        high_bound = bounds[mnemonic][1]
        # Generate a random value
        initial_guess.append(np.random.uniform(low_bound, high_bound))

    # Normalize the lithologies to sum to 100
    lithology_indices = [i for i, m in enumerate(
        X_mnemonics) if m.lower() in lithologies]
    lithology_sum = sum(initial_guess[i] for i in lithology_indices)
    for i in lithology_indices:
        initial_guess[i] *= 100 / lithology_sum

    return np.array(initial_guess)


def minimize_objective_function(objective_function, initial_guess, bounds, X_mnemonics):
    bounds_sequence = [bounds[mnemonic] for mnemonic in X_mnemonics]

    # Indices for WOB, Torque, and Mu
    wob_index = X_mnemonics.index('WOB')
    torque_index = X_mnemonics.index('TORQUE')

    constraints = [
        # Increase WOB constraint
        {'type': 'ineq', 'fun': lambda x: x[wob_index] - 15},
        # Existing Torque constraint
        {'type': 'ineq', 'fun': lambda x: x[torque_index] - 5},
        # Adjust Mu constraint
        {'type': 'ineq', 'fun': lambda x: 1000 - \
            compute_mu(x[wob_index], x[torque_index], config_constants['bit_diameter'])}
    ]

    return minimize(
        objective_function,
        initial_guess,
        method='SLSQP',  # A method that supports constraints
        bounds=Bounds([b[0] for b in bounds_sequence], [b[1]
                      for b in bounds_sequence]),
        constraints=constraints)


def monte_carlo_optimization(df_with_clusters, scaler, trained_model, X_mnemonics, bounds, iterations):
    def objective_function(params):
        wob_index = [i for i, m in enumerate(
            X_mnemonics) if m.lower() == 'wob'][0]
        rpm_index = [i for i, m in enumerate(
            X_mnemonics) if m.lower() == 'rpm'][0]
        torque_index = [i for i, m in enumerate(
            X_mnemonics) if m.lower() == 'torque'][0]
        mu_index = [i for i, m in enumerate(
            X_mnemonics) if m.lower() == 'mu'][0]

        params[mu_index] = compute_mu(
            params[wob_index],
            params[torque_index],
            config_constants['bit_diameter'])

        params_reshaped = np.array(params).reshape(1, -1)

        X_scaled = scaler.transform(params_reshaped)

        # Use all parameters in X_mnemonics for prediction
        rop = trained_model.predict(X_scaled)[0]

        mse = compute_mse(params[wob_index],
                          params[rpm_index], params[torque_index], rop,
                          config_constants['bit_diameter'])

        # IMPORTANT: Another constraint is implemented to avoid unphysically low WOB, Torque and Mu values
        penalty = 0
        if params[wob_index] < 10:
            penalty += 1000000
        if params[torque_index] < 5:
            penalty += 1000000
        if params[mu_index] > 1000:
            penalty += 1000000

        return mse + penalty
        # return mse

    results = []
    for _ in tqdm(range(iterations)):
        initial_guess = get_random_initial_guess(bounds, X_mnemonics)

        # Use the function before calling minimize_objective_function
        result = minimize_objective_function(
            objective_function, initial_guess, bounds, X_mnemonics)
        results.append((result.x, result.fun))

    optimized_params = np.array([res[0] for res in results])
    mse_values = np.array([res[1] for res in results])

    low_mse_threshold = np.percentile(mse_values, 10)
    low_mse_indices = mse_values <= low_mse_threshold
    low_mse_params = optimized_params[low_mse_indices]

    return low_mse_params, mse_values[low_mse_indices]


def get_param_ranges(low_mse_params, X_mnemonics):
    param_ranges = {}
    for i, mnemonic in enumerate(X_mnemonics):
        param_ranges[mnemonic] = (
            low_mse_params[:, i].min(), low_mse_params[:, i].max())
    return param_ranges


def print_results(cluster, params_data, mse_values, X_mnemonics,
                  progress_callback=print):
    progress_callback(f'Cluster: {cluster}')
    progress_callback(f'Parameter Ranges for Low MSE:')

    for mnemonic in X_mnemonics:
        param_values = params_data[mnemonic]
        median = param_values.median()
        Q1 = param_values.quantile(0.25)
        Q3 = param_values.quantile(0.75)
        IQR = Q3 - Q1

        progress_callback(
            f'{mnemonic}: Median = {median:.2f}, IQR = {IQR:.2f}')

    # Calculating and printing MSE information including min, max, median, and IQR
    mse_min = mse_values.min()
    mse_max = mse_values.max()
    mse_median = mse_values.median()
    mse_Q1 = mse_values.quantile(0.25)
    mse_Q3 = mse_values.quantile(0.75)
    mse_IQR = mse_Q3 - mse_Q1
    progress_callback(
        f'MSE: Min = {mse_min:.2f}, Max = {mse_max:.2f}, Median = {mse_median:.2f}, IQR = {mse_IQR:.2f}\n')


def get_bounds_for_cluster(original_data_with_clusters, X_mnemonics, cluster, expanding_factor=10000):
    """Generate bounds for the parameters based on the data in the cluster
    Except lithology, others have max value * 10000 to allow the simulation
    to explore the wide range of data"""
    bounds = {}
    for mnemonic in X_mnemonics:
        # Convert mnemonic to column header
        column_header = get_columns_by_mnemonics(
            original_data_with_clusters, [mnemonic])[0]
        data_for_cluster = original_data_with_clusters[original_data_with_clusters['cluster']
                                                       == cluster][column_header]
        bounds[mnemonic] = (data_for_cluster.min(), data_for_cluster.max(
        ) * (expanding_factor if mnemonic not in ['Si', 'Shale', 'Dolomite', 'Limestone'] else 1))
    return bounds


def execute_monte_carlo_optimization(df_with_clusters, scalers_best_models, X_mnemonics, iterations, progress_callback=print):
    """
    Executes Monte Carlo optimization for each unique cluster in the given DataFrame.

    Parameters:
    df_with_clusters (pandas.DataFrame): DataFrame containing the data with cluster information.
    scalers_best_models (dict): Dictionary containing the best models and scalers for each cluster.
    X_mnemonics (list): List of feature names used in the model.
    iterations (int): Number of iterations to perform in the Monte Carlo optimization.
    progress_callback (function): Function to call with progress information. Defaults to print.

    Returns:
    dict: A dictionary where each key is a cluster and the value is a dictionary containing the parameter ranges,
        low mean squared errors (MSEs), scaler, and model for that cluster.
    """

    clusters = {}
    for cluster in df_with_clusters['cluster'].unique():
        bounds = get_bounds_for_cluster(
            df_with_clusters, X_mnemonics, cluster)

        progress_callback(f"#### Seeking MSE min for cluster {cluster} #####")

        scaler = scalers_best_models[cluster]['scaler']
        trained_model = scalers_best_models[cluster]['model']

        low_mse_params, low_mses = monte_carlo_optimization(df_with_clusters,
                                                            scaler, trained_model, X_mnemonics, bounds, iterations)
        param_ranges = get_param_ranges(low_mse_params, X_mnemonics)
        # Create a DataFrame from the low_mse_params for easier computation of median and IQR
        df_low_mse_params = pd.DataFrame(low_mse_params, columns=X_mnemonics)
        print_results(cluster, df_low_mse_params,
                      pd.Series(low_mses), X_mnemonics, progress_callback)
        clusters[int(cluster)] = {
            'param_ranges': param_ranges,
            'low_mses': low_mses,
            'scaler': scaler,
            'model': trained_model
        }
    return clusters


def add_mse_min_to_original_data(df_with_clusters, clusters):
    df_with_clusters['MSE_min (ksi)'] = df_with_clusters['cluster'].map(
        lambda x: clusters[int(x)]['low_mses'].min())
    return df_with_clusters
