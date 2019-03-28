#!/usr/bin/env python

'''
saddle_endurance_anls.py

Determine length of time segments continuiously seated--that is, in between
standing periods for relieving saddle fatigue.


'''
import os
import sys


# analysis inputs
FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
            + r'2019-03-22-09-57-00.fit'
ConfigFile=None
OutStream=sys.stdout


def FwdRunningMinimum( x, wBeg=1, wEnd=8 ):
    '''
    Like it says, a forward running minimum
    over a future boxcar i+wBeg through i+wEnd
    '''
    from numpy import zeros
    nPts = len(x)
    run_min = zeros(nPts)
    for i in range(nPts-3):
        iBeg = i+wBeg
        iEnd = i+wEnd+1 if i<nPts-wEnd-1 else nPts
        run_min[i] = min( x[iBeg:iEnd] )
    run_min[-3] = x[-1]
    run_min[-2] = x[-1]
    run_min[-1] = x[-1]
    return run_min
# end FwdRunningMinimum()


############################################################
#           saddle_endurance_anls function def             #
############################################################
from activity_tools import FindConfigFile

#def saddle_endurance_anls(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

(FilePath, FitFileName) = os.path.split(FitFilePath)

# no config file needed

from datetime import datetime
from fitparse import Activity
from activity_tools import extract_activity_signals
import numpy as np


required_signals    = [ 'power', 'cadence' ]

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

SampleRate  = 1.0
cadence     = signals['cadence']
nPts        = len(cadence)

cad_fwd_min_3_8 = FwdRunningMinimum( cadence, wBeg=3, wEnd=8 )
cad_fwd_min_1_8 = FwdRunningMinimum( cadence, wBeg=1, wEnd=8 )

STANDING    = 0
SEATED      = 1
state       = STANDING

CThr    = 40.0
seated_state    = np.zeros(nPts)

for i in range(nPts):
    if state==STANDING:
        if cadence[i]>=CThr and cad_fwd_min_1_8[i]>=CThr:
            state   = SEATED
    else: # state==SEATED:
        if cadence[i]< CThr and cad_fwd_min_3_8[i]<CThr:
            state   = STANDING
    seated_state[i] = state


############################################################
#                  plotting                                #
############################################################

# time plot with heart rate
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.dates import date2num, DateFormatter
import datetime as dt
base = dt.datetime(2014, 1, 27, 0, 0, 0)
x = [ base + dt.timedelta(seconds=t) for t in signals['time'] ]
x = date2num(x) # Convert to matplotlib format
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, sharex=True)
ax0.plot_date( x, signals['power'], 'b-', linewidth=1 );
ax0.grid(True)
ax0.set_ylabel('power, W')
ax1.plot_date( x, signals['cadence'],   'g-', linewidth=1 );
ax1.plot_date( x, cad_fwd_min_3_8,      'm-', linewidth=1 );
ax1.plot_date( x, cad_fwd_min_1_8,   'brown', linestyle='-', linewidth=1 );
ax1.grid(True)
ax1.set_ylabel('cadence, RPM')
ax1.legend(['cadence', 'cad_fwd_min_3_8', 'cad_fwd_min_1_8'],
            loc='upper left');
ax2.plot_date( x, seated_state, 'r-', linewidth=3 );
ax2.grid(True)
ax2.set_ylabel('seated')
fig.tight_layout()
fig.subplots_adjust(hspace=0)   # Remove horizontal space between axes

#fig1, ax1 = plt.subplots(nrows=1, sharex=True)
#ax1.plot_date( x, power,        'k-', linewidth=1 );
#ax1.plot_date( x, fboxpower,    'm-', linewidth=1);
#ax1.plot_date( x, cp2,          'r.', markersize=4);
#ax1.plot_date( x, cboxpower,    'b-', linewidth=1);
#ax1.plot_date( x, zone_mid,     'g-', linewidth=3);
#ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
#ax1.set_yticks( p_zone_bounds, minor=False)
#ax1.grid(True)
#ax1.set_title('power, watts')
#fig1.autofmt_xdate()
#ax1.legend(['power', 'FBoxCar', 'cp2', 'CBoxCar', 'zone mid'],
#            loc='upper left');
#fig1.suptitle('Power Zone Detection', fontsize=20)
#fig1.tight_layout()
#fig1.canvas.set_window_title(FitFilePath)

plt.show()

#def ClosePlots():
#    plt.close('all')
#
#return ClosePlots
#
## end zone_detect()
