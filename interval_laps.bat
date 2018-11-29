ECHO OFF

set base=S:\will\documents\OneDrive\2018\fitfiles

REM s:
REM cd S:\will\documents\2018\fitfiles\

ECHO file received:
ECHO %1
ECHO calling python on %1
REM c:\python27\python %base%\dragdrop.py %1
c:\python27\python %base%\detect_laps.py %1
pause
