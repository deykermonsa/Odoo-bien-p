@echo off
setlocal enabledelayedexpansion

REM Ruta base de los módulos Odoo
set BASE=%~dp0

echo ==========================
echo 🛠️  Compilando todos los módulos Odoo en: %BASE%
echo ==========================

REM Recorre todas las subcarpetas dentro de 'addons'
for /D %%D in (%BASE%*) do (
    echo.
    echo 📁 Procesando módulo: %%~nxD

    REM Compilar los archivos .py a .pyc al lado del .py
    python -m compileall -b "%%D"

    REM Borrar archivos .py excepto __init__.py y __manifest__.py
    for /R "%%D" %%F in (*.py) do (
        set filename=%%~nxF
        if /I NOT "!filename!"=="__init__.py" if /I NOT "!filename!"=="__manifest__.py" del "%%F"
    )

    echo ✅ Módulo %%~nxD procesado.
)

echo.
echo ==========================
echo ✅ Todos los módulos fueron compilados exitosamente.
pause
