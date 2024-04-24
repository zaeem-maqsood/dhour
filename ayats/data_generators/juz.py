import requests
import json


def create_juz_ayat_json_file(filename):
    # Initialize the JSON structure with an empty 'juz' list
    juz_data = {"juz": []}

    # Loop through each juz number
    for juz_number in range(1, 31):  # 1 to 30 inclusive
        response = requests.get(f"http://api.alquran.cloud/v1/juz/{juz_number}")

        if response.status_code == 200:  # Successful response
            data = response.json()
            ayahs = data["data"]["ayahs"]

            # Extract ayat numbers for the current juz
            ayat_numbers = [ayah["number"] for ayah in ayahs]

            # Append the juz information with its ayat numbers to the 'juz' list
            juz_data["juz"].append({"number": juz_number, "ayat": ayat_numbers})
        else:
            print(f"Failed to access data for juz {juz_number}")

    # Save the compiled data to a JSON file
    with open(filename, "w") as outfile:
        json.dump(juz_data, outfile, indent=4)

    print(f"Juz and Ayat data successfully saved to {filename}")


# Call the function with your desired filename
create_juz_ayat_json_file("juz_data.json")
