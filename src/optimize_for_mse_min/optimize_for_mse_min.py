import numpy as np
from scipy.optimize import minimize
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
from tqdm import tqdm
import math

# from .optimize_config import bounds, BIT_DIAMETER
from config import config_constants
from utils import get_columns_by_mnemonics


# Function to compute MSE
def compute_mse(wob, rpm, torque, rop):
    wob_term = wob / ((config_constants["bit_diameter"]/2)**2 * math.pi)
    torque_term = 480 * torque * rpm / \
        (config_constants['bit_diameter']**2 * rop * 3.2808)

    return wob_term + torque_term


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
        # Convert the list of parameters to a dictionary
        params_dict = {key.lower(): value for key,
                       value in zip(X_mnemonics, params)}

        # Access the parameters by their names, converted to lower case
        wob = params_dict['wob']
        rpm = params_dict['rpm']
        torque = params_dict['torque']

        # Calculate 'Mu' if it's in X_mnemonics
        if 'mu' in params_dict:
            params_dict['mu'] = torque / \
                (wob * 2.2 * config_constants['bit_diameter'] / 36)

        # Use all parameters in X_mnemonics for prediction
        rop = trained_model.predict([list(params_dict.values())])[0]

        mse = compute_mse(wob, rpm, torque, rop)
        return mse

    results = []
    for _ in tqdm(range(iterations)):
        initial_guess = get_random_initial_guess(bounds, X_mnemonics)

        initial_guess_df = pd.DataFrame(
            [initial_guess], columns=get_columns_by_mnemonics(df_with_clusters, X_mnemonics))

        scaler.transform(initial_guess_df)

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
