@echo off
title DSP-Agent-Aligner (DAA)

echo ========================================
echo   DSP-Agent-Aligner (DAA) Launcher
echo ========================================
echo.

echo [1/3] Activating Conda env: daa
call conda activate daa
if %errorlevel% neq 0 (
    echo [ERROR] Cannot activate conda env daa
    echo Please create it first: conda create -n daa python=3.11
    goto :end
)

echo [2/3] Changing to project directory
cd /d "%~dp0"
echo Current dir: %cd%
echo.

echo [3/3] Starting main program...
echo ========================================
echo.

python dsp_aligner_app.py

:end
echo.
echo ========================================
echo Program exited
echo ========================================
pause