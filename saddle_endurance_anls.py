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

SampleRate      = 1.0
cadence         = signals['cadence']
elapsed_time    = signals['time']
nPts            = len(cadence)

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

#
#   Determine seated segment durations
#
iiUp = np.nonzero( seated_state[1:] - seated_state[0:-1] ==  1 )[0]
iiDn = np.nonzero( seated_state[1:] - seated_state[0:-1] == -1 )[0]
if iiUp[-1] < iiDn[-1]:
    seg_durtns  = np.zeros(len(iiDn))
    seg_starts  = np.zeros(len(iiDn)).astype('int')
    seg_stops   = np.zeros(len(iiDn)).astype('int')
else:
    seg_durtns  = np.zeros(len(iiDn)+1)
    seg_starts  = np.zeros(len(iiDn)+1).astype('int')
    seg_stops   = np.zeros(len(iiDn)+1).astype('int')
if iiDn[0] < iiUp[0]:                               # begins seated
    seg_durtns[0]   = iiDn[0]
    seg_starts[0]   = 0
    seg_stops [0]   = iiDn[0]
    if iiUp[-1] > iiDn[-1]:                         #   Ends seated
        seg_durtns[1:-1]    = iiDn[1:] - iiUp[0:-1]
        seg_starts[1:-1]    = iiUp[0:-1]
        seg_stops [1:-1]    = iiDn[1:]
        seg_durtns[-1]  = nPts - iiUp[-1]
        seg_starts[-1]  = iiUp[-1]
        seg_stops [-1]  = nPts
    else:                                           #   ends standing
        seg_durtns[1:]  = iiDn[1:] - iiUp
        seg_starts[1:]  = iiUp
        seg_stops [1:]  = iiDn[1:]
elif iiUp[0] < iiDn[0]:                             # begins standing
    if iiUp[-1] > iiDn[-1]:                         #   ends seated
        seg_durtns[0:-1]    = iiDn - iiUp[0:-1]
        seg_starts[0:-1]    = iiUp[0:-1]
        seg_stops [0:-1]    = iiDn
        seg_durtns[-1]  = nPts - iiUp[-1]
        seg_starts[-1]  = iiUp[-1]
        seg_stops [-1]  = nPts
    else:                                           #   ends standing
        seg_durtns  = iiDn - iiUp
        seg_starts  = iiUp
        seg_stops   = iiDn
else:
    raise RuntimeError("shouldn't be able to reach this code.")

#
#   Formatted print of results for all segments
#

# overall results
dur = nPts/SampleRate
hh  = dur // 3600
mm  = (dur % 3600) // 60
ss  = (dur % 3600) % 60
print >> OutStream, 'total time     : %2i:%02i:%02i' % (hh, mm, ss)
iSeat   = np.nonzero( seated_state == 1 )[0]
pct     = len(iSeat) / float(nPts) * 100.0
dur = len(iSeat)/SampleRate
hh  = dur // 3600
mm  = (dur % 3600) // 60
ss  = (dur % 3600) % 60
print >> OutStream, 'seated time    : %2i:%02i:%02i (%2i%%))' % (hh, mm, ss, pct)
iStnd   = np.nonzero( seated_state == 0 )[0]
pct     = len(iStnd) / float(nPts) * 100.0
dur = len(iStnd)/SampleRate
hh  = dur // 3600
mm  = (dur % 3600) // 60
ss  = (dur % 3600) % 60
print >> OutStream, 'standing time  : %2i:%02i:%02i (%2i%%))' % (hh, mm, ss, pct)

# segment results
print >> OutStream, 'standing segments:'
names   = [ 'segment', 'start', 'stop', 'duration' ]
fmt     = "%12s"+"%10s"*3
print >> OutStream, fmt % tuple(names)

for i in range(len(seg_durtns)):
    Beg = elapsed_time[ seg_starts[i] ]
    hhBeg   =  Beg // 3600
    mmBeg   = (Beg % 3600) // 60
    ssBeg   = (Beg % 3600) % 60
    End = elapsed_time[ seg_stops[i] ]
    hhEnd   =  End // 3600
    mmEnd   = (End % 3600) // 60
    ssEnd   = (End % 3600) % 60
    dur = seg_durtns[i]/SampleRate
    hhDur   = dur // 3600
    mmDur   = (dur % 3600) // 60
    ssDur   = (dur % 3600) % 60
    DurPlus = '' if hhDur==0 else '+%ih' % (hhDur)
    fmt = '%12d'+'%4i:%02i:%02i'+'%4i:%02i:%02i' + '%7i:%02i' + '%s'
    print >> OutStream, fmt \
            % (i, hhBeg, mmBeg, ssBeg,
                  hhEnd, mmEnd, ssEnd,
                  mmDur, ssDur, DurPlus)

#
# best hour saddle endurance
#
'''
Find the longest segments that together total one hour,
and compute the average duration to serve as a metric for
the ride.
'''

# list of indices for longest durations
def GetSegment(i):
    return seg_durtns[i]
indx    = range(len(seg_durtns))
indx.sort(reverse=True, key=GetSegment)

# compute average and print
print >> OutStream, 'best-hour segments:'
names   = [ 'segment', 'start', 'stop', 'duration' ]
fmt     = "%12s"+"%10s"*3
print >> OutStream, fmt % tuple(names)
TotalTime   = 0.0
i   = 0
while TotalTime < 3600:
    Beg = elapsed_time[ seg_starts[indx[i]] ]
    hhBeg   =  Beg // 3600
    mmBeg   = (Beg  % 3600) // 60
    ssBeg   = (Beg  % 3600) % 60
    End = elapsed_time[ seg_stops[indx[i]] ]
    hhEnd   =  End // 3600
    mmEnd   = (End  % 3600) // 60
    ssEnd   = (End  % 3600) % 60
    dur = seg_durtns[indx[i]]/SampleRate
    hhDur   =  dur // 3600
    mmDur   = (dur  % 3600) // 60
    ssDur   = (dur  % 3600) % 60
    DurPlus = '' if hhDur==0 else '+%ih' % (hhDur)
    fmt = '%12d'+'%4i:%02i:%02i'+'%4i:%02i:%02i' + '%7i:%02i' + '%s'
    print >> OutStream, fmt \
            % (indx[i], hhBeg, mmBeg, ssBeg,
                        hhEnd, mmEnd, ssEnd,
                        mmDur, ssDur, DurPlus)
    TotalTime   += dur
    i           += 1
BestAve = TotalTime / float(i)
hh  =  BestAve // 3600
mm  = (BestAve  % 3600) // 60
ss  = (BestAve  % 3600) % 60
DurPlus = '' if hh==0 else '+%ih' % (hh)
print >> OutStream, '        BEST ONE-HOUR AVERAGE:  %7i:%02i%s' \
        % (mm, ss, DurPlus)

############################################################
#                  plotting                                #
############################################################

# time plot
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.dates import date2num, DateFormatter
import datetime as dt
base = dt.datetime(2014, 1, 27, 0, 0, 0)
x = [ base + dt.timedelta(seconds=t) for t in elapsed_time ]
x = date2num(x) # Convert to matplotlib format
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, sharex=True)
ax0.plot_date( x, signals['power'], 'b-', linewidth=1 );
ax0.grid(True)
ax0.set_ylabel('power, W')
ax0.set_title('Saddle Endurance')
ax1.plot_date( x, signals['cadence'],   'g-', linewidth=1 );
ax1.plot_date( x, cad_fwd_min_3_8,      'm-', linewidth=1 );
ax1.plot_date( x, cad_fwd_min_1_8,   'brown', linestyle='-', linewidth=1 );
ax1.grid(True)
ax1.set_ylabel('cadence, RPM')
ax1.legend(['cadence', 'cad_fwd_min_3_8', 'cad_fwd_min_1_8'],
            loc='upper left');
ax2.plot_date( x, seated_state, 'r-', linewidth=3 );
ax2.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
ax2.grid(True)
ax2.set_ylabel('seated')
ax2.set_yticks([0,1])
ax2.set_yticklabels(('standing', 'seated'))
fig.canvas.set_window_title(FitFilePath)
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
