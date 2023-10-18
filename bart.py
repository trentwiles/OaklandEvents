import requests
import time

# BART's API is terrible, it will unexplainably reject your API key about half the time
# For this reason, the functions are written in a way so they run until a valid response
# is produced.

def getTrainEstimates(apiKey, origin):
    # Origin is the four letter all caps abriviation for a station
    api = requests.get(f"https://api.bart.gov/api/etd.aspx?cmd=etd&orig={origin}&json=y&key={apiKey}")
    try:
        return api.json()["root"]["station"]
    except:
        time.sleep(3)
        return getTrainEstimates(apiKey, origin)

def getStationAbbreviations():
    # I have about half of them
    return {
        "12th St. Oakland City Center": "12TH",
        "16th St. Mission (SF)": "16TH",
        "19th St. Oakland": "19TH",
        "24th St. Mission (SF)": "24TH",
        "Ashby (Berkeley)": "ASHB",
        "Antioch": "ANTC",
        "Balboa Park (SF)": "BALB",
        "Bay Fair (San Leandro)": "BAYF",
        "Castro Valley": "CAST",
        "Civic Center (SF)": "CIVC",
        "Coliseum": "COLS",
        "Colma": "COLM",
        "Concord": "CONC",
        "Daly City": "DALY",
        "Downtown Berkeley": "DBRK",
        "Dublin/Pleasanton": "DUBL"
    }