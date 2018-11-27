# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.
This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.
This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import ssl
import pandas as pd
import argparse
import json
import pprint
import requests
import sys
import urllib
import socket
import urllib.request, urllib.parse, urllib.error
import geocoder
import geopy
import decimal

#Decimal formatter
from decimal import *
getcontext().prec = 8

#reverse location lookup
from geopy import geocoders
from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim

#SSL certificate create
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
geopy.geocoders.options.default_ssl_context = ctx

# .env configuration information
import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#client information stored via .env variale
MY_API_KEY = os.getenv('APIKey') #  Replace this with your real API key
# print(MY_API_KEY)
client = os.getenv('ClientID')

#google api key
GAPI_KEY = os.getenv('GAPIKey')
# print(client)

HOME = "Jersey Ave. Jersey City, NJ."

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


#mySocket connection configuration =========================>
# mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# mySocket.connect((""))
# mySocket.connect(('https://api.yelp.com' , 80))
# mySocket.sendall("GET / HTTP/1.1\r\n\r\n")
# term = input("Please enter yelp search term: ")
# location = input("Please enter search location: ")
# cmd = 'GET https://api.yelp.com/v3/events/{id}'.encode()
# mySocket.send(cmd)
# <============================================================>
Trigger = False
geoQuery = None
input_values = {}
latitude = float(0.00)
longitude = float(0.00)
term = ''
location = ''
count = 0
searchLocation = ''

while term == '':
    term = str(input("Please enter yelp search term: "))
    input_values[term] = term
    count = count + 1
    if input_values[term] == '':
        input_values[term] = input("Sorry I didn't understand that.  Please enter a search term.")

while geoQuery not in {"yes", "no"}:
    response = str(input("Would you like to use your current location?  " + "\n" + "'yes' or 'no':  "))
    geoQuery = response
    if response not in ('yes', 'no'):
        input("Again would you like to use your current location?  Please respond only yes or no:  ")
    elif response == 'yes':
        try:
            GEO = geocoder.ip('me')
            GEOlat = float(GEO.latlng[0])
            input_values[latitude] = GEOlat
            GEOlng = float(GEO.latlng[1])
            input_values[longitude] = GEOlng
            geolocator = GoogleV3(api_key=GAPI_KEY, user_agent="my-application", timeout=30, )
            p1 = "[" + str(GEOlat) + ", " + str(GEOlng) + "]"
            print("p1: ",p1)
            # address, (latitude, longitude) = geolocator.reverse(p1, exactly_one=True, timeout=30, language=None, sensor=True)
            # print(address, latitude, longitude)
            locationGeo = geolocator.reverse(p1, exactly_one=True, timeout=10)
            input_values[location] = locationGeo.address
            input_values[latitude] = locationGeo.latitude
            input_values[longitude] = locationGeo.longitude
            searchLocation = input_values[location]
            print("address: ", locationGeo.address)
            print("lat: ", locationGeo.latitude)
            print("lng: ", locationGeo.longitude)

        except:
            print("Location services failed.  Please enter your location so we may continue.")
            geoQuery = "no"
    else:
        geoQuery = "no"
    if geoQuery == "no":
        while location == '':
            location = str(input("Please enter search location: "))
            input_values[location] = location
            searchLocation = input_values[location]
            # input_values[count] = count + 1
            if input_values[location] == '':
                input_values[location] = input("Sorry I didn't understand that.  Please enter a search location.")
            continue
print("<=============================================================>")
print('')
print('-------------Term----------------')
print('search term: ', input_values[term])
print('')
print('------------Location-------------')
print('location: ',input_values[location])
print('')
# print('--------------Count--------------')
# print('count: ',input_values[count])
# print('')
print("<=============================================================>")
#========================================================================>
#
# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3



# def request(host, path, api_key, url_params=None):
def request(API_HOST, SEARCH_PATH, MY_API_KEY, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    # url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    url = '{0}{1}'.format(API_HOST, quote(SEARCH_PATH.encode('utf8')))

    headers = {
        # 'Authorization': 'Bearer %s' % api_key,
        'Authorization': 'Bearer %s' % MY_API_KEY,

    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)
    
    return response.json()


def search(MY_API_KEY, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
		'sort_by': 'distance',
        # 'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, MY_API_KEY, url_params=url_params)


def get_business(MY_API_KEY, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, MY_API_KEY)


def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(MY_API_KEY, term, searchLocation)

    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} in {1} found.'.format(term, searchLocation))
        return

    business_id = businesses[0]['id']

    print(u'{0} businesses found, querying business info ' \
        'for the top result "{1}" ...'.format(
            len(businesses), business_id))
    response = get_business(MY_API_KEY, business_id)

    print(u'Result for business "{0}" found:'.format(business_id))
    pprint.pprint(response, indent=2)


def main():
    parser = argparse.ArgumentParser()

    # parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
    parser.add_argument('-q', '--term', dest='term', default=term,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        # default=DEFAULT_LOCATION, type=str,
                        default=location, type=str,
                        help='Search location (default: %(default)s)')
    parser.add_argument('-r', '--radius', dest='radius',
                        # default=DEFAULT_LOCATION, type=str,
                        default=10000, type=int,
                        help='Search radius (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        query_api(input_values.term, input_values.location)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )


if __name__ == '__main__':
    main()
    