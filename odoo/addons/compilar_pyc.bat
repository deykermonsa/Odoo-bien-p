@echo off
REM Script para compilar archivos .py a .pyc en el mismo directorio en todo addon

REM Reemplaza esto con el nombre de tu módulo si es distinto a 'calendar'
set MODULO=calendar

REM Cambiar al directorio del módulo
cd /d "%~dp0%MODULO%"

REM Compilar todos los .py en el módulo
python -m compileall -b .

REM Eliminar todos los .py excepto __manifest__.py y __init__.py
for /R %%F in (*.py) do (
    if /I not "%%~nxF"=="__init__.py" if /I not "%%~nxF"=="__manifest__.py" del "%%F"
)

echo ✅ Módulo '%MODULO%' compilado correctamente con archivos .pyc.
pause
