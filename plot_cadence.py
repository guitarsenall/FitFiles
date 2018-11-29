#!/usr/bin/env python

# Sample usage of python-fitparse to parse an activity and
# print its data records.

verbose = True

from datetime import datetime
from fitparse import Activity
from activity_tools import extract_activity_signals

fitfilepath = r'2017-01-26-15-29-03_intervals.fit'

activity = Activity(fitfilepath)
activity.parse()

signals     = extract_activity_signals(activity)

## plot heart rate and calories
#plt.subplot(2, 1, 1)
#plt.plot(t_sig/60, hr_sig, 'r.-')
#plt.title('Heart Rate and Calories')
#plt.ylabel('BPM')
#
#plt.subplot(2, 1, 2)
#plt.plot(t_sig/60, running_calories, 'b.-')
#plt.xlabel('time (min)')
#plt.ylabel('calories')
#
#plt.show()
