from datetime import datetime
import streamlit as st
from .features import Feature
from ml_models import perform_optimization
from utils import ensure_directory_exists


class ModellingFeature(Feature):
    def __init__(self, name: str, parameters: dict = None):
        super().__init__(name, "Modelling",
                         "Performance training ML models for each cluster", parameters)
        self.parameters = parameters or {}

    def execute(self, df):
        scalers_best_models = self.modelling(df)
        # Ensure trained_models folder in temp_folder, if not create one
        ensure_directory_exists('temp_folder/trained_models')
        # Save the trained models and corresponding scaler for each cluster
        # to temp_folder/trained_models
        for cluster, scaler_best_model in scalers_best_models.items():
            scaler_best_model['scaler'].save(
                f"temp_folder/trained_models/scaler_cluster_{cluster}.pkl")
            scaler_best_model['model'].save(
                f"temp_folder/trained_models/model_cluster_{cluster}.pkl")

    def set_feature_parameters(self, cleaned_columns):
        col1, col2 = st.columns(2)
        X_cols = col1.multiselect(
            "Select columns for X", cleaned_columns)
        y_col = col2.selectbox("Select column for y", cleaned_columns)
        if X_cols and y_col and st.button("Proceed Modelling"):
            self.parameters['X_cols'] = X_cols
            self.parameters['y_col'] = y_col
            self.activated = True

    def modelling(self, df):
        # Call the perform_optimization function from the ml_models module
        scalers_best_models = perform_optimization(
            df, self.parameters['X_cols'],
            self.parameters['y_col'])
        return scalers_best_models

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
