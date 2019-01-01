
'''
pwhr_transfer_function.py

Compute HR from a given transfer function and overplot it with measured HR.
'''

import os
import sys

############################################################
#           pwhr_transfer_function function def            #
############################################################

def pwhr_transfer_function(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

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
    HRTimeConstant  = config.getfloat( 'power', 'HRTimeConstant' )
    HRDriftRate     = config.getfloat( 'power', 'HRDriftRate'    )
    print >> OutStream, 'WeightEntry    : ', WeightEntry
    print >> OutStream, 'WeightToKg     : ', WeightToKg
    print >> OutStream, 'weight         : ', weight
    print >> OutStream, 'age            : ', age
    print >> OutStream, 'EndurancePower : ', EndurancePower
    print >> OutStream, 'ThresholdPower : ', ThresholdPower
    print >> OutStream, 'EnduranceHR    : ', EnduranceHR
    print >> OutStream, 'ThresholdHR    : ', ThresholdHR
    print >> OutStream, 'HRTimeConstant : ', HRTimeConstant
    print >> OutStream, 'HRDriftRate    : ', HRDriftRate

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

    # resample to constant-increment (1 Hz) with zeros at missing samples
    import numpy as np
    time_idx                = signals['time'].astype('int')
    power_vi                = signals['power']
    heart_rate_vi           = signals['heart_rate']
    nScans                  = time_idx[-1]+1
    time_ci                 = np.arange(nScans)
    power                   = np.zeros(nScans)
    power[time_idx]         = power_vi
    heart_rate_ci           = np.zeros(nScans)
    heart_rate_ci[time_idx] = heart_rate_vi

    # compute the 30-second, moving-average power signal.
    from endurance_summary import BackwardMovingAverage
    p30 = BackwardMovingAverage( power )

    # Calculate running normalized power and TSS.
    norm_power  = np.zeros(nScans)
    TSS         = np.zeros(nScans)
    for i in range(1,nScans):
        norm_power[i] = np.average( p30[:i]**4 )**(0.25)
        TSS[i] = time_ci[i]/36*(norm_power[i]/FTP)**2

    #
    # simulate the heart rate
    #
    from scipy.integrate import odeint
    SampleRate  = 1.0
    tau         = HRTimeConstant    # 63.0 seconds
    #HRDriftRate = 0.17  # BPM/TSS
    PwHRTable   = np.array( [
                    [    0    ,  0.50*FTHR ],   # Active resting HR
                    [ 0.55*FTP,  0.70*FTHR ],   # Recovery
                    [ 0.70*FTP,  0.82*FTHR ],   # Aerobic threshold
                    [ 1.00*FTP,       FTHR ],   # Functional threshold
                    [ 1.20*FTP,  1.03*FTHR ],   # Aerobic capacity
                    [ 1.50*FTP,  1.06*FTHR ]])  # Max HR
    def heartrate_dot(HR,t):
        i = min( int(t * SampleRate), nScans-1 )
        HRp = np.interp( power[i], PwHRTable[:,0], PwHRTable[:,1] )
        HRt = HRp + HRDriftRate*TSS[i]
        return ( HRt - HR ) / tau
    heart_rate_sim = odeint( heartrate_dot, heart_rate_ci[0], time_ci )


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
    ax0.plot_date( x, heart_rate_ci,  'r-', linewidth=1 );
    ax0.plot_date( x, heart_rate_sim, 'm-', linewidth=3 );
    ax0.set_yticks( h_zone_bounds, minor=False)
    ax0.grid(True)
    ax0.legend( ['measured', 'simulated' ], loc='upper left');
    ax0.set_title('heart rate, BPM')
    ax1.plot_date( x, power,            'k-', linewidth=1 );
    ax1.plot_date( x, p30,              'b-', linewidth=3);
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.set_yticks( p_zone_bounds, minor=False)
    ax1.grid(True)
    ax1.set_title('power, watts')
    fig1.autofmt_xdate()
    ax1.legend( ['power', 'p30' ], loc='upper left');
    fig1.suptitle('Pw:HR Transfer Function', fontsize=20)
    fig1.tight_layout()
    fig1.canvas.set_window_title(FitFilePath)
    plt.show()

    def ClosePlots():
        plt.close('all')
    return ClosePlots

# end pwhr_transfer_function()

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
        pwhr_transfer_function(fitfilepath, ConfigFile=None)
    else:
        raise IOError('Need a .FIT file')

## VO2max intervals:
#FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
#            + r'2018-12-10-17-28-24.fit'
## threshold effort:
#FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
#            + r'2018-09-03-17-36-11.fit'
## threshold intervals:
#FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
#            + r'2018-07-17-15-12-10.fit'
## endurance:
#FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
#            + r'2018-12-31-12-23-12.fit'
# no heartrate signal
#FitFilePath = r'S:\will\documents\OneDrive\bike\activities\will\\' \
#            + r'2018-12-22-16-28-06.fit'
