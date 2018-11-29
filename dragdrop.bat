ECHO OFF
s:
cd S:\will\documents\2018\fitfiles\
ECHO file received:
ECHO %1
ECHO calling python on %1
c:\python27\python dragdrop.py %1
pause
