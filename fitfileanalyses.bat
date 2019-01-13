ECHO OFF

echo Currently running in %CD%

::set base depending on which machine we are on
echo.input file is %~1
echo.drive letter is %~d1
set base=S:\will\documents\OneDrive\2018\fitfiles
if "%~d1" == "D:" (
    set base=D:\Users\Owner\Documents\OneDrive\2018\fitfiles
)
echo.Setting base to %base%

REM set base=%CD%
REM set base=S:\will\documents\OneDrive\2018\fitfiles
REM set base=D:\Users\Owner\Documents\OneDrive\2018\fitfiles

REM s:
REM cd S:\will\documents\2018\fitfiles\

ECHO file received:
ECHO %1
ECHO calling python on %1
REM c:\python27\python %base%\fitfileanalyses.py %1
c:\python27\python %base%\fitfileanalyses.py %1
pause
