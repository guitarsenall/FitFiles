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

    activity = Activity(FitFilePath)
    activity.parse()

    # Records of type 'record' (I know, confusing) are the entries in an
    # activity file that represent actual data points in your workout.
    records = activity.get_records_by_type('record')
    current_record_number = 0

    time_list = []
    heartrate_list  = []
    FirstIter   = True

    for record in records:

        # Print record number
        current_record_number += 1
        if verbose:
            print >> OutStream,  (" Record #%d " % current_record_number).center(40, '-')

        # Get the list of valid fields on this record
        valid_field_names = record.get_valid_field_names()

        for field_name in valid_field_names:
            # Get the data and units for the field
            field_data = record.get_data(field_name)
            field_units = record.get_units(field_name)

            if verbose:
                # Print what we've got!
                if field_units:
                    print >> OutStream,  " * %s: %s %s" % (field_name, field_data, field_units)
                else:
                    print >> OutStream,  " * %s: %s" % (field_name, field_data)

            if 'timestamp' in field_name:
                if FirstIter:
                    t0  = field_data    # datetime
                    t   = t0
                    FirstIter   = False
                else:
                    t   = field_data    # datetime


            if 'heart_rate' in field_name:
                dt  = t-t0
                time_list.append(dt.total_seconds())
                heartrate_list.append(field_data)

    # plot the heart rate
    import numpy as np
    from pylab import *
    time_signal         = array(time_list)
    heartrate_signal    = array(heartrate_list)
    plot(time_signal/60.0, heartrate_signal, 'r.-')
    xlabel('time (min)')
    ylabel('heart rate (BPM)')
    title('heart rate')
    grid(True)
    show()

    # file for holding the signals (dictionary via pickle)
    SignalMap   = { 'time_signal'       : time_signal,
                    'heartrate_signal'  : heartrate_signal }
#    import pickle
#    SignalsFile = open( 'signals.pkl', 'wb')
#    pickle.dump(SignalMap, SignalsFile)
#    SignalsFile.close()

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

    ## import the signals
    #import pickle
    #SignalsFile = open( 'signals.pkl', 'rb')
    #SignalMap   = pickle.load(SignalsFile)
    #SignalsFile.close()
    #
    #print 'signal map fields: ', SignalMap.keys()
    # ['heartrate_signal', 'time_signal']


    from pylab import *


# these should come from ConfigFile now:
#    weight  = 188.0*0.45359237  # lb->kg
#    age     = 50.0
#    EnduranceHR     = 140.0                         # BPM
#    EndurancePower  = 190.0                         # watts
#    ThresholdHR     = 170.0                         # BPM
#    ThresholdPower  = 271.0                         # watts

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

    hr_sig      = SignalMap['heartrate_signal']
    t_sig       = SignalMap['time_signal']
    dt_sig      = append( array([1.0]), t_sig[1:] - t_sig[0:-1] )
    nPts        = t_sig.size
    calories    = zeros(nPts)

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

    running_calories    = cumsum( calories )

    print >> OutStream,  'total calories = %i' % running_calories[nPts-1]

    # plot heart rate and calories
    plt.subplot(2, 1, 1)
    plt.plot(t_sig/60, hr_sig, 'r.-')
    plt.title('Heart Rate and Calories')
    plt.ylabel('BPM')

    plt.subplot(2, 1, 2)
    plt.plot(t_sig/60, running_calories, 'b.-')
    plt.xlabel('time (min)')
    plt.ylabel('calories')

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
    #            + r'2018-12-02-20-29-34.fit'

