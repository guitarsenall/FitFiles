
'''
shire_map_ride.py
Overlay the ride data on the shire map with the origin of
the ride at Bag End, which is located at (158,67) miles.
'''

BagEnd  = (158,67)

#
# Display the shire map
#

import matplotlib.pyplot as plt
# The image is 1393x874 pixels
# The scale stretches from pixel 41 to 325
scale = 50.0 / (325-41) # miles per pixel
left    = -41*scale
right   = (1393-41)*scale
bottom  = -30*scale
top     = (874-30)*scale
image = plt.imread('shire_map.jpg')


'''
Here is a formula:
    https://stackoverflow.com/questions/27928
        /calculate-distance-between-two-latitude-longitude
        -points-haversine-formula
I think, since this gives distance between two points,
I can use it to acquire a scale in the X and Y directions
(i.e., north-south and east-west) converting semicircles
to miles.
Inputs are in degrees, output in miles
'''
from math import cos, asin, sqrt
def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295     #Pi/180
    a = 0.5 - cos((lat2 - lat1) * p)/2 \
            + cos(lat1 * p) * cos(lat2 * p) \
            * (1 - cos((lon2 - lon1) * p)) / 2
    return 0.6237 * 12742 * asin(sqrt(a))   # km->miles

def sc_to_deg(s):
    # convert semicircles to degrees
    return s * (180.0 / 2**31)

#
# Get the ride data
#
FilePath        = r'D:\Users\Owner\Documents\OneDrive\bike\activities\will\\'
FitFilePath     = FilePath + r'2019-05-03-14-32-49.fit'

from datetime import datetime
from fitparse import Activity
from activity_tools import extract_activity_signals, UnitHandler
activity    = Activity(FitFilePath)
signals     = extract_activity_signals(activity, resample='existing')
ride_lat    = signals['position_lat']
ride_lon    = signals['position_long']

# determine scale factors to convert longitude and latitude to miles
LatSpan = distance( sc_to_deg(ride_lat.min()), sc_to_deg(ride_lon[0]),
                    sc_to_deg(ride_lat.max()), sc_to_deg(ride_lon[0]) )
LonSpan = distance( sc_to_deg(ride_lat[0]), sc_to_deg(ride_lon.min()),
                    sc_to_deg(ride_lat[0]), sc_to_deg(ride_lon.max()) )
LatScale    = LatSpan / ( ride_lat.max() - ride_lat.min() )
LonScale    = LonSpan / ( ride_lon.max() - ride_lon.min() )

# compute travel vectors normalized to first point and starting at Bag End.
ride_east   = LonScale * ( ride_lon - ride_lon[0] ) + BagEnd[0]
ride_north  = LatScale * ( ride_lat - ride_lat[0] ) + BagEnd[1]

#
# create the plot
#
fig, ax = plt.subplots()
ax.imshow(  image, origin='upper',
            extent=(left,right,bottom,top) )
ax.plot( ride_east, ride_north, 'g-', linewidth=2 )
plt.show()

