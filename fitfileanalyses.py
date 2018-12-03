
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

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        #self.log = log

    def OnDropFiles(self, x, y, filenames):
        txt = "\n%d file(s) dropped at %d,%d:\n" % (len(filenames), x, y)
        txt += '\n'.join(filenames)
        (FilePath, FileName) = os.path.split(filenames[0])
        os.chdir(FilePath)
        win.SetStatusText(os.getcwd(), number=0)
        SetFileNameText(FileName)
        return True

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
def load(event):
    print 'load button pressed'
FileNameCtl = wx.StaticText(bkg, -1, "", style=wx.ST_NO_AUTORESIZE|wx.BORDER_SIMPLE)
#FileNameCtl.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
dt = MyFileDropTarget(bkg)
FileNameCtl.SetDropTarget(dt)
def SetFileNameText(txt):
    FileNameCtl.SetLabel(txt)
loadButton = wx.Button(bkg, label='Open')
loadButton.Bind(wx.EVT_BUTTON, load)
hBox2 = wx.BoxSizer()
hBox2.Add(FileNameCtl, proportion=1, flag=wx.EXPAND)
hBox2.Add(loadButton, proportion=0, flag=wx.LEFT, border=5)

ContentsCtl = wx.TextCtrl(bkg, style=wx.TE_MULTILINE | wx.HSCROLL)
ContentsCtl.SetValue( 'This will be the output window' )
font1 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New')
ContentsCtl.SetFont(font1)

# vertical box sizer
vbox = wx.BoxSizer(wx.VERTICAL)
vbox.Add(hBox1, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
vbox.Add(hBox2, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
vbox.Add(ContentsCtl, proportion=1,
         flag=wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
bkg.SetSizer(vbox)

win.Show()
app.MainLoop()

