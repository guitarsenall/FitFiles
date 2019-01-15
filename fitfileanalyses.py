
'''
fitfileanalyses.py
'''

import os

# needed to close figure windows, but not working.
# import matplotlib.pyplot as plt


################################################################################
################################################################################
###                               GUI                                        ###
################################################################################
################################################################################

# wxPython GUI library
#   c:\Python27>python -m pip install -U wxPython
import wx

#---------------------------------------------------------------------------

# This is how you pre-establish a file filter so that the dialog
# only shows the extension(s) you want it to.
wildcard = "FIT files (*.fit)|*.fit|"  \
           "All files (*.*)|*.*"

#---------------------------------------------------------------------------

###########################################
#           classes & functions           #
###########################################

from activity_tools import FindConfigFile

def AutoFillConfigFile(FilePath):
    CodePath    = stBar.GetStatusText()
    (FitFilePath, FITFileName) = os.path.split( FileNameCtl.GetLabel() )
    print 'AutoFillConfigFile called. CodePath: ' + CodePath
    ConfigFile  = FindConfigFile(CodePath, FilePath)
    if ConfigFile is None:
        ConfigFileCtl.SetLabel('')
    else:
        ConfigFileCtl.SetLabel(ConfigFile)

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        #self.log = log

    def OnDropFiles(self, x, y, filenames):
        (FilePath, FileName) = os.path.split(filenames[0])
        OutStr = [ "CWD: %s" % os.getcwd() ]
        OutStr.append( 'PATH: %s' % FilePath )
        OutStr.append( 'FILE: %s' % FileName )
        OutputTextCtl.SetValue( '\n'.join(OutStr) )
        print >> OutputTextCtl, '\n'
        #os.chdir(FilePath)
        #win.SetStatusText(os.getcwd(), number=0)
        SetFileNameText(filenames[0])
        AutoFillConfigFile(FilePath)
        return True

def LoadFitFile(event):
    print 'LoadFitFile button pressed'
    dlg = wx.FileDialog(
        None, message="Choose a .FIT file",
        defaultDir=os.getcwd(),
        defaultFile="",
        wildcard = "Garmin files (*.fit)|*.fit|"  \
                   "All files (*.*)|*.*",
        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST |
              wx.FD_PREVIEW
        )
    if dlg.ShowModal() == wx.ID_OK:
        # This returns a Python list of files that were selected.
        paths = dlg.GetPaths()
        #contents.SetValue('You selected %d files:' % len(paths))
        (FilePath, FileName) = os.path.split(paths[0])
        OutStr = [ "CWD: %s" % os.getcwd() ]
        OutStr.append( 'PATH: %s' % FilePath )
        OutStr.append( 'FILE: %s' % FileName )
        OutputTextCtl.SetValue( '\n'.join(OutStr) )
        print >> OutputTextCtl, '\n'
        SetFileNameText(paths[0])
        win.SetStatusText(os.getcwd(), number=0)
        AutoFillConfigFile(FilePath)
    dlg.Destroy()


def LoadConfigFile(event):
    print 'LoadConfigFile button pressed'
    dlg = wx.FileDialog(
        None, message="Choose a configuration file",
        defaultDir=os.getcwd(),
        defaultFile="",
        wildcard = "Text files (*.txt)|*.txt|"  \
                   "All files (*.*)|*.*",
        style=wx.FD_OPEN |
              wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
              wx.FD_PREVIEW
        )
    if dlg.ShowModal() == wx.ID_OK:
        # This returns a Python list of files that were selected.
        paths = dlg.GetPaths()
        (FilePath, FileName) = os.path.split(paths[0])
        OutStr = [ "CWD: %s" % os.getcwd() ]
        OutStr.append( 'PATH: %s' % FilePath )
        OutStr.append( 'FILE: %s' % FileName )
        print >> OutputTextCtl, '\n'.join(OutStr)
        print >> OutputTextCtl, '\n'
        for s in OutStr:
            print s  #OutStr
        ConfigFileCtl.SetLabel(paths[0])
        win.SetStatusText(os.getcwd(), number=0)
    dlg.Destroy()


analyses_labels = [ 'Endurance Laps',
                    'Zone Detection',
                    'Interval Laps',
                    'Heart Rate',
                    'Pw-HR Simulation',
                    'Compare Two Powers']

# make sure matplotlib is imported INSIDE the analysis functions
# or bad things happen (e.g., code freezes until plot is closed, etc...).
from endurance_summary import endurance_summary
from zone_detect import zone_detect
from plot_heartrate import plot_heartrate
from pwhr_transfer_function import pwhr_transfer_function
from interval_laps import interval_laps

class MyLaunchButton(wx.Button):
    ''' class to hold plot-closer functions to be called when application is closed'''

    plot_closer_fcns   = []

    def LaunchAnalysis(self, event):

        AnalysesChoice  = AnalysesCtl.GetSelection()
        AnalysesChoice  = AnalysesCtl.GetString(AnalysesChoice)
        print >> OutputTextCtl, '-'*20 + ' ' + AnalysesChoice + ' ' + '-'*20
        FITFileName = FileNameCtl.GetLabel()
        ConfigFile  = ConfigFileCtl.GetLabel()
        if not os.path.exists(FITFileName):
            dlg = wx.MessageDialog(win,
                        'A valid .FIT file must be entered.',
                        'WARNING',
                        wx.OK | wx.ICON_INFORMATION
                        )
            dlg.ShowModal()
            dlg.Destroy()
            return

        if AnalysesChoice == 'Endurance Laps':
            print 'Running endurance summary on ' + FITFileName
            print >> OutputTextCtl, ''
            try:
                PlotCloserFcn = endurance_summary( FITFileName, ConfigFile,
                                                    OutStream=OutputTextCtl )
                self.plot_closer_fcns.append(PlotCloserFcn)
            except IOError, ErrorObj:
                dlg = wx.MessageDialog(win, ErrorObj.message, AnalysesChoice,
                            wx.OK | wx.ICON_INFORMATION )
                dlg.ShowModal()
                dlg.Destroy()

        elif AnalysesChoice == 'Zone Detection':
            print 'Running zone detection on ' + FITFileName
            print >> OutputTextCtl, ''
            try:
                PlotCloserFcn = zone_detect( FITFileName, ConfigFile,
                                             OutStream=OutputTextCtl )
                self.plot_closer_fcns.append(PlotCloserFcn)
            except IOError, ErrorObj:
                dlg = wx.MessageDialog(win, ErrorObj.message, AnalysesChoice,
                            wx.OK | wx.ICON_INFORMATION )
                dlg.ShowModal()
                dlg.Destroy()

        elif AnalysesChoice == 'Interval Laps':
            print 'Running interval-lap analysis on ' + FITFileName
            print >> OutputTextCtl, ''
            try:
                # no plots created
                interval_laps( FITFileName, ConfigFile,
                               OutStream=OutputTextCtl )
            except IOError, ErrorObj:
                dlg = wx.MessageDialog(win, ErrorObj.message, AnalysesChoice,
                            wx.OK | wx.ICON_INFORMATION )
                dlg.ShowModal()
                dlg.Destroy()

        elif AnalysesChoice == 'Heart Rate':
            print 'Running heartrate analysis on ' + FITFileName
            print >> OutputTextCtl, ''
            try:
                PlotCloserFcn = plot_heartrate( FITFileName, ConfigFile,
                                                OutStream=OutputTextCtl )
                self.plot_closer_fcns.append(PlotCloserFcn)
            except IOError, ErrorObj:
                dlg = wx.MessageDialog(win, ErrorObj.message, AnalysesChoice,
                            wx.OK | wx.ICON_INFORMATION )
                dlg.ShowModal()
                dlg.Destroy()

        elif AnalysesChoice == 'Pw-HR Simulation':
            print 'Running Pw-HR Simulation on ' + FITFileName
            print >> OutputTextCtl, ''
            try:
                PlotCloserFcn = pwhr_transfer_function( FITFileName, ConfigFile,
                                                OutStream=OutputTextCtl )
                self.plot_closer_fcns.append(PlotCloserFcn)
            except IOError, ErrorObj:
                dlg = wx.MessageDialog(win, ErrorObj.message, AnalysesChoice,
                            wx.OK | wx.ICON_INFORMATION )
                dlg.ShowModal()
                dlg.Destroy()

        else:
            print 'Analysis not yet supported: ' + AnalysesChoice
            dlg = wx.MessageDialog(win,
                        'Analysis not supported: ' + AnalysesChoice,
                        'WARNING',
                        wx.OK | wx.ICON_INFORMATION
                        )
            dlg.ShowModal()
            dlg.Destroy()
            return

    # end MyLaunchButton.LaunchAnalysis()

    def ClosePlots(self):
        if len(self.plot_closer_fcns) > 0:
            for PlotCloserFcn in self.plot_closer_fcns:
                PlotCloserFcn()

class StreamTextControl(wx.TextCtrl):
    ''' make a text control streamable for print statement '''
    def write(self, data):
        self.AppendText(data)


###########################################
#    main app, window, and background     #
###########################################

app = wx.App()
win = wx.Frame(None, title="Fit File Analysis Suite", size=(800, 600))
stBar   = win.CreateStatusBar(number=1, style=wx.STB_DEFAULT_STYLE, id=-1,
                                name='stBar')
win.SetStatusText(os.getcwd(), number=0)
bkg = wx.Panel(win)

###########################################
#             controls                    #
###########################################

notesText   = wx.StaticText(bkg, label="Select the .FIT file.")
hBox1 = wx.BoxSizer()
hBox1.Add(notesText, proportion=1, flag=wx.EXPAND)

# notes input filename
FileNameCtl = wx.StaticText(bkg, -1, "",
                    style = wx.ST_NO_AUTORESIZE | wx.BORDER_SIMPLE )
#FileNameCtl.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
dt = MyFileDropTarget(bkg)
FileNameCtl.SetDropTarget(dt)
def SetFileNameText(txt):
    FileNameCtl.SetLabel(txt)
loadButton = wx.Button(bkg, label='Open')
loadButton.Bind(wx.EVT_BUTTON, LoadFitFile)
hBox2 = wx.BoxSizer()
hBox2.Add(FileNameCtl, proportion=1, flag=wx.EXPAND)
hBox2.Add(loadButton, proportion=0, flag=wx.LEFT, border=5)

# Analyses Choice
AnalysesText = wx.StaticText(bkg, label = "Choose analysis to run:" )
AnalysesCtl = wx.Choice(bkg, choices = analyses_labels)
AnalysesCtl.SetSelection(0)     # 'Endurance Laps'
def AnalysesEventChoice(event):
    OutStr  = 'AnalysesEventChoice: %s\n' % event.GetString()
    # OutputTextCtl.SetValue( OutStr )
    print OutStr
bkg.Bind(wx.EVT_CHOICE, AnalysesEventChoice, AnalysesCtl)
hBox3 = wx.BoxSizer()
hBox3.Add(AnalysesText, proportion=0, flag=wx.RIGHT, border=5)
hBox3.Add(AnalysesCtl, proportion=0, flag=wx.EXPAND)

# configuration file
ConfigFileTxt    = wx.StaticText(bkg, label = 'Configuration File:')
ConfigFileCtl    = wx.StaticText(bkg, -1, "",
                            style = wx.ST_NO_AUTORESIZE | wx.BORDER_SIMPLE )
ConfigFileButton = wx.Button(bkg, label='...')
ConfigFileButton.Bind(wx.EVT_BUTTON, LoadConfigFile)
hBox4 = wx.BoxSizer()
hBox4.Add(ConfigFileTxt, proportion=0, flag=wx.RIGHT, border=5)
hBox4.Add(ConfigFileCtl, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=5)
hBox4.Add(ConfigFileButton, proportion=0, flag=wx.LEFT, border=5)

# LAUNCH and CLOSE buttons
LaunchButton = MyLaunchButton(bkg, label='LAUNCH ANALYSIS')
LaunchButton.Bind( wx.EVT_BUTTON, LaunchButton.LaunchAnalysis )
def OnClose(event):
    print 'OnClose called'
    LaunchButton.ClosePlots()
    win.Close(True)
CloseButton = wx.Button(bkg, label='CLOSE')
CloseButton.Bind(wx.EVT_BUTTON, OnClose)
hBox5 = wx.BoxSizer()
hBox5.Add(LaunchButton, proportion=1, flag=wx.LEFT, border=5)
hBox5.Add(CloseButton, proportion=1, flag=wx.LEFT, border=5)

# output text
OutputTextCtl = StreamTextControl(bkg, style=wx.TE_MULTILINE | wx.HSCROLL)
OutputTextCtl.SetValue( 'Analysis output area\n' )
font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New')
OutputTextCtl.SetFont(font1)

# vertical box sizer
vbox = wx.BoxSizer(wx.VERTICAL)
vbox.Add(hBox1, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
vbox.Add(hBox2, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
vbox.Add(hBox3, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
vbox.Add(hBox4, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
vbox.Add(hBox5, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
vbox.Add(OutputTextCtl, proportion=1,
         flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
bkg.SetSizer(vbox)

# attempt to load file specified in command line.
# Recall, sys.argv[0] is the name of the python routine with the
# full path, so it is the CodePath.
# sys.argv[1:] is the first argument (hopefully the FIT file).
import sys
if len(sys.argv) >= 1:
    (CodePath, PyFileName)      = os.path.split(sys.argv[0])
    os.chdir(CodePath)
    win.SetStatusText(os.getcwd(), number=0)
    AutoFillConfigFile(CodePath)
if len(sys.argv) >= 2:
    print 'command line args: ', sys.argv[1:]
    fitfilepath = sys.argv[1]
    if os.path.exists(fitfilepath):
        (FilePath, FileName) = os.path.split(fitfilepath)
        OutStr = [ "CWD: %s" % os.getcwd() ]
        OutStr.append( 'PATH: %s' % FilePath )
        OutStr.append( 'FILE: %s' % FileName )
        OutputTextCtl.SetValue( '\n'.join(OutStr) )
        print >> OutputTextCtl, '\n'
        SetFileNameText(fitfilepath)
        AutoFillConfigFile(FilePath)

win.Show()
app.MainLoop()

