import requests
import json
import os

# it is a dictionary. call key which is api_key: value
api_key = os.environ.get("api_key")

def get_geocode(location, company):
    geocodes = []
    
    for i in range(len(company)):
        loc = location[i]
        comp = company[i]
        url = f'https://maps.googleapis.com/maps/api/geocode/json?address={comp},{loc}&key={api_key}'
        response = requests.get(url).json()
        # {lat, lng}
        geocodes.append(response["results"][0]["geometry"]["location"])
        
    # return dict of list of lat lng.
    return geocodes