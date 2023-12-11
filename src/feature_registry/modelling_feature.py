from datetime import datetime
import streamlit as st
import pickle
from .features import Feature
from ml_models import perform_optimization
from utils import ensure_directory_exists


class ModellingFeature(Feature):
    """
    ModellingFeature class inherits from the Feature class.
    It is used to perform training of ML models for each cluster.
    """

    def __init__(self, name: str, parameters: dict = None):
        """
        Initialize ModellingFeature with name and parameters.
        """
        super().__init__(name, "Modelling",
                         "Performance training ML models for each cluster", parameters)
        self.parameters = parameters or {}

    def execute(self, df, feature_session_state):
        """
        Execute the modelling feature on the given dataframe.
        """

        X_cols, y_col = self.set_feature_parameters(
            st.session_state['cleaned_columns'], feature_session_state)

        # If the user has selected columns for X and y and clicked the "Proceed Modelling" button,
        # set the parameters and activate the feature
        if X_cols and y_col and st.button("Proceed Modelling"):
            st.write(f"X_cols: {X_cols}")
            st.write(f"y_col: {y_col}")
            st.write(df.head())
            self.parameters['X_cols'] = X_cols
            self.parameters['y_col'] = y_col
            self.activated = True

            # Perform optimization and get the best models for each cluster
            scalers_best_models = self.modelling(df, feature_session_state)

            # Ensure trained_models folder in temp_folder, if not create one
            ensure_directory_exists('temp_folder/trained_models')

            # Save the trained models and corresponding scaler for each cluster
            self.parameters['path_scalers_best_models'] = self.save_scalers_and_models(
                scalers_best_models)

        # If the feature is activated, set self.parameters['scalers_best_models'] to the
        # file paths of trained models and scalers for each cluster if that has not been done
        # already
        if self.activated:
            feature_session_state.parameters['X_cols'] = self.parameters['X_cols']
            feature_session_state.parameters['y_col'] = self.parameters['y_col']
            feature_session_state.parameters['path_scalers_best_models'] = self.parameters['path_scalers_best_models']
            feature_session_state.activated = self.activated
            st.write("self.parameters['path_scalers_best_models'] is: ",
                     self.parameters['path_scalers_best_models'])
            st.write(
                feature_session_state.parameters['path_scalers_best_models'])

            scalers_best_models = self.load_saved_scalers_and_models(
                feature_session_state.parameters['path_scalers_best_models'])

            return df, scalers_best_models

    def load_saved_scalers_and_models(self, path_scalers_best_models):
        """
        Load the trained models and corresponding scaler for each cluster from the
        given file paths.
        """
        scalers_best_models = {}
        for cluster, scaler_best_model in path_scalers_best_models.items():
            with open(scaler_best_model['scaler'], 'rb') as f:
                scaler = pickle.load(f)

            with open(scaler_best_model['model'], 'rb') as f:
                model = pickle.load(f)

            scalers_best_models[cluster] = {
                'scaler': scaler,
                'model': model
            }

        return scalers_best_models

    def save_scalers_and_models(self, scalers_best_models):
        """
        Save the trained models and corresponding scaler for each cluster
        to temp_folder/trained_models and update self.parameters['scalers_best_models']
        with the file paths of trained models and scalers for each cluster.
        """

        dict_path_scalers_best_models = {}
        for cluster, scaler_best_model in scalers_best_models.items():
            with open(f"temp_folder/trained_models/scaler_cluster_{cluster}.pkl", 'wb') as f:
                pickle.dump(scaler_best_model['scaler'], f)

            with open(f"temp_folder/trained_models/model_cluster_{cluster}.pkl", 'wb') as f:
                pickle.dump(scaler_best_model['model'], f)

            dict_path_scalers_best_models[f"cluster{cluster}"] = {
                'scaler': f"temp_folder/trained_models/scaler_cluster_{cluster}.pkl",
                'model': f"temp_folder/trained_models/model_cluster_{cluster}.pkl"
            }
        st.write(
            f"dict_path_scalers_best_models from save_scalers_and_model: {dict_path_scalers_best_models}")
        return dict_path_scalers_best_models

    # def set_scaler_best_models(self, clusters):
    #     """
    #     Set self.parameters['scalers_best_models'] to the file paths of trained models
    #     and scalers for each cluster.
    #     """
    #     self.parameters['scalers_best_models'] = {}
    #     for cluster in clusters:
    #         self.parameters['scalers_best_models'][cluster] = {
    #             'scaler': f"temp_folder/trained_models/scaler_cluster_{cluster}.pkl",
    #             'model': f"temp_folder/trained_models/model_cluster_{cluster}.pkl"
    #         }

    def set_feature_parameters(self, cleaned_columns, feature_session_state):
        """
        Set the parameters for the modelling feature.
        """
        # Create two columns in the Streamlit app
        col1, col2 = st.columns(2)

        X_cols = col1.multiselect("Select columns for X", cleaned_columns,
                                  feature_session_state.parameters['X_cols'] if feature_session_state.parameters.get('X_cols') else [])

        # find the index of feature_session_state.parameters['y_col'] in cleaned_columns
        if feature_session_state.parameters.get('y_col', False):
            y_col_index = cleaned_columns.index(
                feature_session_state.parameters['y_col'])
        y_col = col2.selectbox("Select column for y", cleaned_columns,
                               y_col_index if feature_session_state.parameters.get('y_col') else None)

        return X_cols, y_col

    def modelling(self, df, feature_session_state):
        """
        Perform optimization on the given dataframe and return the best models for each cluster.
        """
        # Call the perform_optimization function from the ml_models module
        with st.spinner('Processing...'):
            with st.expander("Performing Optimization"):
                scalers_best_models = perform_optimization(
                    df, feature_session_state.parameters['X_cols'], feature_session_state.parameters['y_col'], progress_callback=st.write)
        return scalers_best_models

    def to_dict(self):
        """
        Convert the ModellingFeature to a dictionary.
        """
        data = super().to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        """
        Create a new ModellingFeature object from a dictionary.
        """
        # Create a new ModellingFeature object
        feature = cls(name=data["name"], parameters=data["parameters"])

        # Set the properties of the ModellingFeature object based on the values in the dictionary
        feature.description = data["description"]
        feature.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
        feature.activated = data["activated"]

        return feature
