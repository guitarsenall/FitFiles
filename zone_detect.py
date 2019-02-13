#!/usr/bin/env python

'''
zone_detect.py

Detect the power zone using time-in-zone thresholds.
That is, for example, one sample spent in zone 5 does NOT mean I am
actually in zone 5; I need to spend enough time there to qualify.
'''

import os
import sys

# a function to compute its centered boxcar average:
def CenteredBoxcarAverage( x, window=30, SampleRate=1.0 ):
    # compute the centered boxcar average
    from numpy import zeros, average
    nPts    = len(x)
    w       = 2*int(window*SampleRate/2)    # force even
    y       = zeros(nPts)
    for i in range(nPts):
        if i < nPts-w/2:
            y[i] = average(x[i : i+w/2])
        else:
            y[i] = average(x[i-w/2 : i+w/2])
    return y

# a function to compute its forward boxcar average:
def ForwardBoxcarAverage( x, window=30, SampleRate=1.0 ):
    # compute the forward 30-second power
    from numpy import zeros, average
    nPts    = len(x)
    w       = int(window*SampleRate)
    y       = zeros(nPts)
    for i in range(nPts):
        if i < nPts-w:
            y[i] = average(x[i:i+w])
        else:
            y[i] = average(x[i:])
    return y



############################################################
#               zone_detect function def                   #
############################################################

from activity_tools import FindConfigFile

def zone_detect(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

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
    print >> OutStream,  'ThresholdPower: ', ThresholdPower
    print >> OutStream,  'ThresholdHR   : ', ThresholdHR

    from datetime import datetime
    from fitparse import Activity
    from activity_tools import extract_activity_signals

    required_signals    = [ 'power' ] # 'heart_rate' optional

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

    hasHR = True if 'heart_rate' in signals.keys() else False

    # up-sample by 5x so that zone-skipping is not needed
    SampleRate  = 5.0
    from numpy import arange, interp
    n           = len(signals['power'])
    old_time    = arange(n)
    nPts        = int(n*SampleRate)  # 32-bit integer
    new_time    = arange(nPts)/SampleRate
    power       = interp(new_time, old_time, signals['power'])
    if hasHR:
        heart_rate  = interp(new_time, old_time, signals['heart_rate'])

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

    def LocateZone( x, zones ):
        Z   = 1
        if x >= zones[2][0]: Z = 2
        if x >= zones[3][0]: Z = 3
        if x >= zones[4][0]: Z = 4
        if x >= zones[5][0]: Z = 5
        if x >= zones[6][0]: Z = 6
        if x >= zones[7][0]: Z = 7
        return Z

    # define boxcar averages used to test for upward transition out of
    # indicated zone.
    fpZ1    = ForwardBoxcarAverage( power, window=90, SampleRate=SampleRate)
    fpZ2    = ForwardBoxcarAverage( power, window=60, SampleRate=SampleRate)
    fpZ3    = ForwardBoxcarAverage( power, window=45, SampleRate=SampleRate)
    fpZ4    = ForwardBoxcarAverage( power, window=30, SampleRate=SampleRate)
    fpZ5    = ForwardBoxcarAverage( power, window=15, SampleRate=SampleRate)
    fpZ6    = ForwardBoxcarAverage( power, window= 5, SampleRate=SampleRate)
    # fpZ7 not needed

    # assemble these into a dictionary:
    # so that I could test
    #     if LocateZone( FBoxCars[CurrentZone][i], pZones )
    #         > CurrentZone:
    FBoxCars = {    1 : fpZ1,
                    2 : fpZ2,
                    3 : fpZ3,
                    4 : fpZ4,
                    5 : fpZ5,
                    6 : fpZ6 }  # Z7 not needed

    # define boxcar averages used to test for downward transition into
    # indicated zone.
    cpZ1    = CenteredBoxcarAverage( power, window=60, SampleRate=SampleRate)
    cpZ2    = CenteredBoxcarAverage( power, window=45, SampleRate=SampleRate)
    cpZ3    = CenteredBoxcarAverage( power, window=30, SampleRate=SampleRate)
    cpZ4    = CenteredBoxcarAverage( power, window=15, SampleRate=SampleRate)
    cpZ5    = CenteredBoxcarAverage( power, window= 7, SampleRate=SampleRate)
    cpZ6    = CenteredBoxcarAverage( power, window= 3, SampleRate=SampleRate)
    # fpZ7 not needed

    # assemble these into a dictionary:
    # so that I could test
    #     if LocateZone( CBoxCars[CurrentZone][i], pZones )
    #         > CurrentZone:
    CBoxCars = {    1 : cpZ1,
                    2 : cpZ2,
                    3 : cpZ3,
                    4 : cpZ4,
                    5 : cpZ5,
                    6 : cpZ6 }  # Z7 not needed

    from numpy import array, arange, append, zeros, cumsum, average

    cp2         = zeros(nPts)
    fboxpower   = zeros(nPts)
    cboxpower   = zeros(nPts)
    zone        = zeros(nPts)
    zone_mid    = zeros(nPts)
    CurrentZone = 1

    # create a phaseless, lowpass-filtered signal for downward transitions
    # see
    #   https://docs.scipy.org/doc/scipy/reference/signal.html
    from scipy import signal
    poles       = 4
    cutoff      = 0.1     # Hz
    Wn          = cutoff / (SampleRate/2)
    PadLen      = int(SampleRate/cutoff)
    b, a        = signal.butter(poles, Wn, btype='lowpass')
    # lpfpower    = signal.filtfilt(b, a, power, padlen=PadLen)


    #   calculate zone midpoints for plotting
    ZoneMidPoint    = {}    # empty dictionary
    ZoneMidPoint[1] = (pZones[1][0]+pZones[1][1]) / 2
    ZoneMidPoint[2] = (pZones[2][0]+pZones[2][1]) / 2
    ZoneMidPoint[3] = (pZones[3][0]+pZones[3][1]) / 2
    ZoneMidPoint[4] = (pZones[4][0]+pZones[4][1]) / 2
    ZoneMidPoint[5] = (pZones[5][0]+pZones[5][1]) / 2
    ZoneMidPoint[6] = (pZones[6][0]+pZones[6][1]) / 2
    ZoneMidPoint[7] = (pZones[7][0]+pZones[7][1]) / 2

    for i, p in zip( range(nPts), power ):

        #   compute the centered 3-second power
        #raise RuntimeError("need to account for sample rate in cp2")
        sr  = int(SampleRate)
        if i == 0:
            cp2[i]  = power[i]
        elif i < 2*sr:
            cp2[i] = average( power[0:i] )
        elif i > nPts-2*sr:
            cp2[i] = average( power[i-sr:] )
        else:
            cp2[i] = average( power[i-sr:i+sr+1] )

        #   upward transition
        cz = CurrentZone    # short name
        if cz < 7:
            tz = 7  # Test Zone
            while tz > cz:
                if  (LocateZone(           cp2[i], pZones ) >= tz) \
                  & (LocateZone( FBoxCars[tz-1][i], pZones ) >= tz):
                    CurrentZone = tz
                    zone[i]     = CurrentZone
                    break
                tz -= 1
        #   downward transition. Avoid 2nd test if in Z1.
        #   use centered-boxcar average to avoid getting "trapped"
        #   in low zones.
        if cz > 1:
            tz = cz-1
            while tz >= 1:
                if  (LocateZone(          cp2[i], pZones ) <= tz) \
                  & (LocateZone( CBoxCars[tz][i], pZones ) <= tz) \
                  & (LocateZone( FBoxCars[tz][i], pZones ) <= tz):
                    CurrentZone = tz
                    zone[i]     = CurrentZone
                    break
                tz -= 1

        # the filtered power comes from CurrentZone after any transition
        fboxpower[i] = FBoxCars[min(CurrentZone  ,6)][i]
        cboxpower[i] = CBoxCars[max(CurrentZone-1,1)][i]

        #   calculate zone midpoints for plotting
        zone_mid[i] = ZoneMidPoint[CurrentZone]

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

    # time plot with heart rate
    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    from matplotlib.dates import date2num, DateFormatter
    import datetime as dt
    base = dt.datetime(2014, 1, 27, 0, 0, 0)
    x = [base + dt.timedelta(seconds=t) for t in new_time]
    x = date2num(x) # Convert to matplotlib format
    if hasHR:
        fig1, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
        ax0.plot_date( x, heart_rate, 'r-', linewidth=3 );
        ax0.set_yticks( h_zone_bounds, minor=False)
        ax0.grid(True)
        ax0.set_title('heart rate, BPM')
    else:
        fig1, ax1 = plt.subplots(nrows=1, sharex=True)
    ax1.plot_date( x, power,        'k-', linewidth=1 );
    ax1.plot_date( x, fboxpower,    'm-', linewidth=1);
    ax1.plot_date( x, cp2,          'r.', markersize=4);
    ax1.plot_date( x, cboxpower,    'b-', linewidth=1);
    ax1.plot_date( x, zone_mid,     'g-', linewidth=3);
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.set_yticks( p_zone_bounds, minor=False)
    ax1.grid(True)
    ax1.set_title('power, watts')
    fig1.autofmt_xdate()
    ax1.legend(['power', 'FBoxCar', 'cp2', 'CBoxCar', 'zone mid'],
                loc='upper left');
    fig1.suptitle('Power Zone Detection', fontsize=20)
    fig1.tight_layout()
    fig1.canvas.set_window_title(FitFilePath)
    plt.show()

    # better histogram plot with control of counts
    from numpy import histogram
    PowerCounts, PowerBins = histogram(power, bins=p_zone_bounds)
    ZoneCounts,   ZoneBins = histogram(zone_mid, bins=p_zone_bounds)
    fig2, ax = plt.subplots()
    bar_width = 0.35
    opacity = 0.4
    #error_config = {'ecolor': '0.3'}
    zone_ints   = arange(7)+1
    LogY = True
    rects1 = ax.bar(zone_ints, PowerCounts/SampleRate/60,
                    bar_width, alpha=opacity, color='b', log=LogY,
                    label='raw power')
    rects2 = ax.bar(zone_ints+bar_width, ZoneCounts/SampleRate/60,
                    bar_width, alpha=opacity, color='r', log=LogY,
                    label='detected zone')
    ax.set_xlabel('Zone')
    ax.set_ylabel('minutes')
    ax.set_title('Zone Detection Histogram')
    ax.set_xticks(zone_ints + bar_width / 2)
    ax.set_xticklabels(('Rec', 'End', 'Tmp', 'Thr', 'VO2', 'An', 'NM'))
    ax.legend()
    fig2.tight_layout()
    fig2.canvas.set_window_title(FitFilePath)
    plt.show()

    # formatted print of histogram
    print >> OutStream, 'Power Zone Histogram:'
    for i in range(7):
        dur = ZoneCounts[i]/SampleRate
        pct = dur / sum( ZoneCounts/SampleRate ) * 100
        hh  = dur // 3600
        mm  = (dur % 3600) // 60
        ss  = (dur % 3600) % 60
        print >> OutStream, '    Zone %i: %2i:%02i:%02i (%2i%%)' \
                            % (i+1, hh, mm, ss, pct)
    dur = sum(ZoneCounts)/SampleRate
    hh  = dur // 3600
    mm  = (dur % 3600) // 60
    ss  = (dur % 3600) % 60
    print >> OutStream, '     total: %2i:%02i:%02i' % (hh, mm, ss)

    def ClosePlots():
        plt.close('all')

    return ClosePlots

# end zone_detect()

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
        zone_detect(fitfilepath, ConfigFile=None)
    else:
        raise IOError('Need a .FIT file')

    # good example
    #FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
    #            + r'2018-10-18-18-26-53.fit'

    # sample without HR
    #FitFilePath = r'D:\Users\Owner\Documents\OneDrive\bike\activities\will\\' \
    #            + r'2018-12-22-16-28-06.fit'

# SAMPLE OUTPUT:
#
#    CWD: D:\Users\Owner\Documents\OneDrive\bike\activities\will
#    PATH: D:\Users\Owner\Documents\OneDrive\bike\activities\will
#    FILE: 2018-10-18-18-26-53.fit
#
#    -------------------- Zone Detection --------------------
#
#    reading config file cyclingconfig_will.txt
#    WeightEntry   :  190.0
#    WeightToKg    :  0.45359237
#    weight        :  86.1825503
#    age           :  52.0
#    EndurancePower:  175.0
#    ThresholdPower:  250.0
#    EnduranceHR   :  140.0
#    ThresholdHR   :  170.0
#    Power Zone Histogram:
#        Zone 1:  0:12:05 (14%)
#        Zone 2:  0:09:39 (11%)
#        Zone 3:  0:21:41 (26%)
#        Zone 4:  0:32:16 (39%)
#        Zone 5:  0:03:39 ( 4%)
#        Zone 6:  0:00:57 ( 1%)
#        Zone 7:  0:00:49 ( 1%)
#         total:  1:21:09
