from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


def kmeans_cluster(df, columns, k=None):
    # Extract the columns for clustering
    data = df[columns]

    if k is None:
        # List to hold the SSE for each k
        sse = []

        # Test k from 1 to 10
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, random_state=1)
            kmeans.fit(data)
            sse.append(kmeans.inertia_)

        # Plot the SSE for each k
        plt.plot(range(1, 11), sse)
        plt.xticks(range(1, 11))
        plt.xlabel("Number of Clusters")
        plt.ylabel("SSE")
        plt.show()

        # Find the elbow point
        k = sse.index(min(sse)) + 1

    # Perform KMeans with the specified or optimal number of clusters
    kmeans = KMeans(n_clusters=k, random_state=1)
    kmeans.fit(data)

    # Add the cluster labels to the original DataFrame
    df['cluster'] = kmeans.labels_

    return df
