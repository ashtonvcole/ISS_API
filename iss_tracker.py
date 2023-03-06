#!/usr/bin/env python3

from flask import Flask, request
import requests
import xmltodict
from geopy.geocoders import Nominatim
import math
import time



app = Flask(__name__)
MEAN_EARTH_RADIUS = 6371
data = None # Defined below



def get_data() -> dict:
    """Get the most recent ISS OEM data.

    This function accesses the most recent Orbital Ephemeris Message for the
    International Space Station available on the NASA website. It parses the
    XML file into a dictionary.

    Args:
        None

    Returns:
        A dictionary of nested lists and dictionaries corresponding to the
            entries in the XML file.
    """
    return xmltodict.parse(requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml').text)



@app.route('/', methods = ['GET'])
def all() -> dict:
    """ Get all data.

    This function returns the entire contents of the most recent Orbital
    Ephemeris Message for the International Space Station.

    Args:
        None

    Returns:
        A dictionary of nested lists and dictionaries corresponding to the
            entries in the XML file. If there is an error, a descriptive
            string will be returned with a 404 status code.
    """
    global data
    if data == None:
        return f'Empty data set\n', 404
    return data



@app.route('/epochs', methods = ['GET'])
def epochs() -> list:
    """Get data for all epochs.

    This function returns a list of all of the epochs within the most recent
    Orrbital Ephemeris Message for the International Space Station.

    Args:
        None

    Returns:
        A list of dictionaries corresponding to the entries in the XML file.
            If there is an error, a descriptive string will be returned with
            a 404 status code.
    """
    global data
    if data == None:
        return f'Empty data set\n', 404
    limit = request.args.get('limit', len(data['ndm']['oem']['body']['segment']['data']['stateVector']))
    offset = request.args.get('offset', 0)
    try:
        limit = int(limit)
        offset = int(offset)
    except:
        return f'Parameters limit and offset must be integers\n', 404
    epochs = []
    i = 0
    count = 0
    for stateVector in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if count >= limit:
            break
        elif i >= offset:
            epochs.append(stateVector['EPOCH'])
            count += 1
        i += 1
    return epochs



@app.route('/epochs/<string:epoch>', methods = ['GET'])
def epochs_state(epoch: str) -> dict:
    """Get state vectors for a specified epoch.

    This function takes in a string representing the desired epoch. If an
    exact match is found in the data set, its state vector is returned.
    Otherwise, the user is given a 404 error.

    Args:
        String representing the desired epoch.

            YYYY-DDDTHH:MM:SS.000Z, or in URL-friendly form
            YYYY-DDDTHH%3AMM%3ASS%2E000Z

    Returns:
        A dictionary of the entire state vector, i.e. EPOCH, X, Y, Z, X_DOT,
        Y_DOT, and X_DOT. If there is an error, a descriptive string will be
        returned with a 404 status code.
    """
    global data
    if data == None:
        return f'Empty data set\n', 404
    for item in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if item['EPOCH'] == epoch:
            return item
    else: # No matching epoch
        return f'Epoch {epoch} not found\n', 404



@app.route('/epochs/<string:epoch>/speed', methods = ['GET'])
def epochs_speed(epoch: str) -> dict:
    """Get speed for a specified epoch.

    This function takes in a string representing the desired epoch. If an
    exact match is found in the data set, its calculated speed is returned.
    Otherwise, the user is given a 404 error.

    Args:
        String representing the desired epoch.

            YYYY-DDDTHH:MM:SS.000Z, or in URL-friendly form
            YYYY-DDDTHH%3AMM%3ASS%2E000Z

    Returns:
        A dictionary of the speed in the following form.

            {"speed" : 0, "units" : "km/s"}

        If there is an error, a descriptive string will be
        returned with a 404 status code.
    """
    global data
    if data == None:
        return f'Empty data set\n', 404
    for item in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if item['EPOCH'] == epoch:
            return {'value' : (float(item['X_DOT']['#text']) ** 2 + \
                    float(item['Y_DOT']['#text']) ** 2 + \
                    float(item['Z_DOT']['#text']) ** 2) ** 0.5, \
                    'units' : item['X_DOT']['@units']}
    else: # No matching epoch
        return f'Epoch {epoch} not found\n', 404



@app.route('/epochs/<string:epoch>/location', methods = ['GET'])
def epochs_location(epoch: str) -> dict:
    """Get location for a specified epoch.

    This function takes in a string representing the desired epoch. If an
    exact match is found in the data set, its calculated location is returned.
    Otherwise, the user is given a 404 error.

    Args:
        String representing the desired epoch.

            YYYY-DDDTHH:MM:SS.000Z, or in URL-friendly form
            YYYY-DDDTHH%3AMM%3ASS%2E000Z

    Returns:
        A dictionary showing the closest identifiable location to the ISS's
        ground track at a given epoch, as well as the latitude, longitude,
        altitude, and speed. If there is an error, a descriptive string will
        be returned with a 404 status code. If the ISS is not close to
        anything, such as when its over the ocean, the location value will be
        set to None.
    """
    global data, MEAN_EARTH_RADIUS
    if data == None:
        return f'Empty data set\n', 404
    for item in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if item['EPOCH'] == epoch:
            x = float(item['X']['#text'])
            y = float(item['Y']['#text'])
            z = float(item['Z']['#text'])
            hrs = int(item['EPOCH'][9:11])
            mins = int(item['EPOCH'][12:14])
            lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
            lon = math.degrees(math.atan2(y, x)) \
                    - ((hrs-12.0)+(mins/60.0))*(360.0/24.0) + 24.0
            alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
            geocoder = Nominatim(user_agent = 'iss_tracker')
            geoloc = geocoder.reverse((lat, lon), zoom = 15, language = 'en')
            to_return = {}
            to_return['closest_epoch'] = item['EPOCH']
            to_return['seconds_from_now'] = 0
            to_return['location'] = {}
            to_return['location']['latitude'] = lat
            to_return['location']['longitude'] = lon
            to_return['location']['altitude'] = {}
            to_return['location']['altitude']['value'] = alt
            to_return['location']['altitude']['units'] = item['X']['@units']
            if geoloc == None:
                to_return['location']['geo'] = None
            else:
                to_return['location']['geo'] = geoloc.raw
            to_return['speed'] = epochs_speed(epoch)
            return to_return
    else: # No matching epoch
        return f'Epoch {epoch} not found\n', 404



@app.route('/now', methods = ['GET'])
def now() -> dict:
    """Get location for the current epoch.

    This function returns the location of the ISS at the closest recorded
    epoch. It provides the difference between this time and now in seconds.

    Args:
        None

    Returns:
        A dictionary showing the closest identifiable location to the ISS's
        ground track at a given epoch, as well as the latitude, longitude,
        altitude, and speed. If there is an error, a descriptive string will
        be returned with a 404 status code. If the ISS is not close to
        anything, such as when its over the ocean, the location geo value
        will be set to None.
    """
    global data, MEAN_EARTH_RADIUS
    time_now = time.time()
    min_item = None
    min_difference = float('inf')
    if data == None:
        return f'Empty data set\n', 404
    for item in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        time_epoch = time.mktime(time.strptime( \
                item['EPOCH'][:-5], '%Y-%jT%H:%M:%S'))
        difference = time_now - time_epoch
        if abs(difference) < abs(min_difference):
            min_item = item
            min_difference = difference
    to_return = epochs_location(min_item['EPOCH'])
    to_return['seconds_from_now'] = min_difference
    return to_return



@app.route('/delete-data', methods = ['DELETE'])
def delete_data() -> str:
    """Clear API data.

    This function removes all stored data from the app instance.

    Args:
        None

    Returns:
        A string confurming that the data has been deleted.
    """
    global data
    data = None
    return 'Data deleted from instance\n'



@app.route('/post-data', methods = ['POST'])
def post_data() -> str:
    """Refresh API data.

    This function retrieves the latest ISS position data from the NASA
    website using get_data(). It overwrites the existing data set. Note that
    this API only retrieves and stores data when the Flask server instance
    is initialized, so this call is necessary if the user wants up-to-date
    information.

    Args:
        None

    Returns:
        A string confirming that the data has been refreshed.
    """
    global data
    data = get_data()
    return 'Data refreshed\n'



@app.route('/comment', methods = ['GET'])
def comment() -> list:
    """Get comment object from data.

    Args:
        None

    Returns:
        A list of all of the comments included in the OEM. If there is an
        error, a descriptive string will be returned with a 404 status code.
    """
    global data
    if data == None:
        return f'Empty data set\n', 404
    return data['ndm']['oem']['body']['segment']['data']['COMMENT']



@app.route('/header', methods = ['GET'])
def header() -> dict:
    """ Get header object from data.

    Args:
        None


    Returns:
        A dictionary of header data included in the OEM. This may include the
        creation date and originator of the file. If there is an error, a
        descriptive string will be returned with a 404 status code.
    """
    global data
    if data == None:
        return f'Empty data set\n', 404
    return data['ndm']['oem']['header']



@app.route('/metadata', methods = ['GET'])
def metadata() -> dict:
    """ Get orbit metadata.

    Args:
        None

    Returns:
        A dictionary of metadata associated with an oriting body. This
        includes the object's identifiers and reference frame. If there is an
        error, a descriptive string will be returned with a 404 status code.
    """
    global data
    if data == None:
        return f'Empty data set\n', 404
    return data['ndm']['oem']['body']['segment']['metadata']



@app.route('/help', methods = ['GET'])
def help() -> str:
    """Returns help description detailing API endpoints.

    Args:
        None

    Returns:
        None
    """
    return 'These are the endpoints of the iss_tracker API.\n' + \
            '\n\nNote that if the data is empty, all GET\n' + \
            'messages will return a string message with a 404\n' + \
            'status.\n\n' + \
            '\t/ GET Return the entire data set in JSON form.\n' + \
            '\t/epochs GET Return a list of all epochs in JSON form.\n' + \
            '\t\tint:limit The maximum number of epochs to return.\n' + \
            '\t\tint:offset What epoch to start from, zero-indexed\n' + \
            '\t/epochs/<int:epoch> GET Return the state vector for\n' + \
            '\t\tan epoch in JSON form. Returns a string error\n' + \
            '\t\tmessage with a 404 status if no such record.\n' + \
            '\t/epochs/<int:epoch>/speed GET Return the instantaneous\n' + \
            '\t\tspeed for an epoch in JSON form. Returns a string\n' + \
            '\t\terror message with a 404 status if no such record.\n' + \
            '\t/delete-data DETETE Clear all data in the instance.\n' + \
            '\t/post-data POST Update and overwrite all data.\n'




data = get_data() # No matter how the app is started, we need to get data

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0') # If interpreted in Python, ensures app is run
