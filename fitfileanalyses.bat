ECHO OFF

REM set base=S:\will\documents\OneDrive\2018\fitfiles
set base=D:\Users\Owner\Documents\OneDrive\2018\fitfiles

REM s:
REM cd S:\will\documents\2018\fitfiles\

ECHO file received:
ECHO %1
ECHO calling python on %1
REM c:\python27\python %base%\fitfileanalyses.py %1
c:\python27\python %base%\fitfileanalyses.py %1
pause
