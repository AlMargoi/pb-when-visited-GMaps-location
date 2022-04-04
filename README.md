## Table of contents:
* [Description](#Description)
* [How to](#How-to)

<br>

## Description
This project was born from my personal need to see when exactly I have visited certain locations.
I have Google Maps following almost all my moves and I use it as some sort of journal. However, when it comes to specific location visits, it can only show you (not always) the last visit. There is no option (that I know of) to show all the dates and timestamps of all my visits to a certain location.

For example: I have a bouldering 10x entries offer taken with a bouldering gym. I might need to know on which dates and how many times did I visit the gym, so that I can know how many entries I still have left.

### How it works:
* You export all your Google Maps data in JSON format
* You run the script and input:
    * The interest location's coordinates
    * A radius (in meters) in whithin which we will consider a visit (higher radius might give false positives, lower radius might give false negatives)
* The script will output the dates where it considers a visit. You can double check then using your Google Maps timeline

### NOTE:
The script only uses the coordinates in the Google Maps JSON files. For greater accuracy, like "passing by" certain coordinates, some specific hashes inside these JSON files need to be converted to coordinates. This can be done using the Google Maps API, but because these API calls cost money, we will not use this feature. This might be included in future release. 

<br>

## How to
To get started, before running the script, please make sure you:
* [Install Python](https://www.python.org/downloads/) 3.10.1 or later 
* Install required modules:
```
$ pip install pandas, progress
```
* Export your Google Maps Data in JSON format. You will end up with one JSON file for each month. Naming of the files should be '[year]_[MONTH].json' (e.g. 2022_APRIL.json). Please keep the naming convention. 
* Place the JSON files in the '.\GMapsJSONFiles' folder, which should be located in the same place with the Python file, and which should coincide with the invocation location
* Run the script from that location and input the required coordinates in decimal format
```
$ python.exe .\InspectGMapsJson.py
Please enter your Latitude in the decimal format: 63.998476353740024
Please enter your Longitude in the decimal format: -22.623755867434134
Please enter desired accuracy (search circle radius) in meters (e.g. 100 / 200 / 1000 / etc): 500
Range: 258m   Visit between 2021-08-20T11:25:48.881Z - 2021-08-20T15:31:46.237Z
Range: 219m   Visit between 2021-08-20T15:43:12.855Z - 2021-08-20T17:03:08Z
Range: 237m   Visit between 2021-09-02T05:03:00.050Z - 2021-09-02T05:45:43.010Z
```