
#   compare_two_powers.py
'''
Compare power data for the same activity from two systems.

To do:
    *   Apply time scaling in hh:mm:ss format.

'''

from datetime import datetime
from fitparse import Activity
from activity_tools import extract_activity_signals, new_find_delay

FilePath        = r'D:\Users\Owner\Documents\OneDrive\bike\activities\leo\\'
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

from pylab import plt, arange, interp, array, zeros, sqrt, average
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

#
#   remove delay and scaling error in heart rate
#
x2  = RetDict['A']
x1  = RetDict['B']
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

## determine indices into edge_t for overlapping region
#iBeg    = int(ExactDelay)
#iEnd    = iBeg + len()

# resample zwift signals onto edge timeline
# using inferred delay and scaling error
zwift_t_s       = TimeScale*zwift_t + ExactDelay
zwift_power_r   = interp(edge_t, zwift_t_s, zwift_power)
zwift_hr_r      = interp(edge_t, zwift_t_s, zwift_hr )

#Measure the delay (and theoretically zero scaling error)
#between the edge (Kickr) and resampled Zwift (PowerTap)
#power meter signals. I think the PowerTap is delayed
#in the Kickr, so
x1  = zwift_power_r
x2  = edge_power
x0  = [1.0, 1.0]
bnds = ( (0.95, 1.05), (-3, 3) )
res = minimize(ScaleDelayError, x0, method='SLSQP', bounds=bnds)
print res.message
print 'scale = %5.3f, Kickr Delay = %5.1f' % (res.x[0], res.x[1])

# resample the resampled zwift_power to eliminate its delay
# so zwift_power_r_r can be cross-plotted against edge_power.
zwift_t_s_s     = res.x[0]*edge_t + res.x[1]
zwift_power_r_r = interp(edge_t, zwift_t_s_s, zwift_power_r)

'''
from scipy.optimize import minimize
zwift_power_r   = interp(edge_t, zwift_t, zwift_power)
def ScaleOffsetError(m, B):
    x2_r    = interp( x1_t, x2_t, x2 )
    c   = x1 - x2_r     # ( m*x2 + B )
    RMSError    = sqrt(average( c**2 ))
    return RMSError
PowerDelay = find_delay( edge_power, zwift_power_r, MinDelay=-20, MaxDelay=20 )
print 'power optimum delay: ', PowerDelay
'''


#
#   plots
#

AxTop = plt.subplot(211)    #2, 1, 1
plt.plot(edge_t/60.0, edge_hr, 'r')
plt.plot(edge_t/60.0, zwift_hr_r, 'b')
plt.legend(['PowerTap P1', 'Zwift'], loc='best')
plt.title('P1 and Zwift Heart Rate and Power')
plt.ylabel('BPM')

# sharex causes the X-limits to be the same in both plots
AxBot = plt.subplot(212, sharex=AxTop)
#plt.axes(sharex=AxTop)
plt.plot(edge_t/60.0, edge_power, 'r')
plt.plot(edge_t/60.0, zwift_power_r, 'b')
plt.legend(['PowerTap P1', 'Zwift'])
plt.xlabel('time (min)')
plt.ylabel('power (w)')
plt.show()

# cross-plot powers
# resample zwift power onto edge
CrossPlotFig    = plt.figure()
sc = plt.scatter(edge_power, zwift_power_r_r, s=5, c=edge_t, \
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
ii      = nonzero( logical_and( edge_t>2,      \
                   logical_and(edge_power>1,   \
                               edge_power<400) ))
x       = edge_power[ii]
y       = zwift_power_r_r[ii]
coef    = polyfit( x, y, deg=1 )
slope   = coef[0]
offset  = coef[1]
print 'slope = %5.3f, offset = %i' % (slope, offset)
y_fit   = slope*x + offset
color   = average(edge_t[ii]) * ones(len(edge_t[ii]))
plt.plot( x, y_fit, 'k-' )
plt.show()
