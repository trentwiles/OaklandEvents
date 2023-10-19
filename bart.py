import requests
import time

# BART's API is terrible, it will unexplainably reject your API key about half the time
# For this reason, the functions are written in a way so they run until a valid response
# is produced.

# If you would like to see the continued version of this, please see bart.trentwil.es
# I've developed a whole API that scrapes BART's website and puts it in JSON format
# Sadly, the actually BART API hardly works, so the following code is here for reference,
# and will not be used.

def getTrainEstimates(apiKey, origin):
    # Origin is the four letter all caps abriviation for a station
    api = requests.get(f"https://api.bart.gov/api/etd.aspx?cmd=etd&orig={origin}&json=y&key={apiKey}", headers={"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"})
    try:
        return api.json()["root"]["station"]["etd"]
    except:
        time.sleep(10)
        return getTrainEstimates(apiKey, origin)

