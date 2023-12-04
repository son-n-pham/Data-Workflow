from .features import Feature


class ClusteringFeature(Feature):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.cluster_params = kwargs
