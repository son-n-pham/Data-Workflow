### How to add a feature

Here is an example of adding clustering feature:

- I have the cluster module available in src
- Create clustering_feature.py in feature_registry module
- In clustering_feature.py, create class ClusteringFeature which inherit base class Feature
- Open cluster module to check if it require more attributes than the base's attributes
  - ![Alt text](image.png)
  - As cheking, it requires attribute columns which is a list and k of integer or None. Those can be stored in parameters.
- Fill in the ClusteringFeature class:

```python
class ClusteringFeature(Feature):
    def __init__(self, name: str, parameters: dict = None):
        super().__init__(name, "Clustering", "Performs clustering on the data", parameters)

    def execute(self, df):
        # Call the perform_kmeans function from the cluster module
        df = perform_kmeans(
            df, self.parameters['columns'], self.parameters['k'])
        return df

    def to_dict(self):
        data = super().to_dict()
        return data

    @classmethod
    def from_dict(cls, data):
        # Create a new GraphFeature object
        feature = cls(
            name=data["name"],
            parameters=data["parameters"],
        )

        # Set the properties of the GraphFeature object based on the values in the dictionary
        feature.description = data["description"]
        feature.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
        feature.activated = data["activated"]
        feature.type = data["type"]

        return feature
```

-
