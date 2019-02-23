ECHO OFF

echo Currently running in %CD%

::set base depending on which machine we are on
echo running on %ComputerName%
IF "%ComputerName%" == "LAPTOP" (
    echo laptop detected
    set base=D:\Users\Owner\Documents\OneDrive\2018\fitfiles
) ELSE (
    echo i7Win10 detected
    set base=S:\will\documents\OneDrive\2018\fitfiles
)

REM ::set base depending on which machine we are on
REM echo.input file is %~1
REM echo.drive letter is %~d1
REM set base=S:\will\documents\OneDrive\2018\fitfiles
REM if "%~d1" == "D:" (
REM     set base=D:\Users\Owner\Documents\OneDrive\2018\fitfiles
REM )

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
