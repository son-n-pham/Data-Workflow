from .features import Feature


class OptimizingParametersFeature(Feature):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.optimizing_parameters_params = kwargs
