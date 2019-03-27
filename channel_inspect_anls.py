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

#    ChannelList = [ 'apple', 'pear', 'banana', 'coconut', 'orange', 'grape', 'pineapple',
#            'blueberry', 'raspberry', 'blackberry', 'snozzleberry',
#            'etc', 'etc..', 'etc...' ]
    ChannelList = signals.keys()
    ChannelList.remove('time')
    ChannelList.remove('metadata')

    if ParentWin is None:
        app = wx.App()

    dlg = wx.MultiChoiceDialog( ParentWin,
                               "Pick channels\nto plot",
                               "channel inspector: " + FitFileName,
                               ChannelList)

    if (dlg.ShowModal() == wx.ID_OK):
        selections = dlg.GetSelections()
        ChannelNames = [ ChannelList[x] for x in selections ]
        print >> OutStream, "Selections: %s -> %s\n" % (selections, ChannelNames)

    dlg.Destroy()

    #
    # time plot
    #

    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    from matplotlib.dates import date2num, DateFormatter
    import datetime as dt
    base = dt.datetime(2014, 1, 1, 0, 0, 0)
    x = [base + dt.timedelta(seconds=t) for t in signals['time'].astype('float')]
    x = date2num(x) # Convert to matplotlib format
    fig1, (ax0, ax1) = plt.subplots(nrows=2, sharex=True)
    ax0.plot_date( x, heart_rate_ci, 'r-', linewidth=1 );
    ax0.plot_date( x, lap_avg_hr_c,  'r-', linewidth=3 );
    ax0.set_yticks( h_zone_bounds, minor=False)
    ax0.grid(True)
    ax0.set_title('heart rate, BPM')
    ax1.plot_date( x, power,            'k-', linewidth=1 );
    ax1.plot_date( x, p30,              'm-', linewidth=1);
    ax1.plot_date( x, lap_avg_power_c,  'b-', linewidth=3);
    ax1.plot_date( x, lap_norm_power_c, 'g-', linewidth=3);
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    ax1.set_yticks( p_zone_bounds, minor=False)
    ax1.grid(True)
    ax1.set_title('power, watts')
    fig1.autofmt_xdate()
    ax1.legend(['power', 'p30', 'lap_avg_power', 'lap_norm_power'],
                loc='upper left');
    fig1.suptitle('Endurance Power Results', fontsize=20)
    fig1.tight_layout()
    fig1.canvas.set_window_title(FitFilePath)
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


