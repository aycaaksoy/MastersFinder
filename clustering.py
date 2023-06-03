import pandas as pd
from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer

df_base = pd.read_csv("C:/Users/aycaa/PycharmProjects/MastersFinder/RankingsEurope.csv")
df = df_base.copy()

df.columns = ["Country", "University Name", "University Score", "Diversity Score"]

kmeans = KMeans()
visualizer = KElbowVisualizer(kmeans, k=(1, 10))
visualizer.fit(df["University Score"].values.reshape(-1, 1))
visualizer.fit(df["Diversity Score"].values.reshape(-1, 1))
# visualizer.show()

# Set the optimal number of clusters determined from the elbow method
num_clusters = 3

# Perform K-means clustering
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(df["University Score"].values.reshape(-1, 1))
kmeans.fit(df["Diversity Score"].values.reshape(-1, 1))

# Assign cluster labels to each data point
cluster_labels = kmeans.labels_

# Print the cluster labels
print(cluster_labels)

# Create a new DataFrame with the cluster labels
df_clustered = pd.DataFrame({'Country': df['Country'], 'University Name': df['University Name'],
                             'University Score': df['University Score'], 'Diversity Score': df['Diversity Score'],
                             'Cluster': cluster_labels})

# Save the DataFrame to a new CSV file
df_clustered.to_csv('clustered_data.csv', index=False, encoding='utf-8')

# Count the number of items in each cluster
cluster_counts = df_clustered['Cluster'].value_counts().sort_index()

# Get the unique cluster names
cluster_names = df_clustered['Cluster'].unique()

# Print the cluster names and their respective item counts
for cluster in cluster_names:
    count = cluster_counts[cluster]
    print(f"Cluster {cluster}: {count} items")