#!/usr/bin/env python

'''
force_analysis.py

create two histograms containing pedal-force bins on the X axis
and revolutions and work on the Y axes.
Assume SampleRate = 1 Hz and every data points, regarless of gaps,
is worth one second.

'''

import sys
import os

############################################################
#              plot_heartrate function def                 #
############################################################

from activity_tools import FindConfigFile

def force_analysis(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

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
    CrankRadius     = config.getfloat( 'power', 'CrankRadius' )
    print >> OutStream,  'CrankRadius: ', CrankRadius

    from datetime import datetime
    from fitparse import Activity
    from activity_tools import extract_activity_signals

    required_signals    = [ 'power',
                            'cadence'   ]

    # get the signals
    activity    = Activity(FitFilePath)
    signals     = extract_activity_signals(activity)

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

    time_signal = signals['time']
    power       = signals['power']
    cadence     = signals['cadence']

    # plot the heart rate
    import numpy as np

