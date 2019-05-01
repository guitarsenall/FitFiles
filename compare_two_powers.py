
#   compare_two_powers.py
'''
Compare power data for the same activity from two systems.

To do:
    *   Apply time scaling in hh:mm:ss format.

'''

import numpy as np
from datetime import datetime
from fitparse import Activity
from activity_tools import extract_activity_signals, new_find_delay

FilePath        = r'D:\Users\Owner\Documents\OneDrive\bike\activities\leo\\'
#FilePath        = r'S:\will\documents\OneDrive\bike\activities\leo\\'
EdgeFilePath    = FilePath + r'P1 - 2019-04-22-11-40-45.fit'
ZwiftFilePath   = FilePath + r'Infocrank (Zwift) 2019-04-22-10-30-09.fit'

# Delay range in seconds.
# for finding the delay in Edge relative to Zwift:
# a positive delay means Edge looks like a delayed version of Zwift.
MinDelay    = 40*60
MaxDelay    = 50*60

#EdgeFilePath    = r'2017-01-02-16-12-43_edge.fit'
#ZwiftFilePath   = r'2017-01-02-16-07-51_zwift.fit'

#EdgeFilePath    = r'2017-01-07-10-20-12_edge_quarq.fit'
#ZwiftFilePath   = r'2017-01-07-10-15-57_zwift_fluid2.fit'

EdgeActivity    = Activity(EdgeFilePath)
ZwiftActivity   = Activity(ZwiftFilePath)

EdgeSignals     = extract_activity_signals(EdgeActivity)
ZwiftSignals    = extract_activity_signals(ZwiftActivity)

# save signals for faster analysis
SignalMap   = { 'EdgeSignals'   : EdgeSignals,
                'ZwiftSignals'  : ZwiftSignals }
import pickle
SignalsFile = open( 'signals.pkl', 'wb')
pickle.dump(SignalMap, SignalsFile)
SignalsFile.close()

from pylab import arange, interp, array, zeros, sqrt, average
#from numpy import array, zeros, arange, interp, sqrt, average
# plot heart rate and calories
edge_hr         = EdgeSignals['heart_rate']
edge_t          = arange(len(edge_hr))
edge_power      = EdgeSignals['power']
zwift_hr        = ZwiftSignals['heart_rate']
zwift_t         = arange(len(zwift_hr))
zwift_power     = ZwiftSignals['power']

#zwift_hr_r      = interp(edge_t, zwift_t, zwift_hr)
#HRDelay         = find_delay( edge_hr, zwift_hr_r,
#                              MinDelay=MinDelay, MaxDelay=MaxDelay )
RetDict = new_find_delay( edge_hr, zwift_hr, MinRMSLength=100 )
HRDelay = RetDict['BestDelay']
print 'heart rate optimum delay: ', HRDelay
edge_cad        = EdgeSignals['cadence']
zwift_cad       = ZwiftSignals['cadence']
#zwift_cad_r     = interp(edge_t, zwift_t, zwift_cad)
#CadenceDelay    = find_delay( edge_cad, zwift_cad_r,
#                              MinDelay=MinDelay, MaxDelay=MaxDelay )
RetDict = new_find_delay( edge_cad, zwift_cad, MinRMSLength=100 )
CadenceDelay    = RetDict['BestDelay']
print 'cadence optimum delay: ', CadenceDelay

Ebeg = RetDict['Abeg']
Zbeg = RetDict['Bbeg']
Eend = RetDict['Aend']
Zend = RetDict['Bend']

#
#   remove delay and scaling error in heart rate
#
x2  = np.concatenate((
        RetDict['A'][0:745],
        RetDict['A'][805:2235]  ))  # remove dropouts
x1  = np.concatenate((
        RetDict['B'][0:745],
        RetDict['B'][805:2235]  ))  # remove dropouts
#x2  = RetDict['A']                 # edge_cad
#x1  = RetDict['B']                 # zwift_cad
#x1  = zwift_hr    # zwift_hr  zwift_cad
#x2  = edge_hr     # edge_hr   edge_cad

# x2 contains x1, but it is delayed and "stretched" in time.
# determine the scale and delay using minimize()
def ScaleDelayError(ScaleNDelay):
    # x1 and x2 must exist in calling namespace
    scale   = ScaleNDelay[0]
    delay   = ScaleNDelay[1]
    t1      = arange(len(x1))
    t2      = arange(len(x2))
    t1s     = scale*t1 + delay
    # resample the scaled x1 onto t2
    x1r     = interp(t2, t1s, x1)
    err     = x1r - x2
    RMSError    = sqrt(average( err**2 ))
    return RMSError

from scipy.optimize import minimize
x0      = [1.0, 0.0]
bnds    = ( (0.95, 1.05), (-10, 10) )
res     = minimize(ScaleDelayError, x0, method='SLSQP', bounds=bnds)
print res.message
TimeScale   = res.x[0]
ExactDelay  = res.x[1]
print 'TimeScale = %10.8f, ExactDelay = %5.3f' % (TimeScale, ExactDelay)

# Resample the zwift data
base_t          = arange(len(RetDict['A']))
zwift_t_s       = TimeScale*base_t + ExactDelay
zwift_cad_r     = interp(base_t, zwift_t_s, zwift_cad)
zwift_hr_r      = interp(base_t, zwift_t_s, zwift_hr )
zwift_power_r   = interp(base_t, zwift_t_s, zwift_power)


#Measure the delay (and theoretically zero scaling error)
#between the edge and resampled Zwift
#power meter signals.
#in the Kickr, so
x1  = zwift_power_r
x2  = edge_power_x  = edge_power[Ebeg:Eend]
x0  = [1.0, 0.0]
bnds = ( (0.95, 1.05), (-3, 3) )
res = minimize(ScaleDelayError, x0, method='SLSQP', bounds=bnds)
PMTimeScale   = res.x[0]
PMExactDelay  = res.x[1]
print res.message
print 'scale = %10.6f, Zwift PM Delay = %6.3f' % (res.x[0], res.x[1])

# resample the resampled zwift_power to eliminate its delay
# so zwift_power_r_r can be cross-plotted against
# edge_power_x.
zwift_t_s_s     = PMTimeScale*base_t + PMExactDelay
zwift_power_r_r = interp(base_t, zwift_t_s_s, zwift_power_r)


#
#   plots
#
import matplotlib.pyplot as plt

# overplot the data shifted by the delay (no resampling).
import matplotlib.dates as md
from matplotlib.dates import date2num, DateFormatter
import datetime as dt
base = dt.datetime(2014, 1, 1, 0, 0, 0)
if CadenceDelay > 0:
    time_signal = edge_t
    x_edge  = [ base + dt.timedelta(seconds=t)          \
                for t in time_signal.astype('float')    ]
    x_zwift = x_edge[Ebeg:Eend]
else:
    time_signal = zwift_t
    x_zwift = [ base + dt.timedelta(seconds=t)          \
                for t in time_signal.astype('float')    ]
    x_edge  = x_zwift[Zbeg:Zend]
x_edge  = date2num(x_edge ) # Convert to matplotlib format
x_zwift = date2num(x_zwift) # Convert to matplotlib format
fig1, (ax0, ax1, ax2) = plt.subplots(nrows=3, sharex=True)
ax0.plot_date( x_edge,   edge_cad, 'r-', linewidth=1 );
ax0.plot_date( x_zwift, zwift_cad, 'b-', linewidth=1 );
ax0.grid(True)
ax0.legend( ['Edge', 'Zwift' ], loc='upper left');
ax0.set_ylabel('cadence, RPM')
ax1.plot_date( x_edge,    edge_hr, 'r-', linewidth=1 );
ax1.plot_date( x_zwift,  zwift_hr, 'b-', linewidth=1 );
ax1.grid(True)
ax1.legend( ['Edge', 'Zwift' ], loc='upper left');
ax1.set_ylabel('heart rate, BPM')
ax2.plot_date( x_edge,    edge_power, 'r-', linewidth=1 );
ax2.plot_date( x_zwift,  zwift_power, 'b-', linewidth=1 );
ax2.grid(True)
ax2.legend( ['Edge', 'Zwift' ], loc='upper left');
ax2.set_ylabel('power, watts')
ax2.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
fig1.tight_layout()
fig1.subplots_adjust(hspace=0)   # Remove horizontal space between axes
fig1.suptitle('Raw data with delay applied', fontsize=20)
plt.show()

# plot resampled zwift data
fig2, (ax0, ax1, ax2) = plt.subplots(nrows=3, sharex=True)
ax0.plot_date( x_edge,   edge_cad,   'r-', linewidth=1 );
ax0.plot_date( x_zwift, zwift_cad_r, 'b-', linewidth=1 );
ax0.grid(True)
ax0.legend( ['Edge', 'Zwift' ], loc='upper left');
ax0.set_ylabel('cadence, RPM')
ax1.plot_date( x_edge,    edge_hr,   'r-', linewidth=1 );
ax1.plot_date( x_zwift,  zwift_hr_r, 'b-', linewidth=1 );
ax1.grid(True)
ax1.legend( ['Edge', 'Zwift' ], loc='upper left');
ax1.set_ylabel('heart rate, BPM')
ax2.plot_date( x_edge,    edge_power,   'r-', linewidth=1 );
ax2.plot_date( x_zwift,  zwift_power_r, 'b-', linewidth=1 );
ax2.grid(True)
ax2.legend( ['Edge', 'Zwift' ], loc='upper left');
ax2.set_ylabel('power, watts')
ax2.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
fig2.tight_layout()
fig2.subplots_adjust(hspace=0)   # Remove horizontal space between axes
fig2.suptitle('Resampled data with TimeScale and ExactDelay applied', fontsize=20)
plt.show()


# cross-plot powers
# resample zwift power onto edge
CrossPlotFig    = plt.figure()
sc = plt.scatter(edge_power_x, zwift_power_r_r, s=5, c=base_t, \
            cmap=plt.get_cmap('brg'), edgecolors='face' )
plt.colorbar(orientation='horizontal')
plt.title('Infocrank Vs PowerTap P1 Over Time (sec)\n(delay removed)')
plt.xlabel('PowerTap P1 (w)')
plt.ylabel('Infocrank via Zwift (w)')
plt.grid(b=True, which='major', axis='both')
a = plt.axis()
plt.axis([ 0, a[1], 0, a[3] ])
plt.show()

#
#   linear regression
#
from pylab import polyfit, average, ones, where, logical_and, nonzero
ii      = nonzero( logical_and( base_t>=0,      \
                   logical_and(edge_power_x>50,   \
                               edge_power_x<1000) ))
x       = edge_power_x[ii]
y       = zwift_power_r_r[ii]
coef    = polyfit( x, y, deg=1 )
slope   = coef[0]
offset  = coef[1]
print 'slope = %5.3f, offset = %i' % (slope, offset)
y_fit   = slope*x + offset
color   = average(edge_t[ii]) * ones(len(edge_t[ii]))
plt.plot( x, y_fit, 'k-' )
plt.show()
