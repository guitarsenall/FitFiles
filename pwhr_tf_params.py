
'''
pwhr_tf_params.py

Estimate parameters for the power-HR transfer function:
    FTHR            : Functional threshold heart rate, BPM
    HRTimeConstant  : First-order time constant for heart rate, sec
    HRDriftRate     : Fatigue-induced cardiac drift rate, BPM/TSS

'''

import os
import sys

############################################################
#               pwhr_tf_params function def                #
############################################################

#def pwhr_tf_params(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

ConfigFile=None
OutStream=sys.stdout

FilePath    = r'S:\will\documents\OneDrive\bike\activities\will\\'
fit_files   = [ '2018-12-10-17-28-24.fit' ,   # VO2max intervals
                '2018-09-03-17-36-11.fit' ,   # threshold effort
                '2018-07-17-15-12-10.fit' ,   # threshold intervals
                '2018-12-31-12-23-12.fit' ]   # endurance


#(FilePath, FitFileName) = os.path.split(FitFilePath)

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
FTP = ThresholdPower

'''
# power zones from "Cyclist's Training Bible", 5th ed., by Joe Friel, p51
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
'''


from fitparse import Activity
from activity_tools import extract_activity_signals
from endurance_summary import BackwardMovingAverage
from scipy.integrate import odeint
from scipy.optimize import minimize
import numpy as np

required_signals    = [ 'power',
                        'heart_rate' ]

SampleRate  = 1.0


def heartrate_dot(HR, t, FTHR, HRTimeConstant, HRDriftRate):
    ''' Heart rate model. The derivative, the return value, is
        proportional to the difference between the HR target and
        the current heartrate.
    '''
    #print '    heartrate_dot called'
    PwHRTable   = np.array( [
                    [    0    ,  0.50*FTHR ],   # Active resting HR
                    [ 0.55*FTP,  0.70*FTHR ],   # Recovery
                    [ 0.70*FTP,  0.82*FTHR ],   # Aerobic threshold
                    [ 1.00*FTP,       FTHR ],   # Functional threshold
                    [ 1.20*FTP,  1.03*FTHR ],   # Aerobic capacity
                    [ 1.50*FTP,  1.06*FTHR ]])  # Max HR
    i = min( int(t * SampleRate), nScans-1 )
    HRp = np.interp( power[i], PwHRTable[:,0], PwHRTable[:,1] )
    HRt = HRp + HRDriftRate*TSS[i]
    return ( HRt - HR ) / HRTimeConstant


def HRSimulationError(params):
    ''' A function passed to scipy.optimize.minimize() that
        computes and returns the error in simulating heart rate
        based on the three parameters passed to it.
            FTHR            = params[0]
            HRTimeConstant  = params[1]
            HRDriftRate     = params[2]
    '''
    args            = tuple(params)
    heart_rate_sim = odeint( heartrate_dot, heart_rate_ci[0], time_ci,
                             args=args )
    err     = heart_rate_sim - heart_rate_ci
    RMSError    = np.sqrt(np.average( err**2 ))
    print 'HRSimulationError called with %10i, %10.1f, %10.3f -> %10.1f' \
            % (params[0], params[1], params[2], RMSError)
    return RMSError


print >> OutStream, 'Optimization Results:'
names1  = [ 'FIT File', 'FTHR (BPM)',  'tau (sec)', 'HRDriftRate' ]
fmt     = '%20s:' + '%10s'*3
print >> OutStream, fmt % tuple(names1)

for FitFile in fit_files:

    # get the signals
    FitFilePath = FilePath + FitFile
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

#    # get the FTP
#    FTP = 250.0 #assume if not present
#    records = activity.get_records_by_type('zones_target')
#    for record in records:
#        valid_field_names = record.get_valid_field_names()
#        for field_name in valid_field_names:
#            if 'functional_threshold_power' in field_name:
#                field_data = record.get_data(field_name)
#                field_units = record.get_units(field_name)
#                #print >> OutStream, 'FTP setting = %i %s' % (field_data, field_units)
#                FTP = field_data

    # resample to constant-increment (1 Hz) with zeros at missing samples
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
    p30 = BackwardMovingAverage( power )

    # Calculate running normalized power and TSS.
    norm_power  = np.zeros(nScans)
    TSS         = np.zeros(nScans)
    for i in range(1,nScans):
        norm_power[i] = np.average( p30[:i]**4 )**(0.25)
        TSS[i] = time_ci[i]/36*(norm_power[i]/FTP)**2

    # optimize by minimizing the simulation error
    x0  = [ ThresholdHR, HRTimeConstant, HRDriftRate ]
    bnds = ( (130.0, 200.0), (30.0, 120.0), (0.0, 0.50) )
    res = minimize(HRSimulationError, x0, method='SLSQP', bounds=bnds)
    #print res.message
    fmt     = '%20s:' + '%10i' + '%10.1f' + '%10.3f'
    print >> OutStream, fmt % (FitFile, res.x[0], res.x[1], res.x[2] )


# end pwhr_tf_params()

#############################################################
##           main program execution                         #
#############################################################
#'''
#This technique allows the module to be imported without
#executing it until one of its functions is called.
#'''
#
#if __name__ == '__main__':
#    import sys
#    if len(sys.argv) >= 2:
#        print 'command line args: ', sys.argv[1:]
#        fitfilepath = sys.argv[1]
#        pwhr_transfer_function(fitfilepath, ConfigFile=None)
#    else:
#        raise IOError('Need a .FIT file')

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
