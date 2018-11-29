#!/usr/bin/env python

# Sample usage of python-fitparse to parse an activity and
# print its data records.

from datetime import datetime

from fitparse import Activity

#fitfilepath = r'S:\will\documents\bike\python-fitparse-master\tests\data\\' \
#            + r'sample-activity.fit'
fitfilepath = r'2017-01-02-16-12-43_edge.fit'

activity = Activity(fitfilepath)
activity.parse()

# Records of type 'record' (I know, confusing) are the entries in an
# activity file that represent actual data points in your workout.
# types: [ 'record', 'lap', 'event', 'session', 'activity', ... ]
records = activity.get_records_by_type('lap')
current_record_number = 0

time_signal = []
heart_rate  = []
FirstIter   = True

for record in records:

    # Print record number
    current_record_number += 1
    print (" Record #%d " % current_record_number).center(40, '-')

    # Get the list of valid fields on this record
    valid_field_names = record.get_valid_field_names()

    for field_name in valid_field_names:
        # Get the data and units for the field
        field_data = record.get_data(field_name)
        field_units = record.get_units(field_name)

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
            time_signal.append(dt.total_seconds())
            heart_rate.append(field_data)

    print
