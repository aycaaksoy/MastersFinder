import pandas as pd


def find_similar_universities(University):
    # Read the CSV file containing the universities and their cluster information
    df_mergedData = pd.read_csv('merged_data.csv')

    # Find the row with the matching university in the specified CSV file
    matched_row = df_mergedData[df_mergedData['University'] == University]

    if matched_row.empty:
        print(f"No matching university found: {University}")
        return []

    # Get the cluster ID of the matched university
    matched_cluster_id = matched_row['Cluster'].values[0]

    # Find all universities with the same cluster ID
    unis = df_mergedData[df_mergedData['Cluster'] == matched_cluster_id]['University'].tolist()

    return unis

