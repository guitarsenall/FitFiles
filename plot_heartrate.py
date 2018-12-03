#!/usr/bin/env python

# Sample usage of python-fitparse to parse an activity and
# print its data records.

verbose = False

from datetime import datetime
from fitparse import Activity

#fitfilepath = r'S:\will\documents\bike\python-fitparse-master\tests\data\\' \
#            + r'sample-activity.fit'
#fitfilepath = r'2017-01-02-16-12-43_edge.fit'
#fitfilepath = r'2017-01-02-16-07-51_zwift.fit'
fitfilepath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
            + r'2018-12-02-20-29-34.fit'

activity = Activity(fitfilepath)
activity.parse()

# Records of type 'record' (I know, confusing) are the entries in an
# activity file that represent actual data points in your workout.
records = activity.get_records_by_type('record')
current_record_number = 0

time_list = []
heartrate_list  = []
FirstIter   = True

for record in records:

    # Print record number
    current_record_number += 1
    if verbose:
        print (" Record #%d " % current_record_number).center(40, '-')

    # Get the list of valid fields on this record
    valid_field_names = record.get_valid_field_names()

    for field_name in valid_field_names:
        # Get the data and units for the field
        field_data = record.get_data(field_name)
        field_units = record.get_units(field_name)

        if verbose:
            # Print what we've got!
            if field_units:
                print " * %s: %s %s" % (field_name, field_data, field_units)
            else:
                print " * %s: %s" % (field_name, field_data)

        if 'timestamp' in field_name:
            if FirstIter:
                t0  = field_data    # datetime
                t   = t0
                FirstIter   = False
            else:
                t   = field_data    # datetime


        if 'heart_rate' in field_name:
            dt  = t-t0
            time_list.append(dt.total_seconds())
            heartrate_list.append(field_data)

    print

# plot the heart rate
import numpy as np
from pylab import *
time_signal         = array(time_list)
heartrate_signal    = array(heartrate_list)
plot(time_signal/60.0, heartrate_signal, 'r.-')
xlabel('time (min)')
ylabel('heart rate (BPM)')
title('heart rate')
grid(True)
show()

# file for holding the signals (dictionary via pickle)
SignalMap   = { 'time_signal'       : time_signal,
                'heartrate_signal'  : heartrate_signal }
import pickle
SignalsFile = open( 'signals.pkl', 'wb')
pickle.dump(SignalMap, SignalsFile)
SignalsFile.close()

########################################################################
###         Compute Calories                                         ###
########################################################################

## import the signals
#import pickle
#SignalsFile = open( 'signals.pkl', 'rb')
#SignalMap   = pickle.load(SignalsFile)
#SignalsFile.close()
#
#print 'signal map fields: ', SignalMap.keys()
# ['heartrate_signal', 'time_signal']


from pylab import *

#   Formula widely available. One site:
#       https://www.easycalculation.com/formulas/heart-rate-calorie-burn.html

weight  = 188.0*0.45359237  # lb->kg
age     = 50.0

#   calibration at endurance
EnduranceHR     = 140.0                         # BPM
EndurancePower  = 190.0                         # watts
EnduranceBurn   = EndurancePower*3600/1e3/60    # Cal/min
EnduranceCoef   = EnduranceBurn                     \
                / (   -55.0969 + 0.6309*EnduranceHR \
                    + 0.1988*weight + 0.2017*age)   \
                * 4.184

#   calibration at threshold
ThresholdHR     = 170.0                         # BPM
ThresholdPower  = 271.0                         # watts
ThresholdBurn   = ThresholdPower*3600/1e3/60    # Cal/min
ThresholdCoef   = ThresholdBurn                     \
                / (   -55.0969 + 0.6309*ThresholdHR \
                    + 0.1988*weight + 0.2017*age)   \
                * 4.184

hr_sig      = SignalMap['heartrate_signal']
t_sig       = SignalMap['time_signal']
dt_sig      = append( array([1.0]), t_sig[1:] - t_sig[0:-1] )
nPts        = t_sig.size
calories    = zeros(nPts)

for i, dt, HR in zip( range(nPts), dt_sig, hr_sig ):

    # calories per minute
    if HR >= EnduranceHR and HR <= ThresholdHR:
        CalPerMin   = EnduranceBurn                 \
                    + (HR-EnduranceHR)              \
                    * (ThresholdBurn-EnduranceBurn) \
                    / (ThresholdHR-EnduranceHR)
    else:
        if HR < EnduranceHR:
            coef  = EnduranceCoef
        else:
            coef  = ThresholdCoef
        CalPerMin   = (   -55.0969      \
                        + 0.6309*HR     \
                        + 0.1988*weight \
                        + 0.2017*age)   \
                    / 4.184             \
                    * coef
    calories[i] = dt * CalPerMin / 60

running_calories    = cumsum( calories )

print 'total calories = %i' % running_calories[nPts-1]

# plot heart rate and calories
plt.subplot(2, 1, 1)
plt.plot(t_sig/60, hr_sig, 'r.-')
plt.title('Heart Rate and Calories')
plt.ylabel('BPM')

plt.subplot(2, 1, 2)
plt.plot(t_sig/60, running_calories, 'b.-')
plt.xlabel('time (min)')
plt.ylabel('calories')

plt.show()
