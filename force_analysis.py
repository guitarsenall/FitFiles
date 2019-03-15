#!/usr/bin/env python

'''
force_analysis.py

create two histograms containing pedal-force bins on the X axis
and revolutions and work on the Y axes.
Assume SampleRate = 1 Hz and every data points, regarless of gaps,
is worth one second.

'''

import sys
import os
import numpy as np

############################################################
#              plot_heartrate function def                 #
############################################################

from activity_tools import FindConfigFile

def force_analysis(FitFilePath, ConfigFile=None, OutStream=sys.stdout):

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
    CrankRadius     = config.getfloat( 'power', 'CrankRadius' ) \
                    / 25.4      # mm -> inches
    print >> OutStream,  'CrankRadius: ', CrankRadius, ' inches'

    from datetime import datetime
    from fitparse import Activity
    from activity_tools import extract_activity_signals

    required_signals    = [ 'power',
                            'cadence'   ]

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

    SampleRate = 1.0                    # Hz
    time_signal = signals['time']
    power       = signals['power']
    cadence     = signals['cadence']

    # Calculate leg force and reps
    from math import pi
    torque  = power / cadence / (2*pi/60)      \
            * 8.8507                                # N*m -> in*lb
    leg_force   = torque / CrankRadius

    '''
    Reference from squat:
        At the end of the Anatomic Adaptation
        phase, I could squat 160lbx4x25. With 75% of my body weight
        (190 lbs), the total leg force was 300 lbs, or 150 lbs per leg.
        This went through a depth of 16 inches. So each leg performed
        work of 100 reps times 150 lbs times 16 inches, or
        240,000 in*lb, which is 27.117 kJ at 150 lb.
    '''
    SquatLegForce   = (160 + 0.75*190) / 2          # lb
    SquatDepth      = 16.0                          # inches
    SquatReps       = 100.0
    SquatWork       = SquatLegForce * SquatDepth * SquatReps    \
                    * 0.000112985416                # in*lb -> kJ

    MaxForce    = max( SquatLegForce, max(leg_force) )

    # compute the histogram
    force_bins  = np.concatenate( (                     \
                        np.arange(0, 100, 5),           \
                        np.array([100, MaxForce*1.1]) ) )
    nBins   = len(force_bins)-1
    force_mids  = (force_bins[0:nBins] + force_bins[1:nBins+1]) / 2.0
    force_mids[-1]  = 110.0
    force_width = (force_bins[1:nBins+1] - force_bins[0:nBins]) * 0.95
    force_width[-1] = 20.0*0.95
    #ForceCounts, ForceBins  = np.histogram( leg_force, bins=force_bins )

    # Instead of counts, we have revs and work as a function of force.
    # So we have to perform the histogram manually.
    # Loop over the force bins
    revs    = np.zeros(nBins)
    work    = np.zeros(nBins)
    for i in range(len(force_bins)-1):
        # Find the indices at which the force is in the bin
        ii = np.nonzero( np.logical_and(
                    leg_force >= force_bins[i],
                    leg_force <  force_bins[i+1] ) )[0]
        # Compute the revs and work at these indices:
        revs[i]     = sum(cadence[ii]) / 60 / SampleRate
        work[i]     = sum(power[ii]) / SampleRate   \
                    / 1000.0                        # J -> kJ


    ###########################################################
    ###             plotting                                ###
    ###########################################################

    # this needs to stay INSIDE the function or bad things happen
    import matplotlib.pyplot as plt

    # force & cadence time plot
    import matplotlib.dates as md
    from matplotlib.dates import date2num, DateFormatter
    import datetime as dt
    base = dt.datetime(2014, 1, 1, 0, 0, 0)
    x = [base + dt.timedelta(seconds=t) for t in time_signal.astype('float')]
    x = date2num(x) # Convert to matplotlib format
    fig1, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
    ax0.plot_date( x, leg_force,    'r-+', linewidth=1 );
    ax0.grid(True)
    ax0.legend( ['leg_force' ], loc='upper left');
    ax0.set_title('Leg Force, lb')
    ax0.set_yticks( force_bins, minor=False)
    ax1.plot_date( x, cadence,  'g-+', linewidth=1 );
    ax1.legend( ['cadence' ], loc='upper left');
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.grid(True)
    ax1.set_title('cadence, RPM')
    fig1.autofmt_xdate()
    fig1.suptitle('Force Analysis', fontsize=20)
    fig1.tight_layout()
    fig1.canvas.set_window_title(FitFilePath)
    plt.show()


    # work histogram plot
    fig2, ax2 = plt.subplots()
    #bar_width = 0.80    # 0.35
    opacity = 0.8
    #error_config = {'ecolor': '0.3'}
    zone_ints   = np.arange(7)+1
    LogY = False
    rects1 = ax2.bar(force_mids, work, force_width,
                    align='center',alpha=opacity, color='r', log=LogY,
                    label='force')
    ax2.set_xlabel('Pedal Force, lb')
    ax2.set_ylabel('work, kJ')
    ax2.set_title('Pedal Force Work Histogram')
    #ax2.set_xticks(zone_ints + bar_width / 2)
    #ax2.set_xticklabels(h_zone_labels)
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
        force_analysis(fitfilepath, ConfigFile=None)
    else:
        raise IOError('Need a .FIT file')

    #FitFilePath = r'D:\Users\Owner\Documents\OneDrive\bike\activities\will\\' \
    #            + r'2019-03-09-12-31-33.fit'

# SAMPLE OUTPUT:
