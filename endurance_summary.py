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

def endurance_summary(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

    (FilePath, FitFileName) = os.path.split(FitFilePath)

    if ConfigFile is None:
        # attempt to find appropriate config file
        if 'will' in FilePath.split('\\'):
            ConfigFile = FilePath + r'\cyclingconfig_will.txt'
            print >> OutStream, 'ConfigFile:'
            print >> OutStream, ConfigFile
        elif 'kim' in FilePath.split('\\'):
            ConfigFile = FilePath + r'\cyclingconfig_kim.txt'
    if (ConfigFile is None) or (not os.path.exists(ConfigFile)):
        raise IOError('Configuration file not specified or found')

    #
    #   Parse the configuration file
    #
    from ConfigParser import ConfigParser
    # are we on the desktop or laptop?
#    if 'D' in FitFilePath.split('\\')[0]:
#        ConfigFilePath  = 'D:\\Users\\Owner\\Documents\\OneDrive\\2018\\fitfiles\\'
#    else:
#        ConfigFilePath  = 'S:\\will\\documents\\OneDrive\\2018\\fitfiles\\'
#    ConfigFile  = ConfigFilePath + 'cyclingconfig_will.txt'
    config      = ConfigParser()
    config.read(ConfigFile)
    print >> OutStream, 'reading config file ' + ConfigFile
    WeightEntry     = config.getfloat( 'user', 'weight' )
    WeightToKg      = config.getfloat( 'user', 'WeightToKg' )
    weight          = WeightEntry * WeightToKg
    age             = config.getfloat( 'user', 'age' )
    EndurancePower  = config.getfloat( 'power', 'EndurancePower' )
    ThresholdPower  = config.getfloat( 'power', 'ThresholdPower' )
    EnduranceHR     = config.getfloat( 'power', 'EnduranceHR'    )
    ThresholdHR     = config.getfloat( 'power', 'ThresholdHR'    )
    print >> OutStream, 'WeightEntry   : ', WeightEntry
    print >> OutStream, 'WeightToKg    : ', WeightToKg
    print >> OutStream, 'weight        : ', weight
    print >> OutStream, 'age           : ', age
    print >> OutStream, 'EndurancePower: ', EndurancePower
    print >> OutStream, 'ThresholdPower: ', ThresholdPower
    print >> OutStream, 'EnduranceHR   : ', EnduranceHR
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

    # get the FTP
    # FTP = 270.0 #assume if not present
    records = activity.get_records_by_type('zones_target')
    for record in records:
        valid_field_names = record.get_valid_field_names()
        for field_name in valid_field_names:
            if 'functional_threshold_power' in field_name:
                field_data = record.get_data(field_name)
                field_units = record.get_units(field_name)
                print >> OutStream, 'FTP setting = %i %s' % (field_data, field_units)
                FTP = field_data


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
    lap_ef          = zeros(nLaps)

    #time    = array(elapsed_time)
    cadence = array(avg_cadence)
    avg_hr  = array(avg_heart_rate)
    max_hr  = array(max_heart_rate)
    balance = array(balance)
    names1  = [    '', '  lap', '  avg', ' norm', 'avg',  'max',    '' ]
    names2  = [ 'lap', ' time', 'power', 'power', ' HR',  ' HR', ' EF' ]
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
        lap_avg_hr[i]       = average(heart_rate_vi[ii])
        lap_avg_power[i]    = average(power[time_idx[ii]])
        lap_norm_power[i]   = average( p30[time_idx[ii]]**4 )**(0.25)
        lap_ef[i]           = lap_norm_power[i] / lap_avg_hr[i]

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
                    lap_ef[i]           )

        # plot lap results as continuous time signals
        lap_avg_hr_c    [time_idx[ii]]  = lap_avg_hr[i]
        lap_avg_power_c [time_idx[ii]]  = lap_avg_power[i]
        lap_norm_power_c[time_idx[ii]]  = lap_norm_power[i]

    #
    # ride-level results
    #
    print >> OutStream, 'ride-level results:'
    names1  = [    '', 'moving', '  avg', ' norm', 'avg',    '',  'Pw:' ]
    names2  = [ 'seg', '  time', 'power', 'power', ' HR', ' EF',  ' HR' ]
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
    all_ef          = all_norm_power / all_avg_hr
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
                all_ef,
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
    mid_ef          = mid_norm_power / mid_avg_hr
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
                mid_ef,
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
    ax0.grid(True)
    ax0.set_title('heart rate, BPM')
    ax1.plot_date( x, power,            'k-', linewidth=1 );
    ax1.plot_date( x, p30,              'm-', linewidth=1);
    ax1.plot_date( x, lap_avg_power_c,  'b-', linewidth=3);
    ax1.plot_date( x, lap_norm_power_c, 'g-', linewidth=3);
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.set_yticks( p_zone_bounds, minor=False)
    ax1.grid(True)
    ax1.set_title('power, watts')
    fig1.autofmt_xdate()
    ax1.legend(['power', 'p30', 'lap_avg_power', 'lap_norm_power'],
                loc='upper left');
    fig1.suptitle('Endurance Power Results', fontsize=20)
    fig1.tight_layout()
    plt.show()

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


## workout summary
#mm = sum(time[ii]) // 60
#ss = sum(time[ii])  % 60
#print '%8s%5i:%02i%8d%8d%8d%8d%8.1f' \
#        % ("AVERAGE", mm, ss,
#            sum(  power[ii]*time[ii]) / sum(time[ii]),
#            sum( avg_hr[ii]*time[ii]) / sum(time[ii]),
#            max(max_hr[ii]),
#            sum(cadence[ii]*time[ii]) / sum(time[ii]),
#            sum(balance[ii]*time[ii]) / sum(time[ii]) )
##print "average interval power: %d watts" % (sum(power[ii]*time[ii]) / sum(time[ii]))
#
#                     avg     avg     max     avg     avg
#     lap    time   power      HR      HR     cad     bal
#       0   16:19     133     127     143      74    48.4
#       1   18:55     171     139     146      74    48.1
#       2   30:40     181     139     148      79    48.1
#       3   40:58     171     138     155      75    48.0
#       4   26:48     175     143     150      81    48.2
#       5   16:29     178     141     151      80    47.5
#       6    6:03      79     133     148      53    47.5
# AVERAGE  156:15     166     138     155      76    48.0
