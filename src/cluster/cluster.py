import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import streamlit as st

from utils import get_columns_by_mnemonics


def perform_kmeans(df, columns, k=None, k_min=2, k_max=11):

    columns = get_columns_by_mnemonics(df, columns)

    # Extract the columns for clustering
    data = df[columns]

    # Scale the data
    scaler = StandardScaler()
    data = scaler.fit_transform(data)

    # List to hold the silhouette scores for each k
    silhouette_scores = []

    if k is None:

        # Test k from 2 to 10 (silhouette score requires at least 2 clusters)
        for k in range(k_min, k_max):
            kmeans = KMeans(n_clusters=k, random_state=1, n_init=10)
            kmeans.fit(data)
            score = silhouette_score(data, kmeans.labels_)
            silhouette_scores.append(score)

        # Plot the silhouette scores for each k
        plt.plot(range(k_min, k_max), silhouette_scores, marker='o')
        plt.xlabel('Number of clusters')
        plt.ylabel('Silhouette Score')
        plt.show()

        # Find the k with the highest silhouette score
        k = silhouette_scores.index(max(silhouette_scores)) + 2

    # Perform KMeans with the specified or optimal number of clusters
    kmeans = KMeans(n_clusters=k, random_state=1)
    kmeans.fit(data)

    st.write(
        f'Silhouette score in cluster.py: {silhouette_scores}')

    # Add the cluster labels to the original DataFrame if there is no cluster column
    # already, otherwise replace the existing cluster column
    df['cluster ()'] = kmeans.labels_

    return df, silhouette_scores, k
