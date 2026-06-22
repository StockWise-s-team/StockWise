@echo off
REM Windows batch script wrapper to run the Python E2E Trade Matching Test

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [-] Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)

python "%~dp0run_demo_test.py"
