import json
import urllib.request
import urllib.parse
import googlemaps
import os
from pyproj import Proj
import math
import imageio
import sys

from secrets import GOOGLE

# place_id finder:  https://developers.google.com/maps/documentation/javascript/examples/places-placeid-finder?hl=en

key = "&key=" + GOOGLE

# Amherst Center -> Boston Logan
#data = urllib.parse.urlencode(
#    {"origin": "place_id:ChIJH79CLPbN5okRjKnQ15YCBnc", 
#    "destination": "place_id:ChIJN0na1RRw44kRRFEtH8OUkww", 
#    "key": GOOGLE})

# Bookmill -> Hanover, NH
#data = urllib.parse.urlencode(
#    {"origin": "place_id:ChIJy1BF_D0u4YkRXGF6np16qBo", 
#    "destination": "place_id:ChIJ5cyscCK3tEwRT_DsE-vcGn8", 
#    "key": GOOGLE})

# noho -> portland, me
#data = urllib.parse.urlencode(
#    {"origin": "place_id:ChIJBSqOfD7X5okRC9vYEwt1FsM", 
#    "destination": "place_id:ChIJLe6wqnKcskwRKfpyM7W2nX4", 
#    "key": GOOGLE})

# logan -> portland, me
#data = urllib.parse.urlencode(
#    {"origin": "place_id:ChIJN0na1RRw44kRRFEtH8OUkww", 
#    "destination": "place_id:ChIJLe6wqnKcskwRKfpyM7W2nX4", 
#    "key": GOOGLE})

# noho -> kemptville
#data = urllib.parse.urlencode(
#    {"origin": "place_id:ChIJBSqOfD7X5okRC9vYEwt1FsM", 
#    "destination": "place_id:ChIJv2UXCyTAzUwRJqBkNxooId8", 
#    "key": GOOGLE})

# noho -> montreal
#data = urllib.parse.urlencode(
#    {"origin": "place_id:ChIJBSqOfD7X5okRC9vYEwt1FsM", 
#    "destination": "place_id:ChIJDbdkHFQayUwR7-8fITgxTmU", 
#    "key": GOOGLE})

# montreal -> kemptville
#data = urllib.parse.urlencode(
#    {"origin": "place_id:ChIJDbdkHFQayUwR7-8fITgxTmU", 
#    "destination": "place_id:ChIJv2UXCyTAzUwRJqBkNxooId8", 
#    "key": GOOGLE})

# logan -> somerville, via south station|museum  of fine arts|lowell
data = urllib.parse.urlencode(
    {"origin": "place_id:ChIJN0na1RRw44kRRFEtH8OUkww", 
    "destination": "place_id:ChIJZeH1eyl344kRA3v52Jl3kHo",
    "waypoints": "via:place_id:ChIJW46859l744kR1Wn6zpu-oPU|via:place_id:ChIJS3rn5w1644kRZNWVxNY_Ay8|via:place_id:ChIJP00s4kmk44kRa5ZSf3715d0",
    "key": GOOGLE},
    safe=":|") 

DownLoc = "data-raw/logan_somerville"


def distance_cart(p1, p2):
    return( math.sqrt((p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1])))

def dir_cart(p1, p2):
    if p1[0]-p2[0] == 0:
        return math.degrees(math.pi/2.0)
    else:
        return( math.degrees(math.atan((p1[1]-p2[1]) / (p1[0]-p2[0]))))

# https://andrewpwheeler.com/2018/04/02/drawing-google-streetview-images-down-an-entire-street-using-python/
def MetaParse(MetaUrl):
    response = urllib.request.urlopen(MetaUrl)
    jsonRaw = response.read()
    jsonData = json.loads(jsonRaw)
    #return jsonData
    if jsonData['status'] == "OK":
        if 'date' in jsonData:
            return (jsonData['date'],jsonData['pano_id']) #sometimes it does not have a date!
        else:
            return (None,jsonData['pano_id'])
    else:
        return (None,None)


PrevImage = [] #Global list that has previous images sampled, memoization kindof        
        
def GetStreetLL(Lat,Lon,Head,File,SaveLoc):
    base = r"https://maps.googleapis.com/maps/api/streetview"
    size = r"?size=640x640&location="
    end = str(Lat) + "," + str(Lon) + "&heading=" + str(Head) + key
    MyUrl = base + size + end
    fi = f"{File}.jpg"
    MetaUrl = base + r"/metadata" + size + end
    #print MyUrl, MetaUrl #can check out image in browser to adjust size, fov to needs
    met_lis = list(MetaParse(MetaUrl))                           #does not grab image if no date
    if (met_lis[1],Head) not in PrevImage and met_lis[0] is not None:   #PrevImage is global list
        urllib.request.urlretrieve(MyUrl, os.path.join(SaveLoc,fi))
        met_lis.append(fi)
        PrevImage.append((met_lis[1],Head)) #append new Pano ID to list of images
    else:
        met_lis.append(None)
    return met_lis  


# https://stackoverflow.com/questions/15380712/how-to-decode-polylines-from-google-maps-direction-api-in-php
def decode_polyline(polyline_str):
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']: 
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index+=1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates



with urllib.request.urlopen(f"https://maps.googleapis.com/maps/api/directions/json?{data}") as f:
    result = json.load(f)


coord=[]

# decode the retreived polylines, capturing each in a list of tuples
# coord contains a list of lists, each of which has the tuples for the
# steps
for i in range (0, len (result["routes"][0]["legs"][0]["steps"])):
    points1 = result["routes"][0]["legs"][0]["steps"][i]["polyline"]["points"]
    if (points1 is not None):
        coord.append(decode_polyline(points1))


cc=[]
cce=[]
k = 0
p = Proj(proj="utm", zone=18, ellps="WGS84")

for i in range (0, len(coord)):
    for j in range(0, len(coord[i])):
        cc.append(coord[i][j])
        lat=coord[i][j][0]
        long=coord[i][j][1]

        x, y = p(lat, long)
        cce.append([x,y])

res = []
res_dir=[]

p0 = cce[0]
res.append(p0)
temp = 0
prev = p0
distance_max=250
for i in range (1, len(cce)):
    temp += distance_cart(cce[i], prev)
    if (temp > distance_max):
        res.append(cce[i])
        res_dir.append(dir_cart(cce[i], prev))
        temp = 0
        prev = cce[i]
        res.append(cce[len(cce)-1])
        res_dir.append(dir_cart(cce[len(cce)-1], prev))

# download
for ct, i in enumerate(res):
    lat, lon = p(i[0], i[1], inverse=True)
    for h in [0, 90, 180, 270]:
        temp = GetStreetLL(Lat=lat, Lon=lon, Head=h, File=f"image-{ct}_head-{h}", SaveLoc=DownLoc)

