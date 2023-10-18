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
        "Dublin/Pleasanton": "DUBL",
        "El Cerrito del Norte": "DELN",
        "El Cerrito Plaza": "PIZA",
        "Embarcadero (SF)": "EMBR",
        "Fremont": "FRMT",
        "Fruitvale (Oakland)": "FTVL",
        "Glen Park (SF)": "GLEN",
        "Hayward": "HAYW",
        "Lafayette": "LAFY",
        "Lake Merritt (Oakland)": "LAKE",
        "MacArthur (Oakland)": "MCAR",
        "Millbrae": "MIBR",
        "Montgomery St. (SF)": "MONT",
        "North Berkeley": "NBRK",
        "North Concord/Martinez": "NCON",
        "Oakland Int'l Airport": "OAKL",
        "Orinda": "ORIN",
        "Pittsburg/Bay Point": "PITT",
        "Pittsburg Center": "PCTR",
        "Pleasant Hill": "PHIL",
        "Powell St. (SF)": "POWL",
        "Richmond": "RICH",
        "Rockridge (Oakland)": "ROCK",
        "San Bruno": "SBRN",
        "San Leandro": "SANL",
        "South San Fransisco": "SSAN",
        "Union City": "UCTY",
        "Warm Springs/South Fremont": "WARM",
        "Walnut Creek": "WCRK",
        "West Dublin": "WDUB",
        "West Oakland": "WOAK"
    }

def getStationAbbreviationByName(name):
    return getStationAbbreviations()[name]

def getEnglishStationNameFromAbbreviation(name):
    list = []
    for x in getStationAbbreviations().items():
        if name == x[1]:
            return x[0]
    return None