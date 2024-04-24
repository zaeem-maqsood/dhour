import requests
import json


def create_hizb_quarters_json_file(filename):
    # Initialize the JSON structure with an empty 'hizbQuarters' list
    hizb_quarters_data = {"hizbQuarters": []}

    # Loop through each hizb quarter number
    for hizb_quarter in range(1, 241):  # 1 to 240 inclusive
        response = requests.get(
            f"http://api.alquran.cloud/v1/hizbQuarter/{hizb_quarter}"
        )

        if response.status_code == 200:  # Successful response
            data = response.json()
            ayahs = data["data"]["ayahs"]

            # Extract juz and ayat numbers for the current hizb quarter
            juz_number = ayahs[0]["juz"] if ayahs else None
            ayat_numbers = [ayah["number"] for ayah in ayahs]

            # Append the hizb quarter information with its juz and ayat numbers to the 'hizbQuarters' list
            hizb_quarters_data["hizbQuarters"].append(
                {"juz": juz_number, "number": hizb_quarter, "ayat": ayat_numbers}
            )
        else:
            print(f"Failed to access data for hizb quarter {hizb_quarter}")

    # Save the compiled data to a JSON file
    with open(filename, "w") as outfile:
        json.dump(hizb_quarters_data, outfile, indent=4)

    print(f"Hizb Quarters data successfully saved to {filename}")


# Call the function with your desired filename
create_hizb_quarters_json_file("hizb_quarters_data.json")
