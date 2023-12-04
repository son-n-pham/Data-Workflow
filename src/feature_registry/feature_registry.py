from .graph_feature import GraphFeature
from .clustering_feature import ClusteringFeature
from .modelling_feature import ModellingFeature
from .predicting_mse_min_feature import PredictingMSEMinFeature
from .optimizing_parameters_feature import OptimizingParametersFeature

FEATURE_REGISTRY = {
    "Graph": GraphFeature,
    "Clustering": ClusteringFeature,
    "Modelling": ModellingFeature,
    "PredictingMSEMin": PredictingMSEMinFeature,
    "OptimizingParameters": OptimizingParametersFeature,
}
