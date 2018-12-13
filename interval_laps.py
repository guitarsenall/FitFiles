#!/usr/bin/env python

'''
interval_laps.py

Process a .FIT file in which the laps represent intervals above a certain
intensity.

'''

import os
import sys

############################################################
#              interval_laps function def                  #
############################################################

def interval_laps(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

    # ConfigFile not currently used, but maintain calling format.

    (FilePath, FitFileName) = os.path.split(FitFilePath)

    from datetime import datetime
    from fitparse import Activity

    activity = Activity(FitFilePath)
    activity.parse()

    # get the FTP
    FTP = 250.0 #assume if not present
    records = activity.get_records_by_type('zones_target')
    for record in records:
        valid_field_names = record.get_valid_field_names()
        for field_name in valid_field_names:
            if 'functional_threshold_power' in field_name:
                field_data = record.get_data(field_name)
                field_units = record.get_units(field_name)
                print >> OutStream, 'FTP setting = %i %s' % (field_data, field_units)
                FTP = field_data

    # set the interval threshold. Intervals with average power below this
    # value are ignored.
    IntervalThreshold = 0.75*FTP

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
        #print >> OutStream, (" Record #%d " % current_record_number).center(40, '-')

        # Get the list of valid fields on this record
        valid_field_names = record.get_valid_field_names()

        for field_name in valid_field_names:
            # Get the data and units for the field
            field_data = record.get_data(field_name)
            field_units = record.get_units(field_name)

            ## Print what we've got!
            #if field_units:
            #    print >> OutStream, " * %s: %s %s" % (field_name, field_data, field_units)
            #else:
            #    print >> OutStream, " * %s: %s" % (field_name, field_data)

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

    from numpy import nonzero, array, arange, zeros, average
    power = array(avg_power)
    ii = nonzero( power > IntervalThreshold )[0]   # index array
    print >> OutStream, 'processing %d laps above %d watts...' % (len(ii), IntervalThreshold)
    time    = array(elapsed_time)
    cadence = array(avg_cadence)
    avg_hr  = array(avg_heart_rate)
    max_hr  = array(max_heart_rate)
    balance = array(balance)
    names1 = [ '',    '',     'avg',   'avg', 'avg', 'max', 'avg' ]
    names2 = [ 'lap', 'time', 'power', 'cad',  'HR',  'HR', 'bal'  ]
    print >> OutStream, "%8s"*7 % tuple(names1)
    print >> OutStream, "%8s"*7 % tuple(names2)
    for i in range(len(ii)):
        mm = time[ii[i]] // 60
        ss = time[ii[i]]  % 60
        print >> OutStream, '%8d%5i:%02i%8d%8d%8d%8d%8.1f' \
                % (ii[i], mm, ss, power[ii[i]],
                    cadence[ii[i]],
                    avg_hr[ii[i]],
                    max_hr[ii[i]],
                    balance[ii[i]] )
    mm = sum(time[ii]) // 60
    ss = sum(time[ii])  % 60
    print >> OutStream, '%8s%5i:%02i%8d%8d%8d%8d%8.1f' \
            % ("AVERAGE", mm, ss,
                sum(  power[ii]*time[ii]) / sum(time[ii]),
                sum(cadence[ii]*time[ii]) / sum(time[ii]),
                sum( avg_hr[ii]*time[ii]) / sum(time[ii]),
                max(max_hr[ii]),
                sum(balance[ii]*time[ii]) / sum(time[ii]) )
    #print >> OutStream, "average interval power: %d watts" % (sum(power[ii]*time[ii]) / sum(time[ii]))

# end interval_laps()

############################################################
#           main program execution                         #
############################################################
'''
This technique allows the module to be imported without
executing it until one of its functions is called.
'''

if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        print 'command line args: ', sys.argv[1:]
        fitfilepath = sys.argv[1]
        interval_laps(fitfilepath, ConfigFile=None)
    else:
        raise IOError('Need a .FIT file')

    #FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
    #            + r'2018-12-10-17-28-24.fit'

# SAMPLE OUTPUT:
#    CWD: D:\Users\Owner\Documents\OneDrive\bike\activities\will
#    PATH: D:\Users\Owner\Documents\OneDrive\bike\activities\will
#    FILE: 2018-12-10-17-28-24.fit
#
#    -------------------- Interval Laps --------------------
#
#    FTP setting = 260 None
#    processing 7 laps above 195 watts...
#                         avg     avg     avg     max     avg
#         lap    time   power     cad      HR      HR     bal
#           1    0:32     478      96     149     159    46.9
#           3    1:00     322      93     153     163    48.3
#           5    2:00     308      93     161     173    48.3
#           7    3:00     292      91     166     178    48.2
#           9    2:01     296      87     162     176    48.7
#          11    0:28     404      96     165     171    48.0
#          13    1:00     307      93     153     168    48.2
#     AVERAGE   10:05     315      91     160     178    48.3
