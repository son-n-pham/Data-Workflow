from datetime import datetime
import pandas as pd
import streamlit as st
from .features import Feature
from cluster import perform_kmeans
from config import config_constants
from file_handle import save_clustered_df_to_file_and_update_session_state, load_file_standardize_header


class ClusteringFeature(Feature):
    def __init__(self, name: str, parameters: dict = None):
        super().__init__(name, "Clustering", "Performs clustering on the data", parameters)
        self.parameters = parameters or {}

    def execute(self, df, feature_session_state):

        clustered_columns, k, auto_cluster = self.set_feature_parameters(
            st.session_state['cleaned_columns'],
            feature_session_state)

        # If the user has selected columns for clustering and clicked the "Proceed Clustering" button,
        # set the parameters and activate the feature
        if clustered_columns and st.button("Proceed Clustering"):
            self.parameters['clustered_columns'] = clustered_columns
            self.parameters['k'] = k
            self.parameters['auto_cluster'] = auto_cluster
            self.activated = True

            # Call the perform_kmeans function from the cluster module
            df_new = self.kmeans_clustering(df)

            # Append 'cluster ()' to cleaned_columns in session state
            if 'cluster ()' not in st.session_state['cleaned_columns']:
                st.session_state['cleaned_columns'].append('cluster ()')

            df_new = save_clustered_df_to_file_and_update_session_state(
                df_new)

        # If the feature is activated and self.parameters['silhouette_scores']
        # is not an empty list, plot the silhouette scores
        if self.activated:

            df = load_file_standardize_header(st.session_state['loaded_file'])

            # Update feature_session_state
            feature_session_state.parameters['clustered_columns'] = self.parameters['clustered_columns']
            feature_session_state.parameters['k'] = self.parameters['k']
            feature_session_state.parameters['auto_cluster'] = self.parameters['auto_cluster']
            feature_session_state.parameters['silhouette_score'] = self.parameters['silhouette_score']
            feature_session_state.activated = self.activated

            if self.parameters['silhouette_score']:
                self.plot_silhouette_scores(
                    self.parameters['silhouette_score'])

            st.success("Clustering has been done!")

            return df

    def kmeans_clustering(self, df):
        # Call the perform_kmeans function from the cluster module
        df, self.parameters['silhouette_score'], self.parameters['k'] = perform_kmeans(
            df, self.parameters['clustered_columns'],
            self.parameters['k'],
            config_constants['k_min'],
            config_constants['k_max'])
        return df

    def set_feature_parameters(self, cleaned_columns, feature_session_state):
        col1, col2, col3 = st.columns(3)

        clustered_columns = col2.multiselect(
            "Select columns to perform clustering on",
            cleaned_columns,
            feature_session_state.parameters.get('clustered_columns', []),
        )

        auto_cluster = col1.checkbox(
            "Select number of clusters automatically",
            value=feature_session_state.parameters["auto_cluster"] if feature_session_state.parameters.get("auto_cluster") else False)

        k = None if auto_cluster else col1.slider(
            "Select k",
            min_value=config_constants['k_min'],
            max_value=config_constants['k_max'],
            value=3,
            disabled=auto_cluster)

        return clustered_columns, k, auto_cluster

    def plot_silhouette_scores(self, silhouette_scores):
        # plot silhouette score to scatter plot if silhouette_scores is not an empty list
        if silhouette_scores:
            # Convert the silhouette scores to a DataFrame with an appropriate index
            silhouette_scores_df = pd.DataFrame(silhouette_scores, index=range(
                config_constants['k_min'], config_constants['k_min'] + len(silhouette_scores)))

            # Plot the silhouette scores
            st.line_chart(silhouette_scores_df)

    def to_dict(self):
        data = super().to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        # Create a new GraphFeature object
        feature = cls(
            name=data["name"],
            parameters=data["parameters"]
        )

        # Set the properties of the GraphFeature object based on the values in the dictionary
        feature.description = data["description"]
        feature.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
        feature.activated = data["activated"]

        return feature
