from file_handle import load_file_standardize_header
import data_wrangle
import cluster
import ml_models
import optimize_for_mse_min

if __name__ == '__main__':

    file_path = r'c:/development/MSE_analysis/data/wanjing.csv'
    df = load_file_standardize_header(file_path)

    mnemonics_to_clean = ['DOC', 'BIT_RPM', 'ROP', 'TORQUE', 'WOB']
    df = data_wrangle.clean_df_by_mnemonics(df, mnemonics_to_clean)
    df = data_wrangle.add_columns(df)

    # mnemonics_to_remove_outliers = ['DOC', 'TORQUE']
    # df = data_wrangle.remove_outliers_by_mnemonics(
    #     df, mnemonics_to_remove_outliers)

    # print("##### Final df after cleaning and removing outliers #####")
    # print(df.head())
    # print(df.describe())

    # columns_for_clustering = ['DOC', 'TORQUE', 'WOB']
    # df = cluster.perform_kmeans(df, columns_for_clustering)

    # best_trained_models = ml_models.perform_optimization(df)

    # clusters = optimize_for_mse_min.execute_monte_carlo_optimization(df, 100)
    # df = optimize_for_mse_min.add_mse_min_to_original_data(df, clusters)

    # print("##### Final df after adding MSE min #####")
    # print(df.head())
    print(df.describe())
