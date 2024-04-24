import requests
import json


def create_rukus_ayat_json_file(filename):
    # Initialize the JSON structure with an empty 'rukus' list
    rukus_data = {"rukus": []}

    # Loop through each ruku number
    for ruku_number in range(1, 559):  # 1 to 558 inclusive
        response = requests.get(f"http://api.alquran.cloud/v1/ruku/{ruku_number}")

        if response.status_code == 200:  # Successful response
            data = response.json()
            ayahs = data["data"]["ayahs"]

            # Extract ayat numbers for the current ruku
            ayat_numbers = [ayah["number"] for ayah in ayahs]

            # Append the ruku information with its ayat numbers to the 'rukus' list
            rukus_data["rukus"].append({"number": ruku_number, "ayat": ayat_numbers})
        else:
            print(f"Failed to access data for ruku {ruku_number}")

    # Save the compiled data to a JSON file
    with open(filename, "w") as outfile:
        json.dump(rukus_data, outfile, indent=4)

    print(f"Ruku and Ayat data successfully saved to {filename}")


# Call the function with your desired filename
create_rukus_ayat_json_file("rukus_ayat_data.json")
