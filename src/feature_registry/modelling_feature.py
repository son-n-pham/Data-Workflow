from .features import Feature


class ModellingFeature(Feature):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.ml_params = kwargs
