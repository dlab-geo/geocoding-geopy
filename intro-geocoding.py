
# coding: utf-8

# # Introductory Geocoding and Mapping

# Juan Shishido, Andrew Chong, Patty Frontiera
# 
# Adapted from Juan Shishido's tutorial at: http://people.ischool.berkeley.edu/~juanshishido/geocoding-workshop/intro-geocoding.html
# 
# School of Information
# 
# GSR, D-Lab

# ## Imports

# In[ ]:

import json
import requests
import pandas as pd
import geopy
from pprint import pprint


# ## Using A Geocoding APIs
# There are a number of Geocoding APIs that you can use to geocode place names and addresses. To use one of these you create code like that shown below. Each geocoding service may have different inputs and outputs.

# ### Photon API
# Here is an example of geocoding with the Photon API.

# In[ ]:

def get_geocoded_object_photon(address):
    # URL
    url = 'http://photon.komoot.de/api/?q=' + address.replace(' ', '+')
    
    # Response
    response = requests.get(url)
    return json.loads(response.text)

get_geocoded_object_photon("1600 Amphitheatre Pkwy, Mountain View, CA")


# ## Geopy Module
# 
# The Geopy Module makes it easy to try a number of different geocoding APIs using the same syntax. It is updated frequently so it is also a good way to keep abreast of the popular geocoding services.
# 
# You can read Geopy's Documentation here: https://geopy.readthedocs.org/en/1.10.0/#. 
# 
# We will use Geopy to geocode addresses with the Google Geocoding Service.

# ### Google Geocoding API
# 
# The Google Geocoder and is extremely popular. It is very accurate for two reasons. It has a robust and sophisticated address parser **and** a great reference database of streets, parcels, and properties. However, it limits you to **2,500** free address geocodes per day. Moreover, you need to read the [Google Geocoder terms of use](https://developers.google.com/maps/documentation/geocoding/usage-limits) to make sure that you do not violate them.  

# #### Test out response object

# In[ ]:

# Create a geocoding object
google_geocoder = geopy.geocoders.GoogleV3()

# Geocode one address with this geocoder
response = google_geocoder.geocode("1600 Amphitheatre Pkwy, Mountain View, CA", google_geocoder) 
type(response)


# #### Navigating the response object
# 
# What is a Location type? 
# 
# Experiment to see if has .keys() method or can be navigated using an index, etc response[0]. 

# In[ ]:

# response.keys()

response[0]
response[1]
response[1][0]
response[1][1]


# #### Write function that only returns latitude & longitude

# In[ ]:

def get_coords_geopy(address, geocoder_instance):
    response = geocoder_instance.geocode(address) 
    lat_lon = response[1][0], response[1][1]
    return lat_lon

# Now try it
coords = get_coords_geopy("1600 Amphitheatre Pkwy, Mountain View, CA", google_geocoder)
coords


# ## Looping through a list of addresses from a text file

# ### Load csv data into pandas DataFrame. 

# In[ ]:

bart = pd.read_csv("data/bartstations.csv")
type(bart)
bart.keys()
 


# ### Quick Dip into Pandas
# 
# Pandas in 10 minutes: http://pandas.pydata.org/pandas-docs/stable/10min.html

# In[ ]:

bart['weekday_visitors'] = 1000*bart.index
bart['weekend_visitors'] = 2000*bart.index
bart['weekly_visitors'] = bart['weekday_visitors'] + bart['weekend_visitors']
bart


# ### Apply upper function to each address using .apply()

# In[ ]:

one_address = "1245 Broadway, Oakland, CA 94612"
one_address_caps = one_address.upper()

bart['address_in_CAPS'] = bart['address'].apply(lambda x: x.upper())
bart


# ### Pass addresses through get_coords_geopy function

# In[ ]:

google_geocoder = geopy.geocoders.GoogleV3()
bart['latitude'], bart['longitude'] = zip(*bart['address'].apply(lambda x: get_coords_geopy(x, google_geocoder)))

bart[['station_name', 'latitude', 'longitude']]


# ## Working with GEOJSON/ Mapping your geocoded addresses
# The following code creates the bart_coords.geojson and bart_coords.js files in the map/geojson folder. bart_coords.js is used by map/bartmap.html for our mapping of BART stations. 
# 
# ### First try opening map/bart_map.html, which will be blank. 

# ### Create a feature for each row of data and push into geo_data object. 

# In[ ]:

geo_data = {
    'type': 'FeatureCollection', 
    'features': []
}

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


# ### Create bart_coords.js file 

# In[ ]:

with open('map/geojson/bart_coords.geojson', 'r') as infile:
    lines = infile.readlines()

    with open('map/geojson/bart_coords.js', 'w') as outfile:
        outfile.write('var bart = ')
        outfile.writelines(lines)

infile.close()
outfile.close()


# ### Now open map/bart_map.html. Your spreadsheet of text addresses have now been geocoded and mapped!

# In[ ]:




# # Batch Geocoding with the Census Geocoder API
# 
# The Census Geocoding API provides a great, free service for geocoding US street addresses. You can read about the Census Geocoder and test it using the online interface at http://geocoding.geo.census.gov/geocoder. Note, the online geocoding interface allows one to geocode up to 1000 addresses at a time without programming via a file upload utility.  Below we show you how to programmatically access the [Census Geocoding API](http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html). 
# 
# ### The good stuff:
# - There are no restrictions on the number of addresses you can geocode or what you can do with the results.
# - You can submit a file of up to 1000 addresses to geocode at a time. This is called **batch geocoding**.
# 
# ### The bad stuff:
# - The geocoding results will not be as good as what you get with the Google Geocoder. But for most applications it is good enough.
# - You are limited to US addresses.
# 
# ### Address format:
# The Census Geocding API requires addresses to be in a strict format:
# - no header row
# - the first column must contain a unique id
# - the id is followed by comma separated values for street address, city, state, and zip
#     - if any component is missing a comma must still be used to separate address components
# - example:
# <pre>
# 1,409 Main St,Oakland,CA,94605
# 2,310 Main St,,CA,94605
# </Pre>
# 
# **Note:** The id column can contain any unique value, for example a place name rather than a numeric id.
# - example:
# <pre>
# house 1,409 Main St,Oakland,CA,94605
# house 2,310 Main St,,CA,94605
# </Pre>

# ### Read in file of addresses to geocode with the Census Geocoder

# In[ ]:

# Identify the file with the addresses in the format required by the geocoder.
# Take a look at the contents of this file to see how these are structured.
cgfile = 'data/bart_addresses_census_format.csv'

# Configure API parameters
# You can read about them here: http://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
url = 'http://geocoding.geo.census.gov/geocoder/geographies/addressbatch'
payload = {'benchmark':'Public_AR_Current','vintage':'ACS2013_Current'}
files = {'addressFile': (cgfile, open(cgfile, 'rb'), 'text/csv')}

# Submit the file of addresses to geocode
r = requests.post(url, files=files, data = payload)

# Review the output
print (r.text)


# ### Save geocoded output to file
# 

# In[ ]:

# Save geocoded data to file
with open('data/bart_geocoded_addresses_from_census.csv', 'w') as outfile:
    outfile.writelines(r.text)
outfile.close()


# ### Read geocoded data back in to do any post processing
# When we do this we will add header rows as there were none in the Census Geocoder output.

# In[ ]:

# Read geocoded data into pandas data frame
colnames = ['station_name','inaddr','ismatch','matchtype','maddr','lon_lat','tlid','sideofst','fipstate','fipcounty','fiptract','junk']
bart_geocoded = pd.read_csv('data/bart_geocoded_addresses_from_census.csv',sep=",", header=None)
bart_geocoded.columns = colnames
bart_geocoded
del bart_geocoded['junk'] #delete junk column at end of file
bart_geocoded


# In[ ]:

# Subset data frame to select only matched addresses
bart_geocoded_match = bart_geocoded.loc[bart_geocoded['ismatch']== 'Match']


# In[ ]:

# Reformat and create a new data frame that we can map
data = {'station': bart_geocoded_match['station_name'], 
        'longitude': bart_geocoded_match['lon_lat'].str.split(',', expand=True)[0],
        'latitude': bart_geocoded_match['lon_lat'].str.split(',', expand=True)[1],
        'address': bart_geocoded_match['maddr']
       }
bart.df = pd.DataFrame(data, columns = ['station', 'longitude', 'latitude','address'])
bart.df


# ## Exercise: 
# Use the mapping code from the Google Geocoder section above to create a map using the census geocoder results.

# In[ ]:

# Your code here to create the geojson data


# Now save the geojson data to a file
with open('map/geojson/bart_coords2.geojson', 'w') as f:
    json.dump(geo_data, f, indent=2)


# In[ ]:

# Read in the geojson data and write it out to a javascript file so we can map it
with open('map/geojson/bart_coords2.geojson', 'r') as infile:
    lines = infile.readlines()

    with open('map/geojson/bart_coords2.js', 'w') as outfile:
        outfile.write('var bart = ')
        outfile.writelines(lines)

infile.close()
outfile.close()


# ### Now open the Census geocoded map/bart_map2.html. 
# Your spreadsheet of text addresses have now been geocoded and mapped!

# In[ ]:



