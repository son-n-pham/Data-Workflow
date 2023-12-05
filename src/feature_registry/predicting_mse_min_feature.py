from .features import Feature


class PredictingMSEMinFeature(Feature):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.mse_min_params = kwargs
