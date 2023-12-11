from .features import Feature
from optimize_for_mse_min import optimize_for_mse_min, add_mse_min_to_original_data


class PredictingMSEMinFeature(Feature):
    def __init__(self, name: str, parameters: dict = None):
        super().__init__(name, "Predicting MSE min",
                         "Predicting MSE min for each cluster", parameters)
        self.parameters = parameters or {}

    def execute(self, df_with_clusters, scalers_best_models,
                X_mnemonics=['TORQUE', 'WOB', 'RPM', 'Mu',
                             'Si', 'Dolomite', 'Limestone', 'Shale'],
                iterations=100):
        # Remove 'cluster' string in the keys of scalers_best_models
        scalers_best_models = {
            k.split("cluster")[-1]: v for k, v in scalers_best_models.items()}
        clusters = optimize_for_mse_min.execute_monte_carlo_optimization(
            df_with_clusters=df_with_clusters,
            scalers_best_models=scalers_best_models,
            X_mnemonics=X_mnemonics, iterations=100)
        df_with_clusters_mse_min = add_mse_min_to_original_data(
            df_with_clusters, clusters)

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
