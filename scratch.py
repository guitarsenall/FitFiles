
# scratch.py

# experiment with a streaming object for print statement
class MyStream():
    def write(self, data):
        print 'MyStream.write(): ', data
mystream = MyStream()
print >> mystream, 'some text'

## experiment with endurance_summary.py
#from endurance_summary import endurance_summary
#fitfilepath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
#            + r'2018-12-03-17-46-09.fit'
#endurance_summary(fitfilepath, ConfigFile=None)


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


