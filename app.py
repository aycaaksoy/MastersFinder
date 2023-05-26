from flask import Flask, render_template, request
import pandas as pd
from gower import gower_matrix
import json

app = Flask(__name__)

# Load your survey data into a pandas DataFrame
data = pd.read_csv("C:/Users/aycaa/PycharmProjects/MastersFinder/260Datav2.csv")
merged_data = pd.read_csv("C:/Users/aycaa/PycharmProjects/MastersFinder/merged_data.csv")

# Convert the merged_data DataFrame to a JSON object
merged_data_json = json.loads(merged_data.to_json(orient='records'))
unique_countries = merged_data['Country'].unique().tolist()


@app.route('/')
def index():
    merged_data_for_index = merged_data[["University", "Country"]]
    return render_template('index.html', merged_data=merged_data_json, unique_countries=unique_countries)


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

    # Get the selected countries from the form
    selected_countries = request.form.getlist('selectedCountries')
    merged_data_filtered = pd.DataFrame()

    # Filter the merged_data based on the selected countries
    if selected_countries[0] == '':
        merged_data_filtered = merged_data.copy()

    elif selected_countries[0] == 'allCountries':
        merged_data_filtered = merged_data.copy()

    elif "," in selected_countries[0]:
        # Split the selected_countries string by commas to obtain individual country names
        countries_list = [country.strip() for country in selected_countries[0].split(',')]
        for country in countries_list:
            # Filter the merged_data DataFrame for each country
            filtered_data = merged_data[merged_data['Country'] == country]
            # Concatenate the filtered data with the merged_data_filtered DataFrame
            merged_data_filtered = pd.concat([merged_data_filtered, filtered_data])

    else:
        merged_data_filtered = merged_data[merged_data['Country'].isin(selected_countries)]

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
    cluster = find_similar_universities(most_similar_university, merged_data_filtered)
    cluster_df = pd.DataFrame(cluster)

    # Prepare the result message
    result_message = f"<h3>Universities:</h3>{cluster_df.to_html()}"

    return render_template('index.html', result=result_message, merged_data=merged_data_json,
                           unique_countries=unique_countries)


def find_similar_universities(university, datav1):
    if datav1.empty:
        print("No data available")
        return []

    matched_row = merged_data[merged_data['University'] == university]
    if matched_row.empty:
        print(f"No matching universities found for the selected countries")
        return []

    # Get the cluster IDs of the matched universities
    matched_cluster_id = matched_row['Cluster'].values[0]

    # Find all universities with the same cluster IDs
    unis = datav1[datav1['Cluster'] == matched_cluster_id]['University'].tolist()

    return unis


if __name__ == '__main__':
    app.run(debug=True)
