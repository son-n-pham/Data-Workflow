import streamlit as st
import pandas as pd
from .features import Feature
from optimize_for_mse_min import execute_monte_carlo_optimization, add_mse_min_to_original_data
from file_handle import save_clustered_df_to_file_and_update_session_state, load_file_standardize_header


class PredictingMSEMinFeature(Feature):
    """
    A class used to represent the PredictingMSEMinFeature.

    ...

    Attributes
    ----------
    name : str  
        the name of the feature
    parameters : dict
        a dictionary of parameters for the feature

    Methods
    -------
    execute(df_with_clusters, scalers_best_models, feature_session_state, X_mnemonics):
        Executes the feature on the given DataFrame.
    dict_to_table(clusters_dict):
        Converts a dictionary of clusters to a DataFrame.
    print_results(feature_session_state, df_with_clusters_mse_min):
        Prints the results of the feature execution.
    set_feature_parameters(feature_session_state):
        Sets the parameters for the feature.
    to_dict():
        Converts the feature to a dictionary.
    from_dict(data):
        Creates a new PredictingMSEMinFeature object from a dictionary.
    """

    def __init__(self, name: str, parameters: dict = None):
        super().__init__(name, "Predicting MSE min",
                         "Predicting MSE min for each cluster", parameters)
        self.parameters = parameters or {}

    def execute(self, df_with_clusters, scalers_best_models,
                feature_session_state,
                X_mnemonics=['TORQUE', 'WOB', 'RPM', 'Mu',
                             'Si', 'Dolomite', 'Limestone', 'Shale']):
        """
        Executes the feature on the given DataFrame.

        Parameters
        ----------
        df_with_clusters : DataFrame
            the DataFrame to execute the feature on
        scalers_best_models : dict
            a dictionary of scalers and best models
        feature_session_state : SessionState
            the session state
        X_mnemonics : list, optional
            a list of mnemonics (default is ['TORQUE', 'WOB', 'RPM', 'Mu', 'Si', 'Dolomite', 'Limestone', 'Shale'])

        Returns
        -------
        DataFrame
            the DataFrame with the feature executed
        """

        iterations, predicting_mse_button = self.set_feature_parameters(
            feature_session_state)
        df_with_clusters_mse_min = None

        if predicting_mse_button:

            # TODO: Fix header and unit when loading file
            # Remove 'cluster' string in the keys of scalers_best_models
            # Temporary fix before re-do on the header and unit
            scalers_best_models = {
                int(k.split("cluster")[-1]): v for k, v in scalers_best_models.items()}
            # Rename column 'cluster ()' to 'cluster' in df_with clusters
            # Temporary fix before re-do on the header and unit
            if 'cluster ()' in df_with_clusters.columns:
                df_with_clusters.rename(
                    columns={'cluster ()': 'cluster'}, inplace=True)

            with st.spinner("Predicting MSE min for each cluster..."):
                with st.expander("Show details"):
                    clusters = execute_monte_carlo_optimization(
                        df_with_clusters=df_with_clusters,
                        scalers_best_models=scalers_best_models,
                        X_mnemonics=X_mnemonics, iterations=iterations,
                        progress_callback=st.write)

                    df_with_clusters_mse_min = add_mse_min_to_original_data(
                        df_with_clusters, clusters)

                    # Rename column 'cluster' back to 'cluster ()'
                    # Temporary fix before re-do on the header and unit
                    df_with_clusters_mse_min.rename(
                        columns={'cluster': 'cluster ()'}, inplace=True)

                    df_with_clusters_mse_min = save_clustered_df_to_file_and_update_session_state(
                        df_with_clusters_mse_min)

                    # TODO
                    # Modify keys of cluster from <integer> to "cluster<integer>'
                    clusters = {
                        f'cluster{cluster_id}': cluster_info for cluster_id, cluster_info in clusters.items()}

                    # Write iterations, clusters to feature_session_state.parameters
                    feature_session_state.parameters['iterations'] = iterations
                    # feature_session_state.parameters['clusters'] = clusters

            feature_session_state.activated = True

        if feature_session_state.activated:
            df_with_clusters_mse_min = load_file_standardize_header(
                st.session_state['loaded_file'])
            self.print_results(feature_session_state, df_with_clusters_mse_min)

        return df_with_clusters_mse_min

    def dict_to_table(self, clusters_dict):

        summary_list = []

        # Iterate through each cluster in the dictionary
        for cluster_id, cluster_info in clusters_dict.items():
            # Initialize the summary dictionary for the current cluster
            cluster_summary = {'cluster_id': cluster_id}

            # Extract min and max values for param_ranges
            for param, values in cluster_info['param_ranges'].items():
                cluster_summary[f"{param}_min"] = min(values)
                cluster_summary[f"{param}_max"] = max(values)

            # Extract min and max for low_mses
            cluster_summary['MSE_min'] = min(cluster_info['low_mses'])
            cluster_summary['MSE_max'] = max(cluster_info['low_mses'])

            # Get the model name
            cluster_summary['model_name'] = cluster_info['model'].__class__.__name__

            # Add the cluster's summary to the list
            summary_list.append(cluster_summary)

        # Create a DataFrame from the list of summaries
        df_summary = pd.DataFrame(summary_list)

        # If the summary list is empty, return an empty DataFrame with specified columns
        if not summary_list:
            return pd.DataFrame(columns=['cluster_id', 'MSE_min', 'MSE_max', 'model_name'])

        # Reorder columns based on the first row's keys if summary list is not empty
        first_row_keys = summary_list[0].keys()
        df_summary = df_summary.reindex(columns=first_row_keys)

        return df_summary

    def print_results(self, feature_session_state, df_with_clusters_mse_min):
        st.success("Predicting MSE min completed!")
        # Summarize the result from saved iterations and clusters
        st.write(
            f"Number of iterations: {feature_session_state.parameters['iterations']}")
        # Write clusters to table
        # st.write("Clusters:")
        # clusters = feature_session_state.parameters['clusters']
        # clusters_df = self.dict_to_table(clusters)
        # st.write(clusters_df)

        st.write(df_with_clusters_mse_min.head())

    def set_feature_parameters(self, feature_session_state):
        st.write("Monte Carlo simulation is run to predict MSE min for each cluster")
        col1, col2 = st.columns(2)
        slider_iterations_key = f"slider_iterations_{feature_session_state.created_at}"
        iterations = col1.slider(
            "Number of simulation iterations", 10, 200, 100, 10, key=slider_iterations_key)
        predicting_mse_button = col1.button("Start Predicting MSE min")
        return iterations, predicting_mse_button

    def to_dict(self):

        data = super().to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        """
        Create a new object from a dictionary.
        """
        # Get the class name from the dictionary
        class_name = data["__class__"]

        # Get the class from the global scope
        class_ = globals()[class_name]

        # Create a new object of the correct class
        feature = class_(name=data["name"], parameters=data["parameters"])

        # Set the properties of the object based on the values in the dictionary
        feature.description = data["description"]
        feature.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
        feature.activated = data["activated"]

        return feature
