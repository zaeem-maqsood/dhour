import requests
import json


def create_json_file(filename):
    # The initial JSON structure
    json_data = {"ayats": []}

    # Loop through each surah
    for surah in range(1, 115):  # 1 to 114 inclusive
        # Access the API endpoint for the current surah
        response = requests.get(f"http://api.alquran.cloud/v1/surah/{surah}")

        if response.status_code == 200:  # Successful response
            # Parse the JSON response
            data = response.json()
            ayahs = data["data"]["ayahs"]
            for ayat in ayahs:
                print("Adding ayat " + str(ayat))
                number = ayat["number"]
                ayat_in_surah = ayat["numberInSurah"]
                json_data["ayats"].append(
                    {"surah": surah, "number": number, "ayat_in_surah": ayat_in_surah}
                )
        else:
            print(f"Failed to access data for surah {surah}")

    # Save the JSON structure to a file
    with open(filename, "w") as outfile:
        json.dump(json_data, outfile, indent=4)

    print(f"Data successfully saved to {filename}")


# Call the function with your desired filename
create_json_file("ayats_data.json")
