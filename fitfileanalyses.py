
'''
fitfileanalyses.py
'''

import os


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

def AutoFillConfigFile(FilePath):
    # attempt to find appropriate config file
    if 'will' in FilePath.split('\\'):
        WillConfigFilename = 'cyclingconfig_will.txt'
        if os.path.exists(WillConfigFilename):
            ConfigFileCtl.SetLabel(WillConfigFilename)
    elif 'kim' in FilePath.split('\\'):
        KimConfigFilename = 'cyclingconfig_kim.txt'
        if os.path.exists(KimConfigFilename):
            ConfigFileCtl.SetLabel(KimConfigFilename)

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        #self.log = log

    def OnDropFiles(self, x, y, filenames):
        txt = "\n%d file(s) dropped at %d,%d:\n" % (len(filenames), x, y)
        txt += '\n'.join(filenames)
        (FilePath, FileName) = os.path.split(filenames[0])
        OutStr = [ "CWD: %s" % os.getcwd() ]
        OutStr.append( 'PATH: %s' % FilePath )
        OutStr.append( 'FILE: %s' % FileName )
        OutputTextCtl.SetValue( '\n'.join(OutStr) )
        os.chdir(FilePath)
        win.SetStatusText(os.getcwd(), number=0)
        SetFileNameText(FileName)
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
        style=wx.FD_OPEN |
              wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
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
        for s in OutStr:
            print s  #OutStr
        SetFileNameText(FileName)
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
        for s in OutStr:
            print s  #OutStr
        ConfigFileCtl.SetLabel(FileName)
        win.SetStatusText(os.getcwd(), number=0)
    dlg.Destroy()


def LaunchAnalysis(event):
    from endurance_summary import endurance_summary
    from zone_detect import zone_detect
    AnalysesChoice  = AnalysesCtl.GetSelection()
    AnalysesChoice  = AnalysesCtl.GetString(AnalysesChoice)
    print 'Launch Analysis called with analysis: ' + AnalysesChoice
    if AnalysesChoice == 'Endurance Laps':
        FITFileName = FileNameCtl.GetLabel()
        if not os.path.exists(FITFileName):
            dlg = wx.MessageDialog(win,
                        'A valid .FIT file must be entered.',
                        'WARNING',
                        wx.OK | wx.ICON_INFORMATION
                        )
            dlg.ShowModal()
            dlg.Destroy()
            return
        print 'Running endurance summary on ' + FITFileName
        ConfigFile  = ConfigFileCtl.GetLabel()
        OutStr  = 'Launching Analysis: %s\n' % AnalysesChoice
        #OutputTextCtl.SetValue( OutStr )
        print >> OutputTextCtl, ''
        endurance_summary( FITFileName, ConfigFile, OutStream=OutputTextCtl )
    elif AnalysesChoice == 'Zone Detection':
        FITFileName = FileNameCtl.GetLabel()
        if not os.path.exists(FITFileName):
            dlg = wx.MessageDialog(win,
                        'A valid .FIT file must be entered.',
                        'WARNING',
                        wx.OK | wx.ICON_INFORMATION
                        )
            dlg.ShowModal()
            dlg.Destroy()
            return
        print 'Running zone detection on ' + FITFileName
        ConfigFile  = ConfigFileCtl.GetLabel()
        OutStr  = 'Launching Analysis: %s\n' % AnalysesChoice
        #OutputTextCtl.SetValue( OutStr )
        print >> OutputTextCtl, ''
        zone_detect( FITFileName, ConfigFile, OutStream=OutputTextCtl )
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


class StreamTextControl(wx.TextCtrl):
    ''' make a text control streamable for print statement '''
    def write(self, data):
        self.AppendText(data)


###########################################
#    main app, window, and background     #
###########################################

app = wx.App()
win = wx.Frame(None, title="Fit File Analysis Suite", size=(600, 400))
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
analyses_labels = [ 'Endurance Laps',
                    'Zone Detection',
                    'Interval Laps',
                    'Heart Rate',
                    'Compare Two Powers']
AnalysesText = wx.StaticText(bkg, label = "Choose analysis to run:" )
AnalysesCtl = wx.Choice(bkg, choices = analyses_labels)
AnalysesCtl.SetSelection(0)
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
LaunchButton = wx.Button(bkg, label='LAUNCH ANALYSIS')
LaunchButton.Bind(wx.EVT_BUTTON, LaunchAnalysis)
def OnClose(event):
    print 'OnClose called'
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

win.Show()
app.MainLoop()

