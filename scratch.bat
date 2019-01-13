@echo off

REM Set filename=C:\Documents and Settings\All Users\Desktop\Dostips.cmd
REM For %%A in ("%filename%") do (
REM     Set Folder=%%~dpA
REM     Set Name=%%~nxA
REM     echo.Folder is: %Folder%
REM     echo.Name is: %Name%
REM )
REM echo.Folder is: %Folder%
REM echo.Name is: %Name%

REM :: http://weblogs.asp.net/jgalloway/archive/2006/11/20/top-10-dos-batch-tips-yes-dos-batch.aspx
REM echo %%~1     =      %~1 
REM echo %%~f1     =      %~f1
REM echo %%~d1     =      %~d1
REM echo %%~p1     =      %~p1
REM echo %%~n1     =      %~n1
REM echo %%~x1     =      %~x1
REM echo %%~s1     =      %~s1
REM echo %%~a1     =      %~a1
REM echo %%~t1     =      %~t1
REM echo %%~z1     =      %~z1
REM echo %%~$PATHATH:1     =      %~$PATHATH:1
REM echo %%~dp1     =      %~dp1
REM echo %%~nx1     =      %~nx1
REM echo %%~dp$PATH:1     =      %~dp$PATH:1
REM echo %%~ftza1     =      %~ftza1

::set base depending on which machine we are on
echo.input file is %~1
echo.drive letter is %~d1
set base=S:\will\documents\OneDrive\2018\fitfiles
if "%~d1" == "D:" (
    set base=D:\Users\Owner\Documents\OneDrive\2018\fitfiles
)
echo.Setting base to %base%

pause
