import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime


def scrape_koeri_earthquakes():
    """
    Scrapes earthquake data from KOERI (Kandilli Observatory and Earthquake Research Institute)
    website and returns a DataFrame with the place and magnitude information.
    """
    # URL of the KOERI earthquake list
    url = "http://www.koeri.boun.edu.tr/scripts/lst9.asp"

    try:
        # Send HTTP request to the website
        response = requests.get(url)
        response.encoding = 'ISO-8859-9'  # Set the encoding for Turkish characters

        # Check if the request was successful
        if response.status_code != 200:
            return f"Failed to retrieve data. Status code: {response.status_code}"

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the pre tag that contains the earthquake data
        pre_tag = soup.find('pre')
        if not pre_tag:
            return "Could not find earthquake data on the page."

        # Get the text from the pre tag
        data_text = pre_tag.text

        # Skip the header lines
        lines = data_text.strip().split('\n')
        data_lines = []

        for line in lines:
            if re.match(r'^\d{4}', line.strip()):  # Lines starting with a year (YYYY)
                data_lines.append(line)

        # Parse each line to extract the relevant information
        earthquakes = []

        for line in data_lines:
            # The format might change, but typically:
            # Date, Time, Lat, Lon, Depth, MD, ML, Mw, Place
            parts = re.split(r'\s+', line.strip())

            if len(parts) >= 9:
                # Extract magnitude (using ML - local magnitude)
                ml_index = 6  # Index for ML (local magnitude)
                magnitude = parts[ml_index]

                # Extract place (everything after the numerical data)
                place_index = 8  # This might vary
                place = ' '.join(parts[place_index:])

                earthquakes.append({
                    'Date': f"{parts[0]} {parts[1]}",
                    'Magnitude': magnitude,
                    'Place': place
                })

        # Create a DataFrame
        df = pd.DataFrame(earthquakes)
        return df

    except Exception as e:
        return f"An error occurred: {str(e)}"


# Run the function and display the results
if __name__ == "__main__":
    print("Scraping earthquake data from KOERI...")
    earthquakes_df = scrape_koeri_earthquakes()

    if isinstance(earthquakes_df, pd.DataFrame):
        print(f"Found {len(earthquakes_df)} recent earthquakes:")
        print(earthquakes_df[['Date', 'Magnitude', 'Place']])
    else:
        print(earthquakes_df)  # Print error message