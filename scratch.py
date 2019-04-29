
# scratch.py

# experiment with new_find_delay()
from activity_tools import new_find_delay
import numpy as np
from math import pi, cos
t   = np.arange(5000)/500.0     # 10 sec at 500 Hz
B   = 2.00*np.cos(2*pi*2*t) \
    + 1.00*np.cos(2*pi*5*t) \
    + 0.50*np.cos(2*pi*9*t)
tB      = np.arange(len(B))
tBs     = 1.001*tB
Bstr    = np.interp(tB, tBs, B)
A   = np.concatenate(( \
            np.random.random(1500), \
            Bstr,
            np.random.random(500) ))
RetDict = new_find_delay( A, B,
                MinRMSLength=100 )
d   = RetDict['BestDelay']
i   = RetDict['BestIndex']
x2  = RetDict['A']
x1  = RetDict['B']

nA  = len(A)
nB  = len(B)
if d >= 0:
    Abeg    = d
    Bbeg    = 0
    if nA-d >= nB:
        Aend    = d+nB
        Bend    = nB
    else:
        Aend    = nA
        Bend    = nA-nB-1+d
else:
    if nB+d >= nA:
        Abeg    = 0
        Bbeg    = -d
        Aend    = nA
        Bend    = nB+d
    else:
        Abeg    = -d
        Bbeg    = 0
        Aend    = nA+d
        Bend    = nB

#
# x2 contains x1, but it is delayed and "stretched" in time.
# determine the scale and delay using minimize()
#
def ScaleDelayError(ScaleNDelay):
# x1 and x2 must exist in calling namespace
    scale   = ScaleNDelay[0]
    delay   = ScaleNDelay[1]
    t1      = np.arange(len(x1))
    t2      = np.arange(len(x2))
    t1s     = scale*t1 + delay
    # resample the scaled x1 onto t2
    x1r     = np.interp(t2, t1s, x1)
    err     = x1r - x2
    RMSError    = np.sqrt(np.average( err**2 ))
    return RMSError

from scipy.optimize import minimize
x0  = [1.0, 0]
bnds = ( (0.8, 1.4), (-10, 10) )
res = minimize(ScaleDelayError, x0, method='SLSQP', bounds=bnds)
print res.message
scale   = res.x[0]
delay   = res.x[1]
print 'scale = %10.6f, delay = %6.3f' % (scale, delay)


### experiment with delay detection.
##import numpy as np
##A   = np.array([0, 0, 0, 1, 0, 0, 0])
##B   = np.array([0, 0, 1, 0, 0])
#nA  = len(A)
#nB  = len(B)
##i   = 5
#if i < nB:
#    Abeg = 0
#    Bbeg = nB-1-i
#else:
#    Abeg = i-nB+1
#    Bbeg = 0
#if i < nA-1:
#    Aend = i+1
#    Bend = nB
#else:
#    Aend = nA
#    Bend = nB-(i-nA)-1
#Bslice  = B[Bbeg:Bend]
#Aslice  = A[Abeg:Aend]
#C = Bslice - Aslice
##print 'B:', Bslice
##print 'A:', Aslice
##print 'C:', C


## find a module
#import imp
#imp.find_module("activity_tools")


## modify dictionary?
#def modify_dict(d):
#    d['key'] = 'modified'
#    return d
#d = {}
#print modify_dict(d)


## get the algorithm right for set_times (saddle_endurance_anls.py)
##seated_state    = orig_seated_state             # "begins seated and ends standing"
##seated_state    = orig_seated_state[:7483]      # "begins seated and ends seated"
##seated_state    = orig_seated_state[145:]       # "begins standing and ends standing"
##seated_state    = orig_seated_state[145:7483]   # "begins standing and ends seated"
#nPts            = len(seated_state)
#import numpy as np
#iiUp = np.nonzero( seated_state[1:] - seated_state[0:-1] ==  1 )[0]
#iiDn = np.nonzero( seated_state[1:] - seated_state[0:-1] == -1 )[0]
#if iiUp[-1] < iiDn[-1]:
#    seg_times   = np.zeros(len(iiDn))
#else:
#    seg_times   = np.zeros(len(iiDn)+1)
#if iiDn[0] < iiUp[0]:                               # begins seated
#    print '    begins seated'
#    seg_times[0]    = iiDn[0]
#    if iiUp[-1] > iiDn[-1]:                         #   Ends seated
#        print '        ends seated'
#        seg_times[1:-1] = iiDn[1:] - iiUp[0:-1]
#        seg_times[-1]   = nPts - iiUp[-1]
#    else:                                           #   ends standing
#        print '        ends standing'
#        seg_times[1:]   = iiDn[1:] - iiUp
#elif iiUp[0] < iiDn[0]:                             # begins standing
#    print '    begins standing'
#    if iiUp[-1] > iiDn[-1]:                         #   ends seated
#        print '        ends seated'
#        seg_times[0:-1] = iiDn - iiUp[0:-1]
#        seg_times[-1]   = nPts - iiUp[-1]
#    else:                                           #   ends standing
#        print '        ends standing'
#        seg_times = iiDn - iiUp
#else:
#    raise RuntimeError("shouldn't be able to reach this code.")


##double-nested array indices
#import numpy as np
#x   = np.arange(1,6,1)
#y   = x+5
#xg, yg  = np.meshgrid(x,y)
#z   = np.arange(101, 120, 1)
#ii  = np.nonzero( z     > 104 )[0]
#jj  = np.nonzero( z[ii] < 108 )[0]
##    >>> z[ii[jj]]
##    array([105, 106, 107])


## differentiating lowpass filter
#import numpy as np
#from scipy import signal
#poles       = 4
#cutoff      = 0.1     # Hz
#SampleRate  = 1.0
#Wn          = cutoff / (SampleRate/2)
#PadLen      = int(SampleRate/cutoff)
#NumB, DenB  = signal.butter(poles, Wn, btype='lowpass',
#                            output='ba', analog=True)
#NumF    = signal.convolve( NumB, [1,0])
#HPtf    = signal.TransferFunction(NumF,DenB)
#t1, y1  = signal.step(HPtf)
#b, a    = signal.bilinear(NumF,DenB, fs=SampleRate)
#x2      = np.ones(len(t1))  # step
#y2      = signal.lfilter(b, a, x2)
#import matplotlib.pyplot as plt
#plt.figure(1)
#plt.plot(t1, y1, 'r-')
#plt.plot(t1, y2, 'b-')
#plt.show()



## Plot multiple workouts with different solutions for
## HR-simulation parameters for Kim.
#import sys
#from pwhr_transfer_function import pwhr_transfer_function
#ConfigFile  = r'D:\Users\Owner\Documents\OneDrive\2018\fitfiles\\'  \
#            + r'cyclingconfig_kim.txt'
#OutStream   = sys.stdout
#FilePath    = r'S:\will\documents\OneDrive\bike\activities\kim\\'
#params  = [
#    #         file              FTHR    tau    HRDriftRate
#    ['2018-09-10-18-21-11.fit', '161', ' 67.3', '0.154862' ], # A2
#    ['2018-06-22-18-35-17.fit', '150', ' 56.6', '0.332012' ], # M2
#    ['2018-08-25-17-27-32.fit', '161', ' 66.9', '0.355928' ], # M6
#    ['2018-09-24-18-27-54.fit', '171', '110.7', '0.103539' ], # M6
#    ['2018-09-06-18-23-46.fit', '153', ' 70.1', '0.381981' ], # M1
#    ['2018-12-26-14-51-33.fit', '157', ' 75.8', '0.151274' ]  # E2
#    ] #2:3
#from ConfigParser import ConfigParser
#config      = ConfigParser()
#config.read(ConfigFile)
#for i in range(len(params)):
#    fitfilepath = FilePath + params[i][0]
#    config.set( 'power', 'ThresholdHR',    params[i][1] )
#    config.set( 'power', 'HRTimeConstant', params[i][2] )
#    config.set( 'power', 'HRDriftRate',    params[i][3] )
#    pwhr_transfer_function( fitfilepath, OutStream=sys.stdout,
#                            ConfigFile=config )



##Follow
##    https://www.youtube.com/watch?v=2lQbGQ_cQ3w
##for step simulation of 1st-order transfer function.
#import numpy as np
#from scipy import signal
#import matplotlib.pyplot as plt
#from scipy.integrate import odeint
#k   = 3.0
#tau = 2.0
#num     = [k]
#den     = [tau, 1]
#HPtf    = signal.TransferFunction(num,den)
#t1, y1  = signal.step(HPtf)
#Fs      = 10.0
#timevec = np.arange(0, 14, 1/Fs)
#nPts    = len(timevec)
#u_input         = np.zeros(nPts)
#u_input[10:]    = 1.0
#def model(y,t):
#    i = int(t * Fs)
#    print 't = ', t, ', i = ', i
#    u = u_input[i]
#    return (-y + k*u)/tau
#y2 = odeint(model,0,timevec)
#plt.figure(1)
#plt.plot(t1, y1, 'r-')
#plt.plot(timevec, y2, 'b--')
#plt.show()


## experiment with zone data structure
#FTHR = 170.0
#hZones  = { 1   : ([     0    ,   0.82*FTHR ],  ' 1' ),
#            2   : ([ 0.82*FTHR,   0.89*FTHR ],  ' 2' ),
#            3   : ([ 0.89*FTHR,   0.94*FTHR ],  ' 3' ),
#            4   : ([ 0.94*FTHR,   1.00*FTHR ],  ' 4' ),
#            5   : ([ 1.00*FTHR,   1.03*FTHR ],  '5a' ),
#            6   : ([ 1.03*FTHR,   1.06*FTHR ],  '5b' ),
#            7   : ([ 1.07*FTHR,   1.15*FTHR ],  '5c' )}
#
#h_zone_bounds   = [     0.4*FTHR,       #  1 lo
#                    hZones[2][0][0],    #  2 lo
#                    hZones[3][0][0],    #  3 lo
#                    hZones[4][0][0],    #  4 lo
#                    hZones[5][0][0],    # 5a lo
#                    hZones[6][0][0],    # 5b lo
#                    hZones[7][0][0],    # 5c lo
#                    hZones[7][0][1] ]   # 5c hi
#
#h_zone_labels   = [ hZones[k][1] for k in range(1,8) ]



#import sys, os
#(CodePath, PyFileName)      = os.path.split(sys.argv[0])
#(FitFilePath, FitFileName)  = os.path.split(sys.argv[1])
#print 'codepath     : ', CodePath
#print 'pyfilename   : ', PyFileName
#print 'fitfilepath  : ', FitFilePath
#print 'fitfilename  : ', FitFileName

## experiment with exceptions
#try:
#    x = 2/0
#except Exception, e:
#    print 'error trapped'
#    ErrObj = e

## experiment with a streaming object for print statement
## used in endurance_summary()
#import sys
#class MyStream():
#    def write(self, data):
#        print data,     # 'MyStream.write(): ', data
#mystream = MyStream()     # MyStream() or sys.stdout
##print >> mystream, 'some text'
#from endurance_summary import endurance_summary
#fitfilepath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
#            + r'2018-12-03-17-46-09.fit'
#endurance_summary(fitfilepath, ConfigFile=None, OutStream=mystream)


## remove bad entries from datalist
#badfiles    = [ '2016-07-09-13-52-59.fit' ]
#DataFileName    = 'datalist.pkl'
#import pickle
#DataFile    = open( DataFileName, 'rb')
#datalist    = pickle.load(DataFile)
#DataFile.close()
#print '%i entries extracted from %s' % (len(datalist), DataFileName)
#for entry in datalist:
#    if entry['filename'] in badfiles:
#        datalist.remove(entry)
#DataFile    = open( DataFileName, 'wb')
#pickle.dump(datalist, DataFile)
#DataFile.close()
#print '%i entries written to %s' % (len(datalist), DataFileName)



## messing with cadence
#cadence = array(avg_cadence)
#avg_hr  = array(avg_heart_rate)
#max_hr  = array(max_heart_rate)
#print "%8s"*6 % tuple(names1)
#print "%8s"*6 % tuple(names2)
#for i in range(len(ii)):
#    mm = time[ii[i]] // 60
#    ss = time[ii[i]]  % 60
#    print '%8d%5i:%02i%8d%8d%8d%8d' \
#            % (ii[i], mm, ss, power[ii[i]],
#                cadence[ii[i]],
#                avg_hr[ii[i]],
#                max_hr[ii[i]] )
#from numpy import average
#mm = sum(time[ii]) // 60
#ss = sum(time[ii])  % 60
#print '%8s%5i:%02i%8d%8d%8d%8d' \
#        % ("AVERAGE", mm, ss,
#            sum(power[ii]*time[ii]) / sum(time[ii]),
#            average(cadence[ii]),
#            average(avg_hr[ii]),
#            average(max_hr[ii]) )

## Determine rider's weight based on climbing power
#from math import *
#power       = 242.0                     # watts = N *m/s
#speed       = 12.5 * 0.44704             # m/s
#duration    = 8*60.0+11                 # seconds
#ascent      = (405-226)*12*25.4/1000    # meters
#distance    = speed * duration          # meters
#thrust      = power/speed               # N
#tht         = asin(ascent/distance)
#weight      = thrust * ( cos(tht)/tan(tht) + sin(tht) ) * 0.224809 # pounds
#print 'Rider weights %i lbs' % weight


## weight-dope to ride with Kim
#KimIntensity    = 0.95
#WillIntensity   = 1.0
#KimFTP          = 160.0         # w
#WillFTP         = 270.0         # w
#KimWeight       = 50.0          # kg
#WillWeight      = (WillIntensity*WillFTP) / (KimIntensity*KimFTP) * KimWeight
#print 'Will: %i kg (%i lbs)' % (WillWeight, WillWeight/0.4536)

## guess Nivin's weight
#NivinPower = 194.0
#WillPower = 285.0
#WillWeight = 85.0
#NivinWeight = NivinPower * WillWeight / WillPower
#print 'Niven: %i kg (%i lbs)' % (NivinWeight, NivinWeight/0.45359237)

#from numpy import nonzero, array, arange, zeros
#nPts = len(x)
#OnState = False
#intervals = []
#interval  = {}
#for i in range(0,nPts-DebounceCounts+1):
#    OnTestArray = nonzero( x[i:i+DebounceCounts] > OnLevel )[0]
#    if len(OnTestArray) == DebounceCounts:
#        if not OnState:
#            # new interval begins
#            print 'interval detected at sample %i' % i
#            interval['on'] = i
#        OnState = True
#    OffTestArray = nonzero( x[i:i+DebounceCounts] < OffLevel)[0]
#    if len(OffTestArray) == DebounceCounts:
#        #print 'OnState set to False at sample %i' % i
#        if OnState:
#            # interval ends
#            print 'interval ended at sample %i' % i
#            interval['off'] = i
#            intervals.append( interval.copy() )
#        OnState = False

## crack the record.type
#from datetime import datetime
#from fitparse import Activity
#FileLoc = r'S:\\will\\documents\\OneDrive\\bike\\activities\\will\\'
#fitfilepath = FileLoc + r'2018-09-28-09-52-01.fit'  # long ride
#activity = Activity(fitfilepath)
#activity.parse()
#records = activity.records
#record_types = set()
#for record in records:
#    if record.type.name != 'record':
#        #print record.type.name
#        record_types.add(record.type.name)
#records = activity.get_records_by_type('lap')
#for record in records:
#    print record.type.name
#    print record.get_valid_field_names()
#    break

## import and plot signals saved as
##   SignalMap   = { 'EdgeSignals'   : EdgeSignals,
##                   'ZwiftSignals'  : ZwiftSignals }
#import pickle
#SignalsFile = open( 'signals.pkl', 'rb')
#SignalMap   = pickle.load(SignalsFile)
#SignalsFile.close()
#print 'signal map fields: ', SignalMap.keys()
#EdgeSignals     = SignalMap['EdgeSignals']
#ZwiftSignals    = SignalMap['ZwiftSignals']
#from pylab import plt, arange, interp
#edge_hr         = EdgeSignals['heart_rate']
#edge_t          = arange(len(edge_hr)) #/ 60.0
#edge_power      = EdgeSignals['power']
#edge_speed      = EdgeSignals['speed']
#zwift_hr        = ZwiftSignals['heart_rate']
#zwift_t         = arange(len(zwift_hr)) #/ 60.0
#zwift_power     = ZwiftSignals['power']
#zwift_speed     = ZwiftSignals['speed']
#AxTop = plt.subplot(211)    #2, 1, 1
#plt.plot(edge_t, edge_speed, 'r')
#plt.plot(zwift_t, zwift_speed, 'b')
#plt.legend(['Garmin Edge', 'Zwift'], loc='best')
#plt.title('Edge and Zwift Speed and Power')
#plt.ylabel('m/s')
#AxBot = plt.subplot(212, sharex=AxTop)
#plt.plot(edge_t, edge_power, 'r')
#plt.plot(zwift_t, zwift_power, 'b')
#plt.legend(['Quarq Elsa RS', 'PowerBeam'])
#plt.xlabel('time (sec)')
#plt.ylabel('power (w)')
#plt.show()


