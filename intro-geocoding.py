import json
import requests
import pandas as pd
import geopy
from pprint import pprint

##################
# Photon example #
##################
def get_geocoded_object_photon(address):
    # URL
    url = 'http://photon.komoot.de/api/?q=' + address.replace(' ', '+')
    
    # Response
    response = requests.get(url)
    return json.loads(response.text)

get_geocoded_object_photon("1600 Amphitheatre Pkwy, Mountain View, CA")

################
# Geopy Module #
################

my_api_key = "[your api key]" 
google_geocoder = geopy.geocoders.GoogleV3(api_key=my_api_key)

response = google_geocoder.geocode("1600 Amphitheatre Pkwy, Mountain View, CA", google_geocoder) 

#####################################
# Manipulating your response object #
#####################################

# try the following commands to figure out whether to manipulate by key or by index?
# type(response)
# response.keys() 
# response[0]



