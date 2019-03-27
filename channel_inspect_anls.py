#!/usr/bin/env python

'''
channel_inspect_anls.py

Present a modal dialog containing a wx.CheckListBox and a button to plot
selected channels.

'''

import os
import sys
import wx

############################################################
#           channel_inspect_anls function def              #
############################################################

from activity_tools import FindConfigFile

def channel_inspect_anls(FitFilePath, ConfigFile=None, OutStream=sys.stdout,
                         ParentWin=None):

    (FilePath, FitFileName) = os.path.split(FitFilePath)

    if ConfigFile is None:
        ConfigFile = FindConfigFile('', FilePath)
    if (ConfigFile is None) or (not os.path.exists(ConfigFile)):
        raise IOError('Configuration file not specified or found')

    # get the signals
    from datetime import datetime
    from fitparse import Activity
    from activity_tools import extract_activity_signals
    activity = Activity(FitFilePath)
    signals     = extract_activity_signals(activity, resample='existing')

    ChannelList = signals.keys()
    ChannelList.remove('time')
    ChannelList.remove('metadata')

    print >> OutStream, 'Signals contained:'
    for s in ChannelList:
        print >> OutStream, '   ' + s

    if ParentWin is None:
        app = wx.App()

    dlg = wx.MultiChoiceDialog( ParentWin,
                               "Pick channels\nto plot",
                               "channel inspector: " + FitFileName,
                               ChannelList)

    if (dlg.ShowModal() == wx.ID_OK):
        selections = dlg.GetSelections()
        ChannelNames = [ ChannelList[x] for x in selections ]
        print >> OutStream, "Plotting: %s" % (ChannelNames)

    dlg.Destroy()

    #
    # time plot
    #
    nPlots  = len(ChannelNames)

    PlotColors  = { 'power'         : 'm'       ,
                    'heart_rate'    : 'r'       ,
                    'cadence'       : 'g'       ,
                    'speed'         : 'b'       ,
                    'temperature'   : 'brown'   }


    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    from matplotlib.dates import date2num, DateFormatter
    import datetime as dt
    base = dt.datetime(2014, 1, 1, 0, 0, 0)
    x = [base + dt.timedelta(seconds=t) for t in signals['time'].astype('float')]
    x = date2num(x) # Convert to matplotlib format
    #fig1, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
    axislist    = []
    fig = plt.figure()
    for i, channel in zip( range(nPlots), ChannelNames ):
        if PlotColors.has_key(channel):
            pcolor  = PlotColors[channel]
        else:
            pcolor  = 'k-'
        if i > 0:
            ax  = plt.subplot( nPlots, 1, i+1, sharex=axislist[0] )
        else:
            ax  = plt.subplot( nPlots, 1, i+1 )
        ax.plot_date( x, signals[channel], pcolor, linewidth=1, linestyle='-' );
        ax.grid(True)
        ax.set_ylabel(channel)
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        ax.grid(True)
        axislist.append(ax)
    fig.autofmt_xdate()
    fig.suptitle(FitFileName, fontsize=20)
    fig.tight_layout()
    fig.canvas.set_window_title(FitFilePath)
    fig.subplots_adjust(hspace=0)   # Remove horizontal space between axes
    plt.show()


    def ClosePlots():
        plt.close('all')

    return ClosePlots

# end channel_inspect_anls()

#----------------------------------------------------------------------



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
        channel_inspect_anls(fitfilepath, ConfigFile=None)
    else:
        raise IOError('Need a .FIT file')


