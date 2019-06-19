import requests
import json

def get_geocode(location, company):
    api_key = "AIzaSyBPtKgw6FBdWbmvt1Og_nrDdcAe9eFGSQA"
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


