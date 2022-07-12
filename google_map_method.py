import json
import urllib.request
import requests
import time
import googlemaps
from pprint import pprint
from bs4 import BeautifulSoup


with open('json/keys.json') as f:
    data = json.load(f)

# search_results: Get the detail results nearby the specific location.
def get_Top5(lat, lng, radius, place_type):
    place_type =  "%2C".join(str(type_ele) for type_ele in place_type )
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(lat) + "%2C" + str(lng) + "&radius=" + str(radius) + "&type=" + place_type + "&language=zh-TW&key=" + data['googleMapKey']
    # search
    headers = {}
    payload = {}
    # all the result details
    response = requests.get(url, headers = headers, data = payload)
    pprint(response.json())
    response_dict = response.json()
    search_results = response_dict["results"]
    # sorted and limited to 5 results
    results = sorted(search_results, key=lambda result : (result['rating'] is not None, result['rating']), reverse=True)[:5]
    return results


#find the specific location
def get_latitude_longtitude(address):
    address = urllib.request.quote(address)
    url = "https://www.google.com/maps/place?q=" + address

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.prettify() #text including all the html detail
    initial_pos = text.find(";window.APP_INITIALIZATION_STATE")
    #find ";window.APP_INITIALIZATION_STATE" 
    data = text[initial_pos+36:initial_pos+85] #get lat, lng range position
    pprint(str_convert_num(data))
    return str_convert_num(data)

# some_num, lng, lat
def str_convert_num(data):
    line = tuple(data.split(','))
    return line[2], line[1]
