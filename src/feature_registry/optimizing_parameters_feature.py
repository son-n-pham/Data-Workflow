import streamlit as st
import pandas as pd
import os
import config
from utils import misc
from optimize_parameters import monte_carlo_optimization
from .features import Feature


class OptimizingParametersFeature(Feature):
    def __init__(self, name: str, parameters: dict = None):
        super().__init__(name, "Optimizing Drilling Parameters",
                         "Optimizing Drilling Parameters", parameters)
        self.parameters = parameters or {}

    def execute(self, df_with_clusters, scalers_best_models,
                feature_session_state,
                X_mnemonics=['TORQUE', 'WOB', 'RPM', 'Mu',
                             'Si', 'Dolomite', 'Limestone', 'Shale']):
        st.write(df_with_clusters.head())

        wob_range, torque_range, rpm_range, mse_tolerance, iterations = self.set_feature_parameters(
            feature_session_state)

        # Create a folder to store optimized parameters
        optimized_paramaters_folder = os.path.join(
            config.temp_directory, "optimized_parameters")
        misc.ensure_directory_exists(optimized_paramaters_folder)

        if st.button("Optimize Parameters"):
            st.write("Optimizing parameters...")

            # Compile wob_range, torque_range, rpm_range into bounds dictionary
            bounds = {
                "wob": wob_range,
                "torque": torque_range,
                "rpm": rpm_range
            }

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

            with st.spinner("Optimizing parameters..."):
                with st.expander("Show details"):
                    optimized_parameters = monte_carlo_optimization(df_with_clusters,
                                                                    X_mnemonics,
                                                                    scalers_best_models,
                                                                    bounds,
                                                                    mse_tolerance=mse_tolerance,
                                                                    iterations=iterations)

            # Save optimized_parameters to a CSV file

            optimized_parameters.to_csv(os.path.join(
                optimized_paramaters_folder, "optimized_parameters.csv"), index=False)

            feature_session_state.activated = True

        if feature_session_state.activated:

            st.success("Optimizing parameters completed!")

            optimized_parameters = pd.read_csv(os.path.join(
                optimized_paramaters_folder, "optimized_parameters.csv"))

            st.write("Quantile summary:")
            df_quantile_summary = optimized_parameters.groupby('cluster')[['WOB (klbs)', 'BIT_RPM (rpm)',
                                                                           'TORQUE (kLbf.ft)', 'ROP (m/h)', 'MSE (ksi)']].quantile([0.25, 0.5, 0.75])
            st.write(df_quantile_summary)

            return df_with_clusters

    def set_feature_parameters(self, feature_session_state):

        st.write("Select the parameter ranges for optimizing")

        col1, col2, col3 = st.columns(3)
        wob_slider_key = f"wob_slider_{feature_session_state.created_at}"
        wob_range = col1.slider("WOB (klbs)", 0, 100,
                                (1, 30), 1, key=wob_slider_key)
        torque_slider_key = f"torque_slider_{feature_session_state.created_at}"
        torque_range = col2.slider(
            "Torque (klbs-ft)", 0, 50, (1, 15), 1, key=torque_slider_key)
        rpm_slider_key = f"rpm_slider_{feature_session_state.created_at}"
        rpm_range = col3.slider("RPM (rpm)", 0, 500,
                                (140, 160), 1, key=rpm_slider_key)

        mse_tolerance_key = f"mse_tolerance_{feature_session_state.created_at}"
        mse_tolerance = st.slider(
            "How much MSE can be higher than MSE_min", 0.0, 10.0, 3.0, 0.1, key=mse_tolerance_key)

        iterations_key = f"iterations_{feature_session_state.created_at}"
        iterations = st.slider("Number of iterations",
                               100, 20000, 10000, 100, key=iterations_key)

        return wob_range, torque_range, rpm_range, mse_tolerance, iterations

    def to_dict(self):

        data = super().to_dict()
        return data

    @classmethod
    def from_dict(cls, data):

        feature = cls(name=data["name"], parameters=data["parameters"])

        feature.description = data["description"]
        feature.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
        feature.activated = data["activated"]

        return feature
