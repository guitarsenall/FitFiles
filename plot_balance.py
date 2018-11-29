# plot_balance.py
'''
cross-plot balance against power
'''

from pylab import plt, arange, interp, array, zeros, sqrt, average

# get signals
from datetime import datetime
from fitparse import Activity
from activity_tools import extract_activity_signals
FileLoc = r'S:\\will\\documents\\OneDrive\\bike\\activities\\will\\'
#fitfilepath = FileLoc + r'2018-06-01-11-13-49.fit'  # long ride
#fitfilepath = FileLoc + r'2016-07-09-13-52-59.fit'  # error
fitfilepath = FileLoc + r'2017-03-09-12-25-12.fit'  # FTP
activity    = Activity(fitfilepath)
signals     = extract_activity_signals(activity, resample='existing')
power       = signals['power']
balance     = signals['left_right_balance']
time        = signals['time']
PAvgBalance = sum(power*balance) / sum(power)

# get session info
records = activity.get_records_by_type('session')
for record in records:
    valid_field_names = record.get_valid_field_names()


# plotting
CrossPlotFig    = plt.figure()
sc = plt.scatter( power, balance, s=5, c=time,
            cmap=plt.get_cmap('brg'), edgecolors='face' )
plt.colorbar(orientation='horizontal')
plt.title('Balance Vs Power over Time (sec)\n' \
            + 'power-weighted average = %4.1f' % (PAvgBalance) )
plt.xlabel('Power (w)')
plt.ylabel('Right Balance (%)')
plt.grid(b=True, which='major', axis='both')
ax = plt.gca()
grids   = arange(10, 100, 10)   # force a gride at 50
ax.set_yticks( grids, minor=False)
ax.grid(True)
plt.show()

