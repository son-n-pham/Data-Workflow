import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from utils import get_columns_by_mnemonics


def perform_kmeans(df, columns, k=None):

    columns = get_columns_by_mnemonics(df, columns)

    # Extract the columns for clustering
    data = df[columns]

    # Scale the data
    scaler = StandardScaler()
    data = scaler.fit_transform(data)

    if k is None:
        # List to hold the silhouette scores for each k
        silhouette_scores = []

        # Test k from 2 to 10 (silhouette score requires at least 2 clusters)
        for k in range(2, 11):
            kmeans = KMeans(n_clusters=k, random_state=1, n_init=10)
            kmeans.fit(data)
            score = silhouette_score(data, kmeans.labels_)
            silhouette_scores.append(score)

        # Plot the silhouette scores for each k
        plt.plot(range(2, 11), silhouette_scores, marker='o')
        plt.xlabel('Number of clusters')
        plt.ylabel('Silhouette Score')
        plt.show()

        # Find the k with the highest silhouette score
        k = silhouette_scores.index(max(silhouette_scores)) + 2

    # Perform KMeans with the specified or optimal number of clusters
    kmeans = KMeans(n_clusters=k, random_state=1)
    kmeans.fit(data)

    # Add the cluster labels to the original DataFrame
    df['cluster'] = kmeans.labels_

    return df
