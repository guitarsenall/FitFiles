# balance_over_time.py
'''
extract and plot balance over all FIT files in the directory.
'''

from pylab import plt, arange, interp, array, zeros, sqrt, average
from datetime import datetime
from fitparse import Activity
from activity_tools import extract_activity_signals
import os
import time

TimerStart = time.time()     # measure execution time

# set to False if datalist is already stored in DataFileName
ExtractData     = False      # True or False
DataFileName    = 'datalist.pkl'

#
# FTP test interval points
#
from matplotlib.dates import date2num
ftp_data    = array([[  '04/04/2015',    248,     48.5 ],
                     [  '08/14/2015',    237,     49.3 ],
                     [  '09/19/2015',    251,     49.2 ],
                     [  '05/23/2016',    252,     50.5 ],
                     [  '09/03/2016',    257,     50.8 ],
                     [  '03/09/2017',    270,     48.1 ] ] )
ftp_date    = []
for DateStr in ftp_data[:,0]:
    ftp_date.append( datetime.strptime(DateStr, '%m/%d/%Y').date() )
ftp_date_num    = date2num(ftp_date) # Convert to matplotlib format
ftp_ftp         = ftp_data[:,1].astype(float)
ftp_balance     = ftp_data[:,2].astype(float)


if ExtractData:

    directory   = r'S:\\will\\documents\\OneDrive\\bike\\activities\\will\\'
    fitfilepath = directory + r'2018-06-01-11-13-49.fit'  # long ride
    fit_files   = []

    # session fields to save from each file
    session_fields = [
        'start_time'      ,
        'total_timer_time',
        'total_distance'  ,
        'avg_speed'       ,
        'avg_power'       ,
        'avg_heart_rate'  ,
        'max_heart_rate'  ]

    today   = datetime.today().date()
    EntryType   = {
            'filename'          :  (''      , None      ),
            'balance'           :  (0.0     , '%'       ),
            'start_time'        :  (today   , None      ),
            'total_timer_time'  :  ( 0.0    , 's'       ),
            'total_distance'    :  ( 0.0    , 'm'       ),
            'avg_speed'         :  ( 0.0    , 'm/s'     ),
            'avg_power'         :  ( 0.0    , 'watts'   ),
            'avg_heart_rate'    :  ( 0.0    , 'bpm'     ),
            'max_heart_rate'    :  ( 0.0    , 'bpm'     )
        }

    #
    # get the list of FIT files
    #
    for filename in os.listdir(directory):
        if filename.endswith(".fit"):
            # print(os.path.join(directory, filename))
            fit_files.append(filename)
        else:
            print 'non-fit file: ' + filename

    #
    # fill the datalist
    #
    #fit_files   = fit_files[650:]       # limit number of files
    nFiles  = len(fit_files)
    index       = 0
    datalist    = []

    print 'processing %i FIT files' % nFiles
    print '-'*2*50 + '|'
    for i, filename in zip(range(nFiles), fit_files):
        if i % (nFiles/50) == 0:    # 50 total dots
            print '.',              # note trailing comma
        fitfilepath = directory + filename
        activity    = Activity(fitfilepath)
        signals     = extract_activity_signals(activity, resample='existing')
        if not signals.has_key('left_right_balance'):
            continue    # skip this file

        # compute balance
        power       = signals['power']
        balance     = signals['left_right_balance']
        timevec     = signals['time']
        PAvgBalance = sum(power*balance) / sum(power)

        # get session info
        entry   = EntryType.copy()
        entry['filename']   = filename
        entry['balance' ]   = PAvgBalance
        records = activity.get_records_by_type('session')
        for record in records:
            for field in session_fields:
                valid_field_names = record.get_valid_field_names()
                if field in valid_field_names:
                    value           = record.get_data(field)
                    unit            = record.get_units(field)
                    entry[field]    = (value, unit)
        datalist.append(entry)
        index   += 1
    print '.'

    import pickle
    DataFile    = open( DataFileName, 'wb')
    pickle.dump(datalist, DataFile)
    DataFile.close()
    print '%i entries written to %s' % (len(datalist), DataFileName)

else:

    # import the signals
    import pickle
    DataFile    = open( DataFileName, 'rb')
    datalist    = pickle.load(DataFile)
    DataFile.close()
    print '%i entries extracted from %s' % (len(datalist), DataFileName)

# end if ExtractData

TimerEnd    = time.time()
ExTime      = TimerEnd - TimerStart
mm  = ExTime // 60
ss  = ExTime % 60
print 'execution time = %02i:%02i' % (mm, ss)

#
# prepare plotting vectors
#
nDays   = len(datalist)
dates   = []
balance = zeros(nDays)
for i, entry in zip( range(nDays), datalist ):
    # index 0 is value, 1 is unit
    dates.append( entry['start_time'][0].date() )
    balance[i]  = entry['balance']


#
# plot
#
import matplotlib.dates as md
from matplotlib.dates import date2num, DateFormatter
x = date2num(dates) # Convert to matplotlib format
#fig1, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
fig1, ax0 = plt.subplots()
ax0.plot_date( x, list(balance),   'b+', markersize=4 );
ax0.plot_date( ftp_date_num, list(ftp_balance), 'go', markersize=12,
                mfc='green' );
ax0.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
fig1.autofmt_xdate()
ax0.legend(['all rides', 'FTP Tests'], loc='best')
ax0.grid(True)
fig1.suptitle('Power Balance Over Time', fontsize=20)
fig1.tight_layout()
plt.ylabel('Right Power Balance, %')
plt.show()

