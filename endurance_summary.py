#!/usr/bin/env python

'''
endurance_summary.py

Print a formatted table of metrics from each lap along with a summary
of the endurance ride omitting the first and last laps (warmup and cooldown).

'''

import os
import sys

#
# create running 30-second average power from which normalized power
# can be computed
#

def BackwardMovingAverage( x, window=30, SampleRate=1.0 ):
    # a function to compute its backward moving average:
    from numpy import zeros, average
    nPts    = len(x)
    w       = int(window*SampleRate)
    y       = zeros(nPts)
    for i in range(nPts):
        if i < w:
            y[i] = average(x[:i+1])         # include i
        else:
            y[i] = average(x[i-w:i+1])      # include i
    return y

############################################################
#           endurance_summary function def                 #
############################################################

from activity_tools import FindConfigFile

def endurance_summary(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

    (FilePath, FitFileName) = os.path.split(FitFilePath)

    if ConfigFile is None:
        ConfigFile = FindConfigFile('', FilePath)
    if (ConfigFile is None) or (not os.path.exists(ConfigFile)):
        raise IOError('Configuration file not specified or found')

    #
    #   Parse the configuration file
    #
    from ConfigParser import ConfigParser
    config      = ConfigParser()
    config.read(ConfigFile)
    print >> OutStream, 'reading config file ' + ConfigFile
    ThresholdPower  = config.getfloat( 'power', 'ThresholdPower' )
    ThresholdHR     = config.getfloat( 'power', 'ThresholdHR'    )
    print >> OutStream, 'ThresholdPower: ', ThresholdPower
    print >> OutStream, 'ThresholdHR   : ', ThresholdHR

    # power zones from "Cyclist's Training Bible", 5th ed., by Joe Friel, p51
    FTP = ThresholdPower
    pZones  = { 1   : [    0    ,   0.55*FTP ],
                2   : [ 0.55*FTP,   0.75*FTP ],
                3   : [ 0.75*FTP,   0.90*FTP ],
                4   : [ 0.90*FTP,   1.05*FTP ],
                5   : [ 1.05*FTP,   1.20*FTP ],
                6   : [ 1.20*FTP,   1.50*FTP ],
                7   : [ 1.50*FTP,   2.50*FTP ]}

    # heart-rate zones from "Cyclist's Training Bible" 5th ed. by Joe Friel, p50
    FTHR = ThresholdHR
    hZones  = { 1   : [     0    ,   0.82*FTHR ],  # 1
                2   : [ 0.82*FTHR,   0.89*FTHR ],  # 2
                3   : [ 0.89*FTHR,   0.94*FTHR ],  # 3
                4   : [ 0.94*FTHR,   1.00*FTHR ],  # 4
                5   : [ 1.00*FTHR,   1.03*FTHR ],  # 5a
                6   : [ 1.03*FTHR,   1.06*FTHR ],  # 5b
                7   : [ 1.07*FTHR,   1.15*FTHR ]}  # 5c

    # get zone bounds for plotting
    p_zone_bounds   = [ pZones[1][0],
                        pZones[2][0],
                        pZones[3][0],
                        pZones[4][0],
                        pZones[5][0],
                        pZones[6][0],
                        pZones[7][0],
                        pZones[7][1] ]

    h_zone_bounds   = [     0.4*FTHR,   # better plotting
                        hZones[2][0],
                        hZones[3][0],
                        hZones[4][0],
                        hZones[5][0],
                        hZones[6][0],
                        hZones[7][0],
                        hZones[7][1] ]


    from datetime import datetime
    from fitparse import Activity
    from activity_tools import extract_activity_signals

    required_signals    = [ 'power',
                            'heart_rate' ]

    # get the signals
    activity = Activity(FitFilePath)
    signals     = extract_activity_signals(activity, resample='existing')

    if not all( s in signals.keys() for s in required_signals ):
        msg = 'required signals not in file'
        print >> OutStream, msg
        print >> OutStream, 'Signals required:'
        for s in required_signals:
            print >> OutStream, '   ' + s
        print >> OutStream, 'Signals contained:'
        for s in signals.keys():
            print >> OutStream, '   ' + s
        raise IOError(msg)

    '''
    ####################
    # Get Records of type 'lap'
    # types: [ 'record', 'lap', 'event', 'session', 'activity', ... ]
    records = activity.get_records_by_type('lap')
    current_record_number = 0

    elapsed_time    = []
    timer_time      = []
    avg_heart_rate  = []
    avg_power       = []
    avg_cadence     = []
    max_heart_rate  = []
    balance         = []
    lap_timestamp   = []
    lap_start_time  = []

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
            #    print >> OutStream, " * %s: %s %s" % (field_name, field_data, field_units)
            #else:
            #    print >> OutStream, " * %s: %s" % (field_name, field_data)

            if 'timestamp' in field_name:
                lap_timestamp.append( field_data )

            if 'start_time' in field_name:
                lap_start_time.append( field_data )

            if 'total_elapsed_time' in field_name:
                elapsed_time.append( field_data )

            if 'total_timer_time' in field_name:
                timer_time.append( field_data )

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
    ####################
    '''

    #
    #   extract lap results
    #
    from fitparse import Activity
    from activity_tools import extract_activity_laps
    import numpy as np
    activity    = Activity(FitFilePath)
    laps        = extract_activity_laps(activity)
    avg_power       = laps['power']
    time            = laps['time']
    cadence         = laps['cadence']
    avg_heart_rate  = laps['avg_hr']
    max_heart_rate  = laps['max_hr']
    balance         = laps['balance']
    lap_start_time  = laps['start_time']
    lap_timestamp   = laps['timestamp' ]
    timer_time      = laps['total_timer_time']
    elapsed_time    = laps['total_elapsed_time']


    IntervalThreshold = 0.0     # get all laps (0.72*FTP)
    from numpy import nonzero, array, arange, zeros, average, logical_and

    # resample power to constant-increment (1 Hz) with zeros at missing samples
    time_idx                = signals['time'].astype('int')
    power_vi                = signals['power']
    heart_rate_vi           = signals['heart_rate']
    nScans                  = time_idx[-1]+1
    time_ci                 = arange(nScans)
    power                   = zeros(nScans)
    power[time_idx]         = power_vi
    heart_rate_ci           = zeros(nScans)
    heart_rate_ci[time_idx] = heart_rate_vi

    t0 = signals['metadata']['timestamp']
    print >> OutStream, 'signal timestamp: ', t0.time()

    # plot lap results as continuous time signals
    lap_avg_hr_c        = zeros(nScans)
    lap_avg_power_c     = zeros(nScans)
    lap_norm_power_c    = zeros(nScans)

    # compute the 30-second, moving-average power signal.
    p30 = BackwardMovingAverage( power )

    #
    # compute lap metrics
    #
    print >> OutStream, 'lap results:'
    nLaps   = len(elapsed_time)
    vi_time_vector  = signals['time']

    lap_avg_power   = zeros(nLaps)
    lap_norm_power  = zeros(nLaps)
    lap_avg_hr      = zeros(nLaps)
    lap_if          = zeros(nLaps)      # intensity factor
    lap_start_sec   = zeros(nLaps)      # lap start times in seconds

    #time    = array(elapsed_time)
    #cadence = array(avg_cadence)
    #avg_hr  = array(avg_heart_rate)
    #max_hr  = array(max_heart_rate)
    #balance = array(balance)
    names1  = [    '', '  lap', '  avg', ' norm', 'avg',  'max',    '' ]
    names2  = [ 'lap', ' time', 'power', 'power', ' HR',  ' HR', ' IF' ]
    fmt     = "%8s"+"%10s"+"%8s"*5
    print >> OutStream, fmt % tuple(names1)
    print >> OutStream, fmt % tuple(names2)

    for i in range(nLaps):
        # count samples in this lap
        tBeg = (lap_start_time[i] - t0).total_seconds()
        tEnd = (lap_timestamp[i]  - t0).total_seconds()
        ii = nonzero( logical_and( time_idx >= tBeg,  \
                                   time_idx <  tEnd)  )[0]
        nPts = ii.size
        lap_start_sec[i]    = tBeg
        lap_avg_hr[i]       = average(heart_rate_vi[ii])
        lap_avg_power[i]    = average(power[time_idx[ii]])
        lap_norm_power[i]   = average( p30[time_idx[ii]]**4 )**(0.25)
        lap_if[i]           = lap_norm_power[i] / FTP

        # duration from lap metrics
        dur = (lap_timestamp[i] - lap_start_time[i]).total_seconds()
        mm = timer_time[i] // 60
        ss = timer_time[i]  % 60
        fmt = '%8d'+'%7i:%02i'+'%8i'*4 + '%8.2f'
        print >> OutStream, fmt \
                % ( i,
                    mm, ss,
                    avg_power[i],
                    lap_norm_power[i],
                    avg_heart_rate[i],
                    max_heart_rate[i],
                    lap_if[i]           )

        # plot lap results as continuous time signals
        lap_avg_hr_c    [time_idx[ii]]  = lap_avg_hr[i]
        lap_avg_power_c [time_idx[ii]]  = lap_avg_power[i]
        lap_norm_power_c[time_idx[ii]]  = lap_norm_power[i]

    #
    # ride-level results
    #
    print >> OutStream, 'ride-level results:'
    names1  = [    '', 'moving', '  avg', ' norm', 'avg',    '',  'Pw:' ]
    names2  = [ 'seg', '  time', 'power', 'power', ' HR', ' IF',  ' HR' ]
    fmt     = "%8s"+"%10s"+"%8s"*5
    print >> OutStream, fmt % tuple(names1)
    print >> OutStream, fmt % tuple(names2)

    # whole ride
    tBeg = (lap_start_time[0] - t0).total_seconds()
    tEnd = (lap_timestamp[-1] - t0).total_seconds()
    ii = nonzero( logical_and( time_idx >= tBeg,  \
                               time_idx <  tEnd)  )[0]
    nPts = ii.size
    dur = nPts  # sample rate 1 Hz
    hh  = dur // 3600
    mm  = (dur % 3600) // 60
    ss  = (dur % 3600) % 60
    all_avg_hr      = average(heart_rate_vi[ii])
    all_avg_power   = average(power_vi[ii])
    all_norm_power  = average( p30[time_idx[ii]]**4 )**(0.25)
    all_max_hr      = max(heart_rate_vi[ii])
    all_if          = all_norm_power / FTP
    # aerobic decoupling
    iiH1            = ii[0:nPts/2]
    h1_norm_power   = average( p30[time_idx[iiH1]]**4 )**(0.25)
    h1_avg_hr       = average(heart_rate_vi[iiH1])
    h1ef            = h1_norm_power / h1_avg_hr
    iiH2            = ii[nPts/2:]
    h2_norm_power   = average( p30[time_idx[iiH2]]**4 )**(0.25)
    h2_avg_hr       = average(heart_rate_vi[iiH2])
    h2ef            = h2_norm_power / h2_avg_hr
    all_pw_hr       = (h1ef-h2ef)/(h1ef)*100.0
    fmt = '%8s'+'%4i:%02i:%02i'+'%8i'*3 + '%8.2f' + '%8.1f'
    print >> OutStream, fmt \
            % ( 'all',
                hh, mm, ss,
                all_avg_power,
                all_norm_power,
                all_avg_hr,
                all_if,
                all_pw_hr          )

    # without end laps
    tBeg = (lap_start_time[1] - t0).total_seconds()
    tEnd = (lap_timestamp[-2] - t0).total_seconds()
    ii = nonzero( logical_and( time_idx >= tBeg,  \
                               time_idx <  tEnd)  )[0]
    nPts = ii.size
    dur = nPts  # sample rate 1 Hz
    hh  = dur // 3600
    mm  = (dur % 3600) // 60
    ss  = (dur % 3600) % 60
    mid_avg_hr      = average(heart_rate_vi[ii])
    mid_avg_power   = average(power_vi[ii])
    mid_norm_power  = average( p30[time_idx[ii]]**4 )**(0.25)
    mid_max_hr      = max(heart_rate_vi[ii])
    mid_if          = mid_norm_power / FTP
    # aerobic decoupling
    iiH1            = ii[0:nPts/2]
    h1_norm_power   = average( p30[time_idx[iiH1]]**4 )**(0.25)
    h1_avg_hr       = average(heart_rate_vi[iiH1])
    h1ef            = h1_norm_power / h1_avg_hr
    iiH2            = ii[nPts/2:]
    h2_norm_power   = average( p30[time_idx[iiH2]]**4 )**(0.25)
    h2_avg_hr       = average(heart_rate_vi[iiH2])
    h2ef            = h2_norm_power / h2_avg_hr
    mid_pw_hr       = (h1ef-h2ef)/(h1ef)*100.0
    fmt = '%5i-%02i'+'%4i:%02i:%02i'+'%8i'*3 + '%8.2f' + '%8.1f'
    print >> OutStream, fmt \
            % ( 1, nLaps-2,
                hh, mm, ss,
                mid_avg_power,
                mid_norm_power,
                mid_avg_hr,
                mid_if,
                mid_pw_hr          )

    print
    print

    #
    # time plot
    #

    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    from matplotlib.dates import date2num, DateFormatter
    import datetime as dt
    base = dt.datetime(2014, 1, 1, 0, 0, 0)
    x = [base + dt.timedelta(seconds=t) for t in time_ci.astype('float')]
    x = date2num(x) # Convert to matplotlib format
    fig1, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
    ax0.plot_date( x, heart_rate_ci, 'r-', linewidth=1 );
    ax0.plot_date( x, lap_avg_hr_c,  'r-', linewidth=3 );
    ax0.set_yticks( h_zone_bounds, minor=False)
    x_laps  = [ base + dt.timedelta(seconds=t)   \
                for t in lap_start_sec.astype('float') ]
    x_laps  = date2num(x_laps)
    for i in range(nLaps):
        ax0.axvline( x_laps[i], label=str(i+1) )
    ax0.grid(True)
    ax0.set_ylabel('heart rate, BPM')
    ax1.plot_date( x, power,            'k-', linewidth=1 );
    ax1.plot_date( x, p30,              'm-', linewidth=1);
    ax1.plot_date( x, lap_avg_power_c,  'b-', linewidth=3);
    ax1.plot_date( x, lap_norm_power_c, 'g-', linewidth=3);
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.set_yticks( p_zone_bounds, minor=False)
    for i in range(nLaps):
        ax1.axvline( x_laps[i], label=str(i+1) )
    ax1.grid(True)
    ax1.set_ylabel('power, watts')
    fig1.autofmt_xdate()
    ax1.legend(['power', 'p30', 'lap_avg_power', 'lap_norm_power'],
                loc='upper left');
    fig1.suptitle('Endurance Power Results', fontsize=20)
    fig1.tight_layout()
    fig1.subplots_adjust(hspace=0)   # Remove horizontal space between axes
    fig1.canvas.set_window_title(FitFilePath)
    plt.show()

    def ClosePlots():
        plt.close('all')

    return ClosePlots

# end endurance_summary()

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
        endurance_summary(fitfilepath, ConfigFile=None)
    else:
        raise IOError('Need a .FIT file')

    #FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
    #            + r'2018-11-22-11-02-30.fit'

# SAMPLE OUTPUT
#    CWD: D:\Users\Owner\Documents\OneDrive\bike\activities\will
#    PATH: D:\Users\Owner\Documents\OneDrive\bike\activities\will
#    FILE: 2018-11-22-11-02-30.fit
#
#    -------------------- Endurance Laps --------------------
#
#    reading config file D:\Users\Owner\Documents\OneDrive\2018\fitfiles\cyclingconfig_will.txt
#    WeightEntry   :  190.0
#    WeightToKg    :  0.45359237
#    weight        :  86.1825503
#    age           :  52.0
#    EndurancePower:  175.0
#    ThresholdPower:  250.0
#    EnduranceHR   :  140.0
#    ThresholdHR   :  170.0
#    FTP setting = 260 None
#    signal timestamp:  11:02:30
#    lap results:
#                   lap     avg    norm     avg     max
#         lap      time   power   power      HR      HR      EF
#           0      6:58     178     179     121     132    1.49
#           1     11:53     190     199     135     149    1.48
#           2     18:20     181     189     140     148    1.35
#           3     18:08     180     187     141     149    1.33
#           4     18:28     170     183     139     147    1.32
#           5     13:43     190     196     143     151    1.37
#           6      3:10      69     138     133     151    1.04
#    ride-level results:
#                moving     avg    norm     avg             Pw:
#         seg      time   power   power      HR      EF      HR
#         all   1:30:44     176     188     138    1.37     5.2
#        1-05   1:20:34     180     190     139    1.36     3.2
