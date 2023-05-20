from flask import Flask, render_template, request
import pandas as pd
from gower import gower_matrix

app = Flask(__name__)

# Load your survey data into a pandas DataFrame
data = pd.read_csv("260Datav2.csv")


# uniData = pd.read_csv("merged_data.csv")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recommendation', methods=['POST'])
def recommendation():
    # Get the user inputs from the form
    major = request.form['major']
    university = request.form['university']
    q1 = int(request.form['q1'])
    q2 = int(request.form['q2'])
    q3 = int(request.form['q3'])
    q4 = int(request.form['q4'])
    q5 = int(request.form['q5'])
    q6 = int(request.form['q6'])
    q7 = int(request.form['q7'])

    # Prepare the user input as a dictionary
    user_input = {
        "Hangi bölümde okuyorsunuz? LİSANS": major,
        "Hangi ünide okuyorsunuz? LİSANS": university,
        "Üniversitenin Dünya Sıralaması": q1,
        "Üniversitenin Akademik Bilinirliği": q2,
        "Üniversitenin Araştırma ve Yayıma Verdiği Önem": q3,
        "Programın İçeriği": q4,
        "Programın Akademik Bilinirliği": q5,
        "Programın Eğitim Dili": q6,
        "İngilizce konuşulan çevre": q7
    }

    # Convert the user input to a DataFrame
    user_input_df = pd.DataFrame(user_input, index=[0])

    # Concatenate the user input DataFrame to the existing dataset
    data_with_input = pd.concat([data, user_input_df], ignore_index=True)

    # Prepare the data for Gower's distance calculation
    categorical_cols = ["Hangi bölümde okuyorsunuz? LİSANS", "Hangi ünide okuyorsunuz? LİSANS"]
    numerical_cols = ["Üniversitenin Dünya Sıralaması", "Üniversitenin Akademik Bilinirliği",
                      "Üniversitenin Araştırma ve Yayıma Verdiği Önem", "Programın İçeriği",
                      "Programın Akademik Bilinirliği", "Programın Eğitim Dili", "İngilizce konuşulan çevre"]

    # Calculate Gower's distance matrix
    distance_matrix = gower_matrix(data_with_input[categorical_cols + numerical_cols])

    # Get the index of the user input row
    user_input_index = len(data_with_input) - 1

    # Calculate the distances between the user input and all other rows
    distances = distance_matrix[user_input_index, :]

    # Sort the distances and get the indices of the 5 most similar rows
    similar_indices = distances.argsort()[1:2]

    similar_rows = data.loc[similar_indices]

    # Get the university name from the most similar row
    most_similar_university = similar_rows.iloc[0]['Hangi ünide okuyorsunuz? YÜKSEKLİSANS']
    cluster = find_similar_universities(most_similar_university)
    cluster_df = pd.DataFrame(cluster)
    cluster_df.columns=['Universities']
    # Prepare the result message
    result_message = f"<h3>Universities:</h3>{cluster_df.to_html()}"

    return render_template('index.html', result=result_message)


def find_similar_universities(university):
    # Read the CSV file containing the universities and their cluster information
    df_mergedData = pd.read_csv('merged_data.csv')

    # Find the row with the matching university in the specified CSV file
    matched_row = df_mergedData[df_mergedData['University'] == university]

    if matched_row.empty:
        print(f"No matching university found: {university}")
        return []

    # Get the cluster ID of the matched university
    matched_cluster_id = matched_row['Cluster'].values[0]

    # Find all universities with the same cluster ID
    unis = df_mergedData[df_mergedData['Cluster'] == matched_cluster_id]['University'].tolist()

    return unis


if __name__ == '__main__':
    app.run()
