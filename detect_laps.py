#!/usr/bin/env python

# detect_laps.py

import sys
print 'command line args: ', sys.argv[1:]
# typ 'S:\\will\\documents\\bike\\fitfiles\\2017-01-08-15-41-48_zwift.fit'
#fitfilepath = r'S:\will\documents\bike\python-fitparse-master\tests\data\\' \
#            + r'sample-activity.fit'
#fitfilepath = r'2017-01-02-16-12-43_edge.fit'
fitfilepath = sys.argv[1]

from datetime import datetime

from fitparse import Activity


activity = Activity(fitfilepath)
activity.parse()


# get the FTP
FTP = 270.0 #assume if not present
records = activity.get_records_by_type('zones_target')
for record in records:
    valid_field_names = record.get_valid_field_names()
    for field_name in valid_field_names:
        if 'functional_threshold_power' in field_name:
            field_data = record.get_data(field_name)
            field_units = record.get_units(field_name)
            print 'FTP setting = %i %s' % (field_data, field_units)
            FTP = field_data


# Get Records of type 'lap'
# types: [ 'record', 'lap', 'event', 'session', 'activity', ... ]
records = activity.get_records_by_type('lap')
current_record_number = 0

elapsed_time    = []
avg_heart_rate  = []
avg_power       = []
avg_cadence     = []
max_heart_rate  = []
balance         = []

FirstIter   = True

for record in records:

    # Print record number
    current_record_number += 1
    #print (" Record #%d " % current_record_number).center(40, '-')

    # Get the list of valid fields on this record
    valid_field_names = record.get_valid_field_names()

    for field_name in valid_field_names:
        # Get the data and units for the field
        field_data = record.get_data(field_name)
        field_units = record.get_units(field_name)

        ## Print what we've got!
        #if field_units:
        #    print " * %s: %s %s" % (field_name, field_data, field_units)
        #else:
        #    print " * %s: %s" % (field_name, field_data)

        if 'timestamp' in field_name:
            if FirstIter:
                t0  = field_data    # datetime
                t   = t0
                FirstIter   = False
            else:
                t   = field_data    # datetime

        if 'total_timer_time' in field_name:
            elapsed_time.append( field_data )

        if 'avg_power' in field_name:
            avg_power.append( field_data )

        # avg_heart_rate is in a lap record
        if 'avg_heart_rate' in field_name:
            avg_heart_rate.append(field_data)

        if 'max_heart_rate' in field_name:
            max_heart_rate.append(field_data)

        if 'avg_cadence' in field_name:
            avg_cadence.append(field_data)

        if 'left_right_balance' in field_name:
            balance.append(field_data)

    #print

IntervalThreshold = 0.72*FTP
from numpy import nonzero, array, arange, zeros, average
power = array(avg_power)
ii = nonzero( power > IntervalThreshold )[0]   # index array
print 'processing %d laps above %d watts...' % (len(ii), IntervalThreshold)
time    = array(elapsed_time)
cadence = array(avg_cadence)
avg_hr  = array(avg_heart_rate)
max_hr  = array(max_heart_rate)
balance = array(balance)
names1 = [ '',    '',     'avg',   'avg', 'avg', 'max', 'avg' ]
names2 = [ 'lap', 'time', 'power', 'cad',  'HR',  'HR', 'bal'  ]
print "%8s"*7 % tuple(names1)
print "%8s"*7 % tuple(names2)
for i in range(len(ii)):
    mm = time[ii[i]] // 60
    ss = time[ii[i]]  % 60
    print '%8d%5i:%02i%8d%8d%8d%8d%8.1f' \
            % (ii[i], mm, ss, power[ii[i]],
                cadence[ii[i]],
                avg_hr[ii[i]],
                max_hr[ii[i]],
                balance[ii[i]] )
mm = sum(time[ii]) // 60
ss = sum(time[ii])  % 60
print '%8s%5i:%02i%8d%8d%8d%8d%8.1f' \
        % ("AVERAGE", mm, ss,
            sum(  power[ii]*time[ii]) / sum(time[ii]),
            sum(cadence[ii]*time[ii]) / sum(time[ii]),
            sum( avg_hr[ii]*time[ii]) / sum(time[ii]),
            max(max_hr[ii]),
            sum(balance[ii]*time[ii]) / sum(time[ii]) )
#print "average interval power: %d watts" % (sum(power[ii]*time[ii]) / sum(time[ii]))
