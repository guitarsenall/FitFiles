# FitFiles
A collection of analysis routines for .FIT files from Garmin devices.

#   Overview of capabilities
    ##   Fast access to custom analyses of selected FIT file
    ##   Endurance laps
    ##   Power-zone detection
    ##   Intervals
    ##   Heartrate zone analysis
    ##   Heartrate simulation from power
#   How to launch using the batch file (fitfileanalyses.bat)
    ##   May need to edit to set the base code directory.
#   User config files.
#   How to install
    ##   Python 2.7
    ##   NumPy
    ##   SciPy
    ##   MatPlotLib
    At a command prompt, enter,
    >   'cd C:\Python27\'
    >   `python -m pip install matplotlib'

    ##   FitParse
         FitParse is a python library for parsing .FIT activity files
         developed by DT Cooper and available at,
             https://github.com/dtcooper/python-fitparse
         However, this uses a modified version of the old release that
         I made (to handle left-right balance). Simply copy the following files
         from the folder fitparse_mod:
                fitparse_mod/__init__.py
                fitparse_mod/activity.py
                fitparse_mod/base.py
                fitparse_mod/exceptions.py
                fitparse_mod/profile.def
                fitparse_mod/records.py
         into,
                C:\Python27\Lib\site-packages\fitparse\

    ##   wxPython GUI library
    At a command prompt, enter,
    >   `python -m pip install -U wxPython'
