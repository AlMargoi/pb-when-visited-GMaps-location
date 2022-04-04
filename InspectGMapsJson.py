from math import sin, cos, acos, atan2, fabs, sqrt, pi
from datetime import datetime
import pandas as pd
from progress.bar import Bar
import re
import os
import time
import logging

logging.basicConfig(level = logging.DEBUG)
# Set to logging.WARNING (default) 

def get_coordinates(timelineObj):
    # Extracts coordinates from timelineObject objects
    # timelineObject = object stored in Google Maps Timeline JSON
    if 'placeVisit' in timelineObj.keys():
        try:
            coords = [timelineObj['placeVisit']['location']]
            if 'latitudeE7' not in coords[0].keys():
                # Drop item if coordinates are not in ['location'] object
                return 0
        except KeyError:
            # Some placeVisit data do not contain coordinates
            # Since these are a minority, they will be ignored
            return 0
        except Exception as err:
            print(type(err))
            print(err)
    elif 'activitySegment' in timelineObj.keys():
        coords = [timelineObj['activitySegment']['startLocation']]
        coords.append(timelineObj['activitySegment']['endLocation'])
        if 'waypointPath' in timelineObj['activitySegment'].keys():
            for waypoint in timelineObj['activitySegment']['waypointPath']['waypoints']:
                coords.append({
                    'latitudeE7': waypoint['latE7'],
                    'longitudeE7': waypoint['lngE7']
                })
        if 'transitPath' in timelineObj['activitySegment'].keys():
            for transitStop in timelineObj['activitySegment']['transitPath']['transitStops']:
                coords.append({
                    'latitudeE7': transitStop['latitudeE7'],
                    'longitudeE7': transitStop['longitudeE7']
                })
        if 'simplifiedRawPath' in timelineObj['activitySegment'].keys():
            for point in timelineObj['activitySegment']['simplifiedRawPath']['points']:
                coords.append({
                    'latitudeE7': point['latE7'],
                    'longitudeE7': point['lngE7']
                })
    return coords


def get_date(timelineObj):
    # Extracts date data from timelineObject
    # Returns {startTimestamp, endTimestamp}
    if "placeVisit" in timelineObj.keys():
        date = timelineObj["placeVisit"]["duration"]
        return date
    elif "activitySegment" in timelineObject.keys():
        date = timelineObject["activitySegment"]["duration"]
        return date
    else:
        return "UnknownDate"


def get_coord_distance(latitude1, longitude1, latitude2, longitude2):
    # Calculate distance between points (in meters), for accuracy purposes.
    # Math taken from: https://www.movable-type.co.uk/scripts/latlong.html
    R = 6371 * 1e3 #constant radius of earth in km:
    delta_lat_rad = abs(latitude1 - latitude2) * pi / 180
    delta_long_rad = abs(longitude1 - longitude2) * pi / 180
    latitude1_rad = latitude1 * pi / 180
    latitude2_rad = latitude2 * pi / 180
    a = (sin(delta_lat_rad/2))**2 + cos(latitude1_rad)*cos(latitude2_rad)*(sin(delta_long_rad/2))**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    d = R * c
    return int(d)


def prompt_user(message, condition, warning, returnType="str"):
    prompt = True
    while prompt == True:
        user_input = float(input(message))
        if eval(condition):
            prompt = False
            try:
                if returnType == "int":
                    return int(user_input)
                elif returnType == "float":
                    return float(user_input)
                else:
                    return str(user_input)
            except ValueError as error:
                print(f"[!] Invalid input: {error}")
                prompt = True
        else:
            print(warning)



# Ask for input:
location_latitude = float(prompt_user(message="Please enter your Latitude in the decimal format: ",
                                        condition = "-90 <= user_input and user_input <= 90 ",
                                        warning="[!] Warning: Latitude accepted range is [-90, 90]",
                                        returnType = float))
location_longitude = float(prompt_user(message="Please enter your Longitude in the decimal format: ",
                                        condition = "-180 <= user_input and user_input <= 180 ",
                                        warning="[!] Warning: Longitude accepted range is [-180, 180]",
                                        returnType = float))
location_latitudeE7 = location_latitude * 10**7
location_longitudeE7 = location_longitude * 10**7
threshold = float(prompt_user(message="Please enter desired accuracy (search circle radius) in meters (e.g. 100 / 200 / 1000 / etc): ",
                                        condition = "0 < user_input and user_input < 100000 ",
                                        warning="[!] Warning: Accuracy accepted range is [0, 100000]",
                                        returnType = float))


# Build the array of JSON files in current directory:
# Match Google Maps json naming format to avoid unwanted files.
JSON_files = []
JSON_folder = '.\GMapsJSONFiles'
for file in os.listdir(JSON_folder):
    regex_filter = "^[0-9]{4}_(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)?\.json$"
    if file.endswith(".json") and re.search(regex_filter, file):
        JSON_files.append(f"{JSON_folder}\\" + file)

numberof_keyErrors = 0
attempts = 0
when_visited_location = []
with Bar("Working on it...", max=len(JSON_files)) as progress_bar:
    for file in JSON_files:
        #print(f">>>>> processing {file}")
        try:
            current_JSON = pd.read_json(file)
            for timelineObject in current_JSON['timelineObjects']:
                attempts += 1
                coordinates_list = get_coordinates(timelineObject)
                if coordinates_list == 0:
                    # Skip current iteration if we couldn't get coordinates properly
                    continue 
                for coordinates in coordinates_list:
                    distance = get_coord_distance(coordinates['latitudeE7'] / 1e7, coordinates['longitudeE7'] / 1e7,
                                                    location_latitudeE7 / 1e7, location_longitudeE7 / 1e7)
                    condition = (distance <= threshold)
                    if condition:
                        obj_to_append = get_date(timelineObject)
                        obj_to_append['distance'] = str(distance) + "m"
                        when_visited_location.append(obj_to_append)
        except KeyError as err:
            # KeyErrors are acceptable occasionally, as long as occurences are neglectible
                numberof_keyErrors += 1
        except Exception as err:
            print(f"[Error]: {type(err)}: {err}")
        progress_bar.next()


# Make sure the output data is sorted:
when_visited_location.sort(key=lambda x: datetime.strptime(x['startTimestamp'].replace('Z','').split('.')[0], "%Y-%m-%dT%H:%M:%S"))

# Use previous_print to not print same visit 2 times:
previous_print = ""
for visit in when_visited_location:
    if f"Range: {visit['distance'].ljust(6)} Visit between {visit['startTimestamp']} - {visit['endTimestamp']}" != previous_print:
        print(f"Range: {visit['distance'].ljust(6)} Visit between {visit['startTimestamp']} - {visit['endTimestamp']}")
        previous_print = f"Range: {visit['distance'].ljust(6)} Visit between {visit['startTimestamp']} - {visit['endTimestamp']}"
    else:
        previous_print = f"Range: {visit['distance'].ljust(6)} Visit between {visit['startTimestamp']} - {visit['endTimestamp']}"


try:
    keyErrorPercentage = str(numberof_keyErrors * 100 / attempts)[0:5] + "%"
except ZeroDivisionError:
    keyErrorPercentage = f"{numberof_keyErrors} (total)"

logging.debug(f"KeyError ratio (to be inspected if > 1%): {keyErrorPercentage}")
