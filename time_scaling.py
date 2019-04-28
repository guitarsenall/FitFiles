
# time_scaling.py
'''
One signal may be sampled with a delay relative to another.
Furthermore, the sampling may be at a different rate. So it is
both shifted and scaled in time. I need to master the basics.

Suppose Time2 is running faster than Time1
and started earlier. It's signal will appear delayed and
"stretched out" relative to Time1 so that its time axis would be,
    Time2 = m*Time1 + B
where m and B are the slope and offset, respectively.
'''

from numpy import array, zeros, arange, interp, sqrt, average
from scipy.optimize import minimize


'''
m = 2.0
B = 2.0

# create a simple test signal with two impulses
nPts    = 20
x1      = zeros(nPts)
x1[0]   = 1.0
x1[4]   = 1.0
t1      = arange(nPts)

# create a signal that is x1 delayed by 2 and time-scaled by 2
x2      = zeros(nPts)
x2[2]  = 1.0   # x1[0] delayed 2
x2[10] = 1.0   # x1[4] delayed and stretched
t2      = arange(nPts)

'''

m = 1.2
B = 10.0

# create a test signal with a pulse
iBeg1   = 40
iEnd1   = 60
nPts    = 100
x1      = zeros(nPts)
x1[iBeg1:iEnd1] = 1.0
t1      = arange(nPts)

# create a signal that is x1 delayed by B and time-scaled by m
x2      = zeros(nPts)
iBeg2 = int( m*iBeg1 + B )
iEnd2 = int( m*iEnd1 + B )
x2[iBeg2:iEnd2] = 1.0
t2      = t1.copy()

#
# x2 contains x1, but it is delayed and "stretched" in time.
# determine the scale and delay using minimize()
#
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
x0  = [1.2, 10]
bnds = ( (0.8, 1.4), (-10, 10) )
res = minimize(ScaleDelayError, x0, method='SLSQP', bounds=bnds)
print res.message
scale   = res.x[0]
delay   = res.x[1]
print 'scale = %5.3f, delay = %5.1f' % (scale, delay)

# create the shifted, and scaled time vector that maps x1 to x2
# so that plotting x1 against t1s causes it to "match" (look like)
# x2.
t1s = scale*t1+delay

# resample x1 onto x2. x1 matches x2 when plotted against t1s,
# but it is not sampled the same. We want a version that is.
x1r = interp(t1, t1s, x1)

#
# plots
#
import matplotlib.pyplot as plt
fig1, (ax0, ax1, ax2) = plt.subplots(nrows=3, sharex=False)
fig1.suptitle('time shifting and scaling', fontsize=20)
ax0.plot(t1, x1, 'b-o')
ax0.plot(t2, x2, 'r-+')
ax0.legend(['x1', 'x2'], loc='best')
ax1.plot(t1s, x1, 'b-o')
ax1.plot(t1, x2, 'r-+')
ax1.legend(['x1 (m=1.2, B=10)', 'x2'], loc='best')
ax2.plot(t1, x1r, 'b-o')
ax2.plot(t1, x2,  'r-+')
ax2.legend(['x1 (resampled)', 'x2'], loc='best')
plt.show()


