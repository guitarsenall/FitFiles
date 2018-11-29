
# dragdrop.py

import sys
print 'command line args: ', sys.argv[1:]

# Sample usage of python-fitparse to parse an activity and
# print its data records.

verbose = False

#
#   Parse the configuration file
#
from ConfigParser import ConfigParser
ConfigFile  = 'cyclingconfig.txt'
config      = ConfigParser()
config.read(ConfigFile)
#print 'reading config file ' + ConfigFile
print '-'*20 + ' ' + ConfigFile + ' ' + '-'*20
WeightEntry     = config.getfloat( 'user', 'weight' )
WeightToKg      = config.getfloat( 'user', 'WeightToKg' )
weight          = WeightEntry * WeightToKg
age             = config.getfloat( 'user', 'age' )
EndurancePower  = config.getfloat( 'power', 'EndurancePower' )
ThresholdPower  = config.getfloat( 'power', 'ThresholdPower' )
EnduranceHR     = config.getfloat( 'power', 'EnduranceHR'    )
ThresholdHR     = config.getfloat( 'power', 'ThresholdHR'    )
print 'WeightEntry   : ', WeightEntry
print 'WeightToKg    : ', WeightToKg
print 'weight        : ', weight
print 'age           : ', age
print 'EndurancePower: ', EndurancePower
print 'ThresholdPower: ', ThresholdPower
print 'EnduranceHR   : ', EnduranceHR
print 'ThresholdHR   : ', ThresholdHR

from datetime import datetime
from fitparse import Activity
from activity_tools import extract_activity_signals

# typ 'S:\\will\\documents\\bike\\fitfiles\\2017-01-08-15-41-48_zwift.fit'
fitfilepath = sys.argv[1]

activity    = Activity(fitfilepath)
signals     = extract_activity_signals(activity)

########################################################################
###         Compute Calories                                         ###
########################################################################

from numpy import array, arange, append, zeros, cumsum, average
#from pylab import *

#   Formula widely available. One site:
#       https://www.easycalculation.com/formulas/heart-rate-calorie-burn.html

#weight  = 188.0*0.45359237  # lb->kg
#age     = 50.0

#   calibration at endurance
#EnduranceHR     = 140.0                         # BPM
#EndurancePower  = 180.0                         # watts
EnduranceBurn   = EndurancePower*3600/1e3/60    # Cal/min
EnduranceCoef   = EnduranceBurn                     \
                / (   -55.0969 + 0.6309*EnduranceHR \
                    + 0.1988*weight + 0.2017*age)   \
                * 4.184

#   calibration at threshold
#ThresholdHR     = 170.0                         # BPM
#ThresholdPower  = 271.0                         # watts
ThresholdBurn   = ThresholdPower*3600/1e3/60    # Cal/min
ThresholdCoef   = ThresholdBurn                     \
                / (   -55.0969 + 0.6309*ThresholdHR \
                    + 0.1988*weight + 0.2017*age)   \
                * 4.184

hr_sig      = signals['heart_rate']
t_sig       = arange(len(hr_sig))   # seconds
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

print '-'*20 + ' CALORIE/ENERGY RESULTS ' + '-'*20
print 'total time           = %5i minutes' % ( t_sig[-1]/60.0 )
print 'average heart rate   = %5i BPM' % average(hr_sig)
if 'power' in signals.keys():
    print 'total work           = %5i kJ' % \
            ( cumsum( signals['power'] )[-1] / 1e3 )
print 'total calories       = %5i Cal' % running_calories[nPts-1]

########################################################################
###         Interval Summary                                         ###
########################################################################

from activity_tools import threshold_state_detect
from numpy import average, zeros

FTP = 0.95*ThresholdPower

# VO2max intervals
print '-'*20 + ' VO2MAX INTERVALS ' + '-'*20
MinLength = 30  # seconds
vo2max_intervals    = threshold_state_detect( signals['power'],
                                OnLevel =1.05*FTP,
                                OffLevel=0.75*FTP,
                                DebounceCounts=5  )
interval_averages = zeros(len(vo2max_intervals))
interval_samples  = zeros(len(vo2max_intervals))
for i, interval in enumerate(vo2max_intervals):
    on  = interval['on']
    off = interval['off']
    if off-on >= MinLength:
        seg = signals['power'][on:off]
        interval_averages[i] = average(seg)
        interval_samples[i] = off-on
        mm = interval_samples[i] // 60
        ss = interval_samples[i]  % 60
        print '    interval %2i: %4i watts for %02i:%02i' \
            % (i, interval_averages[i], mm, ss)
vo2max_time = sum(interval_samples) / 60.0
if vo2max_time:
    vo2max_average  = sum( interval_samples * interval_averages ) \
                    / sum(interval_samples)
    print 'VO2max interval average = %i watts for %5.1f minutes' \
        % (vo2max_average, vo2max_time)

# Sweet-spot intervals
print '-'*20 + ' SWEET-SPOT INTERVALS ' + '-'*20
MinLength = 60*2  # seconds
ss_intervals    = threshold_state_detect( signals['power'],
                                OnLevel =0.88*FTP,
                                OffLevel=0.70*FTP,
                                DebounceCounts=5  )
interval_averages = zeros(len(ss_intervals))
interval_samples  = zeros(len(ss_intervals))
for i, interval in enumerate(ss_intervals):
    on  = interval['on']
    off = interval['off']
    if off-on >= MinLength:
        seg = signals['power'][on:off]
        interval_averages[i] = average(seg)
        interval_samples[i] = off-on
        mm = interval_samples[i] // 60
        ss = interval_samples[i]  % 60
        print '    interval %2i: %4i watts for %02i:%02i' \
            % (i, interval_averages[i], mm, ss)
ss_time = sum(interval_samples) / 60.0
if ss_time:
    ss_average  = sum( interval_samples * interval_averages ) \
                / sum(interval_samples)
    print 'Sweet-spot interval average = %i watts for %5.1f minutes' \
        % (ss_average, ss_time)

