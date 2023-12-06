from datetime import datetime
import streamlit as st
from .features import Feature
from cluster import perform_kmeans


class ClusteringFeature(Feature):
    def __init__(self, name: str, parameters: dict = None):
        super().__init__(name, "Clustering", "Performs clustering on the data", parameters)
        self.parameters = parameters or {}

    def execute(self, df):
        # Call the perform_kmeans function from the cluster module
        df_new = self.kmeans(df)
        return df_new

    def kmeans(self, df):
        # Call the perform_kmeans function from the cluster module
        df = perform_kmeans(
            df, self.parameters['columns'], self.parameters['k'])
        return df

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
        if col1.checkbox("Select number of clusters automatically"):
            self.parameters['k'] = None
        else:
            self.parameters['k'] = col3.slider(
                "Select k", min_value=2, max_value=11, value=3)

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
