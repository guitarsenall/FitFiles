
'''
shire_map_ride_anls.py
Overlay the ride data on the shire map with the origin of
the ride at Bag End, which is located at (158,67) miles.
'''

import sys
import os
import numpy as np


############################################################
#              helper functions                            #
############################################################

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


############################################################
#              shire_map_ride_anls function def            #
############################################################

from activity_tools import FindConfigFile

def shire_map_ride_anls(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

    verbose = False

    (FilePath, FitFileName) = os.path.split(FitFilePath)

    if ConfigFile is None:
        ConfigFile = FindConfigFile('', FilePath)
    if (ConfigFile is None) or (not os.path.exists(ConfigFile)):
        raise IOError('Configuration file not specified or found')

    #
    #   Parse the configuration file
    #
    from ConfigParser import ConfigParser
    config      = ConfigParser()
    config.read(ConfigFile)
    print >> OutStream, 'reading config file ' + ConfigFile
    RideScale       = config.getfloat( 'mapping', 'RideScale' )
    print >> OutStream,  'RideScale: ', RideScale

    #
    # get the shire map
    #

    # this needs to stay INSIDE the function or bad things happen
    import matplotlib.pyplot as plt

    # Image and scale properties
    ImSize  = (3661, 2373)      # image size in pixels
    ScaleL  = (  72, 2320)      #  left corner of scale in image coords
    ScaleR  = ( 806, 2313)      # right corner of scale in image coords
    ScaleMi = 50.0              # scale in miles
    BagEndPx= (2410, 1217)      # Bag End location in pixels
    #BagEndPx= (0,0)      # Bag End location in pixels
    scale   = ScaleMi / (ScaleR[0]-ScaleL[0])   # miles per pixel
    #left    = -ScaleL[0]*scale
    #right   =  (ImSize[0]-ScaleL[0])*scale
    #bottom  = -(ImSize[1]-ScaleL[1])*scale
    #top     = ( ImSize[1] - (ImSize[1]-ScaleL[1]) )*scale
    left    = -BagEndPx[0]*scale
    right   = (ImSize[0]-BagEndPx[0])*scale
    bottom  = -(ImSize[1]-BagEndPx[1])*scale
    top     = BagEndPx[1]*scale
    image = plt.imread('shire_map_b.jpg')


    #
    # Get the ride data
    #
    required_signals    = [ 'position_lat',
                            'position_long'   ]

    from datetime import datetime
    from fitparse import Activity
    from activity_tools import extract_activity_signals, UnitHandler
    activity    = Activity(FitFilePath)
    signals     = extract_activity_signals(activity, resample='existing')

    if not all( s in signals.keys() for s in required_signals ):
        msg = 'required signals not in file'
        print >> OutStream, msg
        print >> OutStream, 'Signals required:'
        for s in required_signals:
            print >> OutStream, '   ' + s
        print >> OutStream, 'Signals contained:'
        for s in signals.keys():
            print >> OutStream, '   ' + s
        raise IOError(msg)

    ride_lat    = signals['position_lat']
    ride_lon    = signals['position_long']

    # determine scale factors to convert longitude and latitude to miles
    LatSpan = distance( sc_to_deg(ride_lat.min()), sc_to_deg(ride_lon[0]),
                        sc_to_deg(ride_lat.max()), sc_to_deg(ride_lon[0]) )
    LonSpan = distance( sc_to_deg(ride_lat[0]), sc_to_deg(ride_lon.min()),
                        sc_to_deg(ride_lat[0]), sc_to_deg(ride_lon.max()) )
    LatScale    = LatSpan / ( ride_lat.max() - ride_lat.min() )
    LonScale    = LonSpan / ( ride_lon.max() - ride_lon.min() )

    # compute travel vectors normalized to first point and scaled by RideScale.
    ride_east   = LonScale * ( ride_lon - ride_lon[0] ) * RideScale
    ride_north  = LatScale * ( ride_lat - ride_lat[0] ) * RideScale

    ###########################################################
    ###             plotting                                ###
    ###########################################################

    fig, ax = plt.subplots()
    ax.imshow(  image, origin='upper',
                extent=(left,right,bottom,top) )
    ax.plot( ride_east, ride_north, 'r-', linewidth=3 )
    plt.show()

    def ClosePlots():
        plt.close('all')

    return ClosePlots

# end shire_map_ride_anls()

############################################################
#           main program execution                         #
############################################################
'''
This technique allows the module to be imported without
executing it until one of its functions is called.
'''

if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        print 'command line args: ', sys.argv[1:]
        fitfilepath = sys.argv[1]
        shire_map_ride_anls(fitfilepath, ConfigFile=None)
    else:
        raise IOError('Need a .FIT file')

    #FitFilePath = r'D:\Users\Owner\Documents\OneDrive\bike\activities\will\\' \
    #            + r'2019-05-17-16-02-36.fit'

# SAMPLE OUTPUT:
