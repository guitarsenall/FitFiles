#!/usr/bin/env python

'''
plot_heartrate.py

# Sample usage of python-fitparse to parse an activity and
# print its data records.
'''

import sys
import os

############################################################
#              plot_heartrate function def                 #
############################################################

def plot_heartrate(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

    verbose = False

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
    ConfigFile  = 'cyclingconfig_will.txt'
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
    print >> OutStream,  'WeightEntry   : ', WeightEntry
    print >> OutStream,  'WeightToKg    : ', WeightToKg
    print >> OutStream,  'weight        : ', weight
    print >> OutStream,  'age           : ', age
    print >> OutStream,  'EndurancePower: ', EndurancePower
    print >> OutStream,  'ThresholdPower: ', ThresholdPower
    print >> OutStream,  'EnduranceHR   : ', EnduranceHR
    print >> OutStream,  'ThresholdHR   : ', ThresholdHR

    from datetime import datetime
    from fitparse import Activity
    from activity_tools import extract_activity_signals

    required_signals    = [ 'heart_rate' ]

    # get the signals
    activity    = Activity(FitFilePath)
    signals     = extract_activity_signals(activity)

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

    time_signal         = signals['time']
    heartrate_signal    = signals['heart_rate']

    # plot the heart rate
    import numpy as np

    ########################################################################
    ###         Compute Calories                                         ###
    ########################################################################

    '''
    Formula widely available. One site:
        https://www.easycalculation.com/formulas/heart-rate-calorie-burn.html

        For Male,
        Calorie Burned = (  (   -55.0969
                                + (0.6309 x HR)
                                + (0.1988 x W )
                                + (0.2017 x A )  )
                            / 4.184) x 60 x T

        For Female,
        Calorie Burned = (  (   -20.4022
                                + (0.4472 x HR)
                                + (0.1263 x W )
                                + (0.0740 x A )  )
                            / 4.184) x 60 x T

        Where,
        HR  = Heart Rate
        W   = Weight in kilograms
        A   = Age
        T   = Exercise duration time in hours
    '''

    #   calibration at endurance
    EnduranceBurn   = EndurancePower*3600/1e3/60    # Cal/min
    EnduranceCoef   = EnduranceBurn                     \
                    / (   -55.0969 + 0.6309*EnduranceHR \
                        + 0.1988*weight + 0.2017*age)   \
                    * 4.184

    #   calibration at threshold
    ThresholdBurn   = ThresholdPower*3600/1e3/60    # Cal/min
    ThresholdCoef   = ThresholdBurn                     \
                    / (   -55.0969 + 0.6309*ThresholdHR \
                        + 0.1988*weight + 0.2017*age)   \
                    * 4.184

    hr_sig      = signals['heart_rate']
    t_sig       = signals['time']
    dt_sig      = np.append( np.array([1.0]),
                             t_sig[1:] - t_sig[0:-1] )
    nPts        = t_sig.size
    calories    = np.zeros(nPts)

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

    running_calories    = np.cumsum( calories )

    print >> OutStream,  'total calories = %i' % running_calories[nPts-1]

    ########################################################################
    ###         Zone Histogram                                           ###
    ########################################################################

    # heart-rate zones from "Cyclist's Training Bible" 5th ed. by Joe Friel, p50
    FTHR = ThresholdHR
    hZones  = { 1   : ([     0    ,   0.82*FTHR ],  ' 1' ),
                2   : ([ 0.82*FTHR,   0.89*FTHR ],  ' 2' ),
                3   : ([ 0.89*FTHR,   0.94*FTHR ],  ' 3' ),
                4   : ([ 0.94*FTHR,   1.00*FTHR ],  ' 4' ),
                5   : ([ 1.00*FTHR,   1.03*FTHR ],  '5a' ),
                6   : ([ 1.03*FTHR,   1.06*FTHR ],  '5b' ),
                7   : ([ 1.07*FTHR,   1.15*FTHR ],  '5c' )}
    h_zone_bounds   = [     0.4*FTHR,       #  1 lo
                        hZones[2][0][0],    #  2 lo
                        hZones[3][0][0],    #  3 lo
                        hZones[4][0][0],    #  4 lo
                        hZones[5][0][0],    # 5a lo
                        hZones[6][0][0],    # 5b lo
                        hZones[7][0][0],    # 5c lo
                        hZones[7][0][1] ]   # 5c hi
    h_zone_labels   = [ hZones[k][1] for k in range(1,8) ]

    ZoneCounts, ZoneBins    = np.histogram( hr_sig, bins=h_zone_bounds )

    # formatted print of histogram
    SampleRate  = 1.0
    print >> OutStream, 'Heart-Rate Zone Histogram:'
    for i in range(7):
        dur = ZoneCounts[i]/SampleRate
        pct = dur / sum( ZoneCounts/SampleRate ) * 100
        hh  = dur // 3600
        mm  = (dur % 3600) // 60
        ss  = (dur % 3600) % 60
        print >> OutStream, '    Zone %2s: %2i:%02i:%02i (%2i%%)' \
                            % ( h_zone_labels[i], hh, mm, ss, pct)
    dur = sum(ZoneCounts)/SampleRate
    hh  = dur // 3600
    mm  = (dur % 3600) // 60
    ss  = (dur % 3600) % 60
    print >> OutStream, '      total: %2i:%02i:%02i' % (hh, mm, ss)


    ###########################################################
    ###             plotting                                ###
    ###########################################################

    # plot heart rate and calories
    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    from matplotlib.dates import date2num, DateFormatter
    import datetime as dt
    base = dt.datetime(2014, 1, 27, 0, 0, 0)
    x = [base + dt.timedelta(seconds=t) for t in t_sig]
    x = date2num(x) # Convert to matplotlib format
    fig1, ax0 = plt.subplots()
    ax0.plot_date( x, hr_sig, 'r-', linewidth=3 );
    ax0.set_yticks( h_zone_bounds, minor=False)
    ax0.grid(True)
    ax0.set_title('heart rate, BPM')
    ax0.set_title('Heart Rate Analysis')
    fig1.autofmt_xdate()
    fig1.tight_layout()
    plt.show()

    #    plt.plot(t_sig/60, hr_sig, 'r.-')
    #    plt.title('Heart Rate and Calories')
    #    plt.ylabel('BPM')
    #    plt.subplot(2, 1, 2)
    #    plt.plot(t_sig/60, running_calories, 'b.-')
    #    plt.xlabel('time (min)')
    #    plt.ylabel('calories')

    # heart rate histogram plot
    fig2, ax2 = plt.subplots()
    bar_width = 0.80    # 0.35
    opacity = 0.4
    #error_config = {'ecolor': '0.3'}
    zone_ints   = np.arange(7)+1
    LogY = False
    rects1 = ax2.bar(zone_ints+bar_width/2, ZoneCounts/SampleRate/60,
                    bar_width, alpha=opacity, color='r', log=LogY,
                    label='heart rate')
    ax2.set_xlabel('Zone')
    ax2.set_ylabel('minutes')
    ax2.set_title('Heart Rate Zone Histogram')
    ax2.set_xticks(zone_ints + bar_width / 2)
    ax2.set_xticklabels(h_zone_labels)
    ax2.legend()
    fig2.tight_layout()
    plt.show()



# end plot_heartrate()

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
        plot_heartrate(fitfilepath, ConfigFile=None)
    else:
        raise IOError('Need a .FIT file')

    #FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
    #            + r'2018-12-02-13-13-19.fit'

