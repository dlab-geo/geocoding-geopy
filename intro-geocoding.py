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

# try the following commands to figure out whether to manipulate by key or by index
# type(response)
# response.keys() 
# response[0]

#################################################################################################
# Write a customized function based on the format of the response object and information needed #
#################################################################################################

def get_coords_geopy(address, geocoder_instance):
    response = geocoder_instance.geocode(address) 
    lat_lon = response[1][0], response[1][1]
    return lat_lon

coords = get_coords_geopy("1600 Amphitheatre Pkwy, Mountain View, CA", google_geocoder)
coords

#######################################
# Load csv data into pandas DataFrame #
####################################### 

bart = pd.read_csv("data/bartstations.csv")
type(bart)
bart.keys()

####################################################
# Pass addresses through get_coords_geopy function #
####################################################

google_geocoder = geopy.geocoders.GoogleV3(api_key=my_api_key)
bart['latitude'], bart['longitude'] = zip(*bart['address'].apply(lambda x: get_coords_geopy(x, google_geocoder)))

bart[['station_name', 'latitude', 'longitude']]

###############################
# Map your geocoded addresses #
###############################
# The following code creates the bart_coords.geojson and bart_coords.js files in the map/geojson folder
# bart_coords.js is used by map/bartmap.html for our mapping of BART stations
# Troubleshooting tip: Some installations may have an issue with "wb" and "rb" in subsequent code. Try "w" & "r" 

geo_data = {
    'type': 'FeatureCollection', 
    'features': []
}

# create a feature for each row of data and push into geo_data object 
for i in bart.index:
    feature = {
        'type': 'Feature', 
        'geometry': {
            "type": "Point", 
            "coordinates": [float(bart['longitude'][i]), float(bart['latitude'][i])]
        },
            'properties': {
                'station_name': bart['station_name'][i]
            }
    }

    # Add the feature into the GeoJSON wrapper
    geo_data['features'].append(feature)

with open('map/geojson/bart_coords.geojson', 'w') as f:
    json.dump(geo_data, f, indent=2)

# create bart_coords.js file 
with open('map/geojson/bart_coords.geojson', 'r') as infile:
    lines = infile.readlines()

    with open('map/geojson/bart_coords.js', 'w') as outfile:
        outfile.write('var bart = ')
        outfile.writelines(lines)

infile.close()
outfile.close()










