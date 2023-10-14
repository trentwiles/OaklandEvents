import requests

def getStops(apiKey, route):
    data = requests.get(f"https://api.actransit.org/transit/route/{route}/stops?token={apiKey}")
    if data.status_code == 200:
        return data.json()[0]["Stops"]
    raise ValueError(f"AC Transit API Error (HTTP {data.status_code})")

def getBusTime(apiKey, stopID, routeID):
    data = requests.get(f"https://api.actransit.org/transit/stops/{stopID}/predictions/?token={apiKey}")
    if data.status_code == 200:
        times = []
        for x in data.json():
            if x['RouteName'] == routeID:
                times.append(x)
    return times