@echo off
setlocal

set "VENV_DIR=venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"

:loop
if not exist "%PYTHON_EXE%" (
  echo Creating venv...
  python -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo Failed to create venv.
    goto :eof
  )
)

echo Installing requirements...
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install requirements.
  goto :eof
)

cls

echo Running main.py...
"%PYTHON_EXE%" main.py

set /p _=Press Enter to run again...

goto loop
