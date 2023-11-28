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


def get_random_initial_guess(bounds, X_mnemonics):
    initial_guess = []
    lithologies = ['si', 'shale', 'dolomite', 'limestone']
    for mnemonic in X_mnemonics:
        # Generate a random value
        initial_guess.append(np.random.uniform(
            bounds[mnemonic][0], bounds[mnemonic][1]))

    # Normalize the lithologies to sum to 100
    lithology_indices = [i for i, m in enumerate(
        X_mnemonics) if m.lower() in lithologies]
    lithology_sum = sum(initial_guess[i] for i in lithology_indices)
    for i in lithology_indices:
        initial_guess[i] *= 100 / lithology_sum

    return np.array(initial_guess)


def minimize_objective_function(objective_function, initial_guess, bounds, X_mnemonics):
    bounds_sequence = [bounds[mnemonic] for mnemonic in X_mnemonics]
    return minimize(
        objective_function,
        initial_guess,
        method='L-BFGS-B',
        bounds=bounds_sequence)


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
        return mse

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


# Other functions (print_results, execute_monte_carlo_optimization, add_mse_min_to_original_data) remain the same.
def print_results(cluster, param_ranges, low_mses):
    print(f'Cluster: {cluster}')
    print(f'Parameter Ranges for Low MSE:')
    for param, (low, high) in param_ranges.items():
        print(f'{param}: {low:.2f} to {high:.2f}')
    print(
        f'Corresponding MSE Range: {low_mses.min():.2f} to {low_mses.max():.2f}')
    print()


def get_bounds_for_cluster(original_data_with_clusters, X_mnemonics, cluster):
    """Generate bounds for the parameters based on the data in the cluster
    Except lithology, others have max value * 100 to allow the simulation
    to explore the wide range of data"""
    bounds = {}
    for mnemonic in X_mnemonics:
        # Convert mnemonic to column header
        column_header = get_columns_by_mnemonics(
            original_data_with_clusters, [mnemonic])[0]
        data_for_cluster = original_data_with_clusters[original_data_with_clusters['cluster']
                                                       == cluster][column_header]
        bounds[mnemonic] = (data_for_cluster.min(), data_for_cluster.max(
        ) * (100 if mnemonic not in ['Si', 'Shale', 'Dolomite', 'Limestone'] else 1))
    return bounds


def execute_monte_carlo_optimization(df_with_clusters, scalers_best_models, X_mnemonics, iterations):

    clusters = {}
    for cluster in df_with_clusters['cluster'].unique():
        bounds = get_bounds_for_cluster(
            df_with_clusters, X_mnemonics, cluster)

        print(f"#### Seeking MSE min for cluster {cluster} #####")

        scaler = scalers_best_models[cluster]['scaler']
        trained_model = scalers_best_models[cluster]['model']

        low_mse_params, low_mses = monte_carlo_optimization(df_with_clusters,
                                                            scaler, trained_model, X_mnemonics, bounds, iterations)
        param_ranges = get_param_ranges(low_mse_params, X_mnemonics)
        print_results(cluster, param_ranges, low_mses)
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
