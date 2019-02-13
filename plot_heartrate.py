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

from activity_tools import FindConfigFile

def plot_heartrate(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

    verbose = False

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
    WeightEntry     = config.getfloat( 'user', 'weight' )
    WeightToKg      = config.getfloat( 'user', 'WeightToKg' )
    weight          = WeightEntry * WeightToKg
    age             = config.getfloat( 'user', 'age' )
    sex             = config.get(      'user', 'sex' )
    EndurancePower  = config.getfloat( 'power', 'EndurancePower' )
    ThresholdPower  = config.getfloat( 'power', 'ThresholdPower' )
    EnduranceHR     = config.getfloat( 'power', 'EnduranceHR'    )
    ThresholdHR     = config.getfloat( 'power', 'ThresholdHR'    )
    HRTimeConstant  = config.getfloat( 'power', 'HRTimeConstant' )
    HRDriftRate     = config.getfloat( 'power', 'HRDriftRate'    )
    print >> OutStream,  'WeightEntry   : ', WeightEntry
    print >> OutStream,  'WeightToKg    : ', WeightToKg
    print >> OutStream,  'weight        : ', weight
    print >> OutStream,  'age           : ', age
    print >> OutStream,  'sex           : ', sex
    print >> OutStream,  'EndurancePower: ', EndurancePower
    print >> OutStream,  'ThresholdPower: ', ThresholdPower
    print >> OutStream,  'EnduranceHR   : ', EnduranceHR
    print >> OutStream,  'ThresholdHR   : ', ThresholdHR
    print >> OutStream, 'HRTimeConstant : ', HRTimeConstant
    print >> OutStream, 'HRDriftRate    : ', HRDriftRate

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

    However, the formula is adapted to the user's power capacity:
        :   At EnduranceHR, CalPerMin is set to EndurancePower
            (assuming efficiency of 1/4.184 so that calories burned
            equal kJ expended).
        :   At ThresholdHR, CalPerMin is set to ThresholdPower.
        :   Between EnduranceHR and ThresholdHR, CalPerMin is
            interpolated.
        :   Below EnduranceHR, CalPerMin follows the formula, but
            it is scaled onto [EnduranceHR, EndurancePower].
        :   Above ThresholdHR, CalPerMin follows the formula, but
            it is scaled onto [ThresholdHR, ThresholdPower].

    '''

    hr_sig      = signals['heart_rate']
    t_sig       = signals['time']
    dt_sig      = np.append( np.array([1.0]),
                             t_sig[1:] - t_sig[0:-1] )
    nPts        = t_sig.size
    calories    = np.zeros(nPts)

    EnduranceBurn   = EndurancePower*3600/1e3/60    # Cal/min
    print >> OutStream,  'EnduranceBurn = %5.2f cal/min' % EnduranceBurn
    ThresholdBurn   = ThresholdPower*3600/1e3/60    # Cal/min
    print >> OutStream,  'ThresholdBurn = %5.2f cal/min' % ThresholdBurn


    if sex == 'male':

        #   calibration at endurance
        EnduranceCoef   = EnduranceBurn             \
                        / ( -55.0969                \
                            + 0.6309*EnduranceHR    \
                            + 0.1988*weight         \
                            + 0.2017*age)           \
                        * 4.184

        #   calibration at threshold
        ThresholdCoef   = ThresholdBurn             \
                        / ( -55.0969                \
                            + 0.6309*EnduranceHR    \
                            + 0.1988*weight         \
                            + 0.2017*age)           \
                        * 4.184

    else:   # female

        #   calibration at endurance
        EnduranceCoef   = EnduranceBurn             \
                        / ( -20.4022                \
                            + 0.4472*EnduranceHR    \
                            + 0.1263*weight         \
                            + 0.0740*age)           \
                        * 4.184

        #   calibration at threshold
        ThresholdCoef   = ThresholdBurn             \
                        / ( -20.4022                \
                            + 0.4472*EnduranceHR    \
                            + 0.1263*weight         \
                            + 0.0740*age)           \
                        * 4.184


    for i, dt, HR in zip( range(nPts), dt_sig, hr_sig ):

        # calories per minute
        if HR >= EnduranceHR and HR <= ThresholdHR:
            CalPerMin   = EnduranceBurn                 \
                        + (HR-EnduranceHR)              \
                        * (ThresholdBurn-EnduranceBurn) \
                        / (ThresholdHR-EnduranceHR)
        else:
            coef = EnduranceCoef if (HR < EnduranceHR) else ThresholdCoef
            if sex == 'male':
                CalPerMin   = ( -55.0969        \
                                + 0.6309*HR     \
                                + 0.1988*weight \
                                + 0.2017*age)   \
                            / 4.184             \
                            * coef
            else:
                CalPerMin   = ( -20.4022        \
                                + 0.4472*HR     \
                                + 0.1263*weight \
                                + 0.0740*age)   \
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


    ########################################################################
    ###         Power & TSS Estimation                                   ###
    ########################################################################

    from endurance_summary import BackwardMovingAverage

    # see
    #   https://docs.scipy.org/doc/scipy/reference/signal.html
    from scipy import signal
    poles       = 3
    cutoff      = 0.10    # Hz
    Wn          = cutoff / (SampleRate/2)

    '''
    # construct and apply a differentiating, lowpass filter
    NumB, DenB  = signal.butter(poles, Wn, btype='lowpass',
                                output='ba', analog=True)
    NumF        = signal.convolve( NumB, [1,0])     # add differentiator
    bDLP, aDLP  = signal.bilinear( NumF,DenB, fs=SampleRate )
    hr_dot      = signal.lfilter(bDLP, aDLP, hr_sig)
    '''

    # apply a phaseless lowpass filter, then differentiate.
    # for some reason, running the Butterworth analog filter
    # through bilinear() gives a better result. Otherwise,
    # set analog=False to get coefficients directly.
    PadLen      = int(SampleRate/cutoff)    # one period of cutoff
    NumB, DenB  = signal.butter(poles, Wn, btype='lowpass',
                                output='ba', analog=True)
    bLPF, aLPF  = signal.bilinear( NumB,DenB, fs=SampleRate )
    hr_lpf      = signal.filtfilt(bLPF, aLPF, hr_sig, padlen=PadLen)
    hr_dot      = np.gradient(hr_lpf, 1/SampleRate)

    FTP         = ThresholdPower
    FTHR        = ThresholdHR
    tau         = HRTimeConstant
    PwHRTable   = np.array( [
                    [    0    ,  0.50*FTHR ],   # Active resting HR
                    [ 0.55*FTP,  0.70*FTHR ],   # Recovery
                    [ 0.70*FTP,  0.82*FTHR ],   # Aerobic threshold
                    [ 1.00*FTP,       FTHR ],   # Functional threshold
                    [ 1.20*FTP,  1.03*FTHR ],   # Aerobic capacity
                    [ 1.50*FTP,  1.06*FTHR ]])  # Max HR

    # loop through the time series building running power and TSS.
    # Notice this is necessary because HRd[i] depends on TSS[i-1].
    sPower  = np.zeros(nPts)
    TSS     = np.zeros(nPts)
    HRd     = np.zeros(nPts)        # fatigue drift
    HRp     = np.zeros(nPts)        # power target
    p30     = np.zeros(nPts)        # 30-sec boxcar average
    w       = int(30*SampleRate)    # window for boxcar
    NPower  = np.zeros(nPts)        # normalized power

    for i in range(1,nPts):
        HRd[i]      = HRDriftRate*TSS[i-1]
        HRp[i]      = hr_sig[i] + tau*hr_dot[i] - HRd[i]
        sPower[i]   = np.interp( HRp[i], PwHRTable[:,1], PwHRTable[:,0] )
        if i < w:
            p30[i]  = np.average(sPower[:i+1])         # include i
        else:
            p30[i]  = np.average(sPower[i-w:i+1])      # include i
        NPower[i]   = np.average( p30[:i]**4 )**(0.25)
        TSS[i]      = t_sig[i]/36*(NPower[i]/FTP)**2

    print >> OutStream, 'estimated NP   = %6i W' % NPower[-1]
    print >> OutStream, 'estimated work = %6i kJ' % \
                ( np.cumsum(sPower)[-1] / 1e3 / SampleRate )
    print >> OutStream, 'estimated TSS  = %6i TSS' % TSS[-1]
    if 'power' in signals.keys():
        mPower  = signals['power']
        print >> OutStream, 'measured work  = %6i kJ' % \
                ( np.cumsum( mPower )[-1] / 1e3 / SampleRate )
        mP30    = BackwardMovingAverage( mPower )
        mNPower = np.average( mP30**4 )**(0.25)
        mTSS    = t_sig[-1]/36*(mNPower/FTP)**2
        print >> OutStream, 'measured NP    = %6i W' % mNPower
        print >> OutStream, 'measured TSS   = %6i TSS' % mTSS

    ###########################################################
    ###             plotting                                ###
    ###########################################################

    # power zones from "Cyclist's Training Bible", 5th ed., by Joe Friel, p51
    pZones  = { 1   : [    0    ,   0.55*FTP ],
                2   : [ 0.55*FTP,   0.75*FTP ],
                3   : [ 0.75*FTP,   0.90*FTP ],
                4   : [ 0.90*FTP,   1.05*FTP ],
                5   : [ 1.05*FTP,   1.20*FTP ],
                6   : [ 1.20*FTP,   1.50*FTP ],
                7   : [ 1.50*FTP,   2.50*FTP ]}

    # heart-rate zones from "Cyclist's Training Bible" 5th ed. by Joe Friel, p50
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

    # power simulation plot
    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    from matplotlib.dates import date2num, DateFormatter
    import datetime as dt
    base = dt.datetime(2014, 1, 1, 0, 0, 0)
    x = [base + dt.timedelta(seconds=t) for t in t_sig.astype('float')]
    x = date2num(x) # Convert to matplotlib format
    fig1, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
    ax0.plot_date( x, hr_sig,  'r-', linewidth=2 );
    ax0.plot_date( x, tau*hr_dot, 'b-', linewidth=2 );
    ax0.plot_date( x, HRd, 'g-', linewidth=2 );
    ax0.plot_date( x, HRp, 'k-', linewidth=2 );
    ax0.set_yticks( h_zone_bounds, minor=False)
    ax0.grid(True)
    ax0.legend( ['HR', 'tau*HRdot', 'HRd', 'HRp' ], loc='upper left');
    ax0.set_title('heart rate, BPM')
    if 'power' in signals.keys():
        mPower  = signals['power']
        ax1.plot_date( x, mPower, 'k-', linewidth=1);
        ax1.plot_date( x, sPower, 'b-', linewidth=2 );
        ax1.legend( ['measured power', 'simulated power' ], loc='upper left');
    else:
        ax1.plot_date( x, sPower, 'b-', linewidth=2 );
        ax1.legend( ['simulated power' ], loc='upper left');
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.set_yticks( p_zone_bounds, minor=False)
    ax1.grid(True)
    ax1.set_title('power, watts')
    fig1.autofmt_xdate()
    fig1.suptitle('Pw:HR Transfer Function', fontsize=20)
    fig1.tight_layout()
    fig1.canvas.set_window_title(FitFilePath)
    plt.show()


    # plot heart rate and calories
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
    fig1.canvas.set_window_title(FitFilePath)
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
    fig2.canvas.set_window_title(FitFilePath)
    plt.show()

    def ClosePlots():
        plt.close('all')

    return ClosePlots

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

# SAMPLE OUTPUT:
#    CWD: D:\Users\Owner\Documents\OneDrive\bike\activities\will
#    PATH: D:\Users\Owner\Documents\OneDrive\bike\activities\will
#    FILE: 2018-12-02-13-13-19.fit
#
#    -------------------- Heart Rate --------------------
#
#    reading config file D:\...\fitfiles\cyclingconfig_will.txt
#    WeightEntry   :  190.0
#    WeightToKg    :  0.45359237
#    weight        :  86.1825503
#    age           :  52.0
#    sex           :  male
#    EndurancePower:  175.0
#    ThresholdPower:  250.0
#    EnduranceHR   :  140.0
#    ThresholdHR   :  170.0
#    total calories = 645
#    Heart-Rate Zone Histogram:
#        Zone  1:  1:16:43 (92%)
#        Zone  2:  0:03:46 ( 4%)
#        Zone  3:  0:01:57 ( 2%)
#        Zone  4:  0:00:11 ( 0%)
#        Zone 5a:  0:00:00 ( 0%)
#        Zone 5b:  0:00:00 ( 0%)
#        Zone 5c:  0:00:00 ( 0%)
#          total:  1:22:37

#    -------------------- Endurance Laps --------------------
#
#    reading config file D:\...\cyclingconfig_will.txt
#    WeightEntry   :  190.0
#    WeightToKg    :  0.45359237
#    weight        :  86.1825503
#    age           :  52.0
#    EndurancePower:  175.0
#    ThresholdPower:  250.0
#    EnduranceHR   :  140.0
#    ThresholdHR   :  170.0
#    required signals not in file
#    Signals required:
#       power
#       heart_rate
#    Signals contained:
#       distance
#       temperature
#       altitude
#       heart_rate
#       time
#       metadata
