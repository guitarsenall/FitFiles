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
#              force_analysis function def                 #
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
    nPts        = len(power)

    # Calculate leg force and reps
    from math import pi
    torque  = np.zeros(nPts)
    ii  = cadence.nonzero()[0]
    torque[ii]  = power[ii] / cadence[ii] / (2*pi/60)      \
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

    # Histogram bin edges. The first bin is underflow (includes data
    # down to the minimum regardless of the first edge), and the last
    # is overflow (includes data up to maximum regardless of the last edge).
    force_bins      = np.arange(0, 82, 2)       # (0, 85, 5)
    cadence_bins    = np.arange(26, 126, 2)     # (25, 125, 5)

    # compute the force-work histogram
    # Instead of counts, we have revs and work as a function of force.
    # So we have to perform the histogram manually.
    nFBins  = len(force_bins)-1
    force_width = (force_bins[1:nFBins+1] - force_bins[0:nFBins]) * 0.95

    revs    = np.zeros(nFBins)
    force_work    = np.zeros(nFBins)
    for i in range(nFBins):
        FBinLo  = force_bins[i] if i>1 else leg_force.min()
        FBinHi  = force_bins[i+1] if i<nFBins else leg_force.max()*1.1
        ii = np.nonzero( np.logical_and(
                    leg_force >= FBinLo,
                    leg_force <  FBinHi ) )[0]
        # Compute the revs and work at these indices:
        revs[i]         = sum(cadence[ii]) / 60 / SampleRate
        force_work[i]   = sum(power[ii]) / SampleRate   \
                        / 1000.0                        # J -> kJ

    # compute the cadence-work histogram
    nCBins          = len(cadence_bins)-1
    cadence_width   = (cadence_bins[1:nCBins+1] - cadence_bins[0:nCBins]) * 0.95
    cadence_work    = np.zeros(nCBins)
    for i in range(nCBins):
        CBinLo  = cadence_bins[i] if i>1 else leg_force.min()
        CBinHi  = cadence_bins[i+1] if i<nCBins else cadence.max()*1.1
        ii = np.nonzero( np.logical_and(
                    cadence >= CBinLo,
                    cadence <  CBinHi ) )[0]
        cadence_work[i] = sum(power[ii]) / SampleRate   \
                        / 1000.0                        # J -> kJ


    #
    #   Exposure Histogram
    #
    #    I want the plot to display force on the X axis, but this is
    #    the column (2nd) index, and the Y axis is the row (1st) index.
    #    So I need to transpose work2d at some point; it would probably
    #    be best to do so right up front since np.meshgrid() formats
    #    the coordinates this way.
    work2d          = np.zeros([nCBins  ,nFBins  ])     # note shape!
    power_grid      = np.zeros([nCBins+1,nFBins+1])
    force_grid, cadence_grid = np.meshgrid(force_bins, cadence_bins)
    for i in range(nFBins):
        FBinLo = force_bins[i] if i>1 else leg_force.min()
        FBinHi = force_bins[i+1] if i < nFBins else leg_force.max()*1.1
        ii = np.nonzero( np.logical_and(
                    leg_force >= FBinLo,
                    leg_force <  FBinHi ) )[0]
        for j in range(nCBins):
            CBinLo = cadence_bins[j] if j > 1 else cadence.min()
            CBinHi = cadence_bins[j+1] if j < nCBins else cadence.max()*1.1
            jj = np.nonzero( np.logical_and(
                    cadence[ii] >= CBinLo,
                    cadence[ii] <  CBinHi  ))[0]
            work2d[j,i]     = sum(power[ii[jj]])    \
                            / SampleRate / 1000.0   # J -> kJ
            TorqueNM        = force_bins[i] * CrankRadius / 8.8507
            power_grid[j,i] = TorqueNM * cadence_bins[j] * (2*pi/60)
    # last grid column
    i += 1
    TorqueNM    = force_bins[i] * CrankRadius / 8.8507
    for j in range(nCBins+1):
        power_grid[j,i] = TorqueNM * cadence_bins[j] * (2*pi/60)
    # last grid row. Leave j = nCBins
    for i in range(nFBins+1):
        TorqueNM        = force_bins[i] * CrankRadius / 8.8507
        power_grid[j,i] = TorqueNM * cadence_bins[j] * (2*pi/60)
    power_lines = np.arange(50, power_grid.max(), 50)


    ###########################################################
    ###             plotting                                ###
    ###########################################################

    # this needs to stay INSIDE the function or bad things happen
    import matplotlib.pyplot as plt

    # force & cadence time plot with grids at valid bin edges so that
    # underflow and overflow bins are shown accurately.
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
    ax0.set_yticks( force_bins[1:-1], minor=False)
    ax1.plot_date( x, cadence,  'g-+', linewidth=1 );
    ax1.legend( ['cadence' ], loc='upper left');
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.grid(True)
    ax1.set_title('cadence, RPM')
    ax1.set_yticks( cadence_bins[1:-1], minor=False)
    fig1.autofmt_xdate()
    fig1.suptitle('Force Analysis', fontsize=20)
    fig1.tight_layout()
    fig1.canvas.set_window_title(FitFilePath)
    plt.show()


    # force_work histogram plot
    fig2, ax2 = plt.subplots()
    opacity = 0.8
    LogY = False
    rects1 = ax2.bar(force_bins[:-1], force_work, force_width,
                    align='edge',alpha=opacity, color='r', log=LogY,
                    label='force')
    ax2.set_xlabel('Pedal Force, lb')
    ax2.set_ylabel('work, kJ')
    ax2.set_title('Pedal Force Work Histogram')
    ax2.legend()
    fig2.tight_layout()
    fig2.canvas.set_window_title(FitFilePath)
    plt.show()

    # cadence_work histogram plot
    fig4, ax4 = plt.subplots()
    opacity = 0.8
    rects4 = ax4.barh(cadence_bins[:-1], cadence_work, cadence_width,
                    align='edge',alpha=opacity, color='g', log=False,
                    label='cadence')
    ax4.set_ylabel('cadence, RPM')
    ax4.set_xlabel('work, kJ')
    ax4.set_title('Cadence-Work Histogram')
    ax4.legend()
    fig4.tight_layout()
    fig4.canvas.set_window_title(FitFilePath)
    plt.show()

    # create a custom segmented colormap. I want zero to be a cool color
    # on which I can see the power contours; I want a quick transition that
    # exposes low work values with a subtle cool color; then I want the
    # map to gradually transition through "hotter" colors to red.
    from matplotlib import colors as mcolors
    colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
    segment_data = [
                    # X        color
                    ( 0  ,   'darkviolet' ),
                    ( 0.1,   'darkgreen'  ),
                    ( 0.3,   'blue'       ),
                    ( 0.5,   'cyan'       ),
                    ( 0.7,   'yellow'     ),
                    ( 1.0,   'red'        ) ]
    cdict = {'red'  : [],
             'green': [],
             'blue' : []}
    for x, cName in segment_data:
        rgba = mcolors.to_rgba( colors[cName] )
        cdict[  'red'].append( (x, rgba[0], rgba[0]) )
        cdict['green'].append( (x, rgba[1], rgba[1]) )
        cdict[ 'blue'].append( (x, rgba[2], rgba[2]) )
    newcmp = mcolors.LinearSegmentedColormap('WillsCmap',
                                    segmentdata=cdict, N=256)

    # exposure histogram plot
    # clone from
    #   https://matplotlib.org/gallery/images_contours_and_fields/pcolor_demo.html
    fig3, ax3 = plt.subplots()
    c   = ax3.pcolor( force_grid, cadence_grid, work2d,
                      cmap=newcmp, vmin=work2d.min(), vmax=work2d.max() )
    ax3.axis([   force_bins.min(), force_bins.max(),
                cadence_bins.min(), cadence_bins.max()])
    cbar    = fig3.colorbar(c, ax=ax3)
    cbar.ax.set_ylabel('work, kJ')
    CS = ax3.contour( force_grid, cadence_grid, power_grid,
                      power_lines, colors='k' )
    ax3.clabel(CS, fontsize=9, inline=1)
    ax3.set_xlabel('Pedal Force, lb')
    ax3.set_ylabel('cadence, RPM')
    ax3.set_title('Pedal Exposure Histogram')
    fig3.tight_layout()
    fig3.canvas.set_window_title(FitFilePath)
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
