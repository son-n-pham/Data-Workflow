from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.svm import SVR
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler

from utils import get_columns_by_mnemonics


def evaluate_models(models_list, X, y, kfold):
    best_mse = float('inf')
    best_model = None

    for model_name, model in models_list:
        model.fit(X, y)
        cv_scores = -cross_val_score(model, X, y,
                                     cv=kfold, scoring='neg_mean_squared_error')
        print(f"Cross-validation MSE scores for {model_name}: {cv_scores}")
        avg_mse = cv_scores.mean()
        print(f"Average MSE for {model_name}: {avg_mse}\n")

        if avg_mse < best_mse:
            best_mse = avg_mse
            best_model = model

    return best_model, best_mse


def perform_optimization(dataframe, X_mnemonics=['WOB', 'BIT_RPM', 'TORQUE', 'Mu'], y_mnemonic='ROP', k=7):
    """
    Performs optimization on a given dataframe using various machine learning models.

    This function takes a dataframe and a list of mnemonics for the features (X) and the target (y).
    It performs k-fold cross-validation on various machine learning models for each unique cluster in the dataframe.
    The best model (with the lowest mean squared error) is selected for each cluster. Additionally, it returns the 
    StandardScaler instances used for each cluster.

    Parameters:
    dataframe (pandas.DataFrame): The dataframe to perform optimization on.
    X_mnemonics (list of str): The mnemonics for the features. Default is ['WOB', 'BIT_RPM', 'TORQUE', 'Mu'].
    y_mnemonic (str): The mnemonic for the target. Default is 'ROP'.
    k (int): The number of folds for k-fold cross-validation. Default is 7.

    Returns:
    dict: A dictionary where the keys are the unique clusters and the values are another dictionary containing 
    'scaler' and 'model' keys. The 'scaler' key corresponds to the StandardScaler instance used for the cluster and 
    the 'model' key corresponds to the best model for the cluster.
    """

    # If y_mnemonic is a string, convert it to a list
    if isinstance(y_mnemonic, str):
        y_mnemonic = [y_mnemonic]

    print("##### X_mnemonics #####")
    print(X_mnemonics)

    X_cols = get_columns_by_mnemonics(dataframe, X_mnemonics)
    print("##### X_cols #####")
    print(X_cols)

    y_col = get_columns_by_mnemonics(dataframe, y_mnemonic)[0]

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
        print(f"Evaluating cluster {cluster}")
        cluster_data = dataframe[dataframe['cluster'] == cluster]

        print(
            f" ####### X shape is: {len(cluster_data[X_cols].columns)} #########")
        print(
            f" ####### X columns are: {cluster_data[X_cols].columns} #########")

        scaler = StandardScaler()  # Create a new scaler for this cluster
        X = scaler.fit_transform(cluster_data[X_cols])  # Scale the data

        y = cluster_data[y_col]

        best_model, best_mse = evaluate_models(models_list, X, y, kfold)

        # Store the scaler and model for this cluster
        scalers_best_models[cluster] = {'scaler': scaler, 'model': best_model}

    return scalers_best_models
