@echo off
setlocal EnableDelayedExpansion

:: ----------------- DEFAULT CONFIGURATION -----------------
set IMAGE_NAME=guillemp/geneanalysis:latest
set DEFAULT_DATA_FOLDER=C:\Users\Guillem\GeneAnalysis\data
set CONTAINER_DATA_FOLDER=/app/data
set PORT=8501
:: ---------------------------------------------------------

echo ===========================================
echo   GeneAnalysis Docker Launcher
echo ===========================================
echo.

:: Ask user to confirm data folder
set DATA_FOLDER=%DEFAULT_DATA_FOLDER%

:confirm_path
echo The current data folder is:
echo   %DATA_FOLDER%
echo.
set /p ANSWER="Is this correct? (Y/N): "

if /I "%ANSWER%"=="Y" goto run_container
if /I "%ANSWER%"=="N" goto change_path

echo Invalid input. Please enter Y or N.
goto confirm_path


:change_path
echo.
set /p NEWPATH="Enter the full path to the data folder: "
set DATA_FOLDER=%NEWPATH%
echo.
goto confirm_path


:run_container
echo.
echo Starting Streamlit Docker container...
echo Image:      %IMAGE_NAME%
echo Data mount: %DATA_FOLDER% -> %CONTAINER_DATA_FOLDER%
echo Port:       %PORT%
echo.

docker run ^
    -p %PORT%:%PORT% ^
    -v "%DATA_FOLDER%:%CONTAINER_DATA_FOLDER%" ^
    %IMAGE_NAME%

pause
