from datetime import datetime
import pandas as pd
import streamlit as st
from .features import Feature
from cluster import perform_kmeans


class ClusteringFeature(Feature):
    def __init__(self, name: str, parameters: dict = None):
        super().__init__(name, "Clustering", "Performs clustering on the data", parameters)
        self.parameters = parameters or {}

    def execute(self, df):
        self.parameters["silhouette_scores"] = []

        # Call the perform_kmeans function from the cluster module
        df_new, self.parameters["silhouette_scores"], self.parameters['k'] = self.kmeans(
            df)

        return df_new

    def kmeans(self, df):
        # Call the perform_kmeans function from the cluster module
        df, silhouette_score, k = perform_kmeans(
            df, self.parameters['columns'],
            self.parameters['k'],
            self.parameters['k_min'],
            self.parameters['k_max'])
        return df, silhouette_score, k

    def set_feature_parameters(self, cleaned_columns):
        col1, col2, col3 = st.columns(3)
        # col1 is to select the columns to perform clustering on
        # multiselect is used to select multiple columns from the list
        # of cleaned_columns in session state
        self.parameters['columns'] = col2.multiselect(
            "Select columns to perform clustering on", cleaned_columns)
        # col2 is check box to select whether to use optimal k or not
        # if checked, k is set to None; otherwise, activate col3
        # col3 is to select the value of k by getting input from user using slider
        self.parameters['k_min'] = 2
        self.parameters['k_max'] = 11
        if col1.checkbox("Select number of clusters automatically"):
            self.parameters['k'] = None
        else:
            self.parameters['k'] = col3.slider(
                "Select k", min_value=self.parameters['k_min'], max_value=self.parameters['k_max'], value=3)

    def plot_sihouetteS_score(self, silhouette_scores):
        # plot silhouette score to scatter plot if silhouette_scores is not an empty list
        if silhouette_scores:
            # Convert the silhouette scores to a DataFrame with an appropriate index
            silhouette_scores_df = pd.DataFrame(silhouette_scores, index=range(
                self.parameters['k_min'], self.parameters['k_min'] + len(silhouette_scores)))

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
