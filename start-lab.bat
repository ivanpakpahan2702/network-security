@echo off
cd /d "%~dp0"
if not "%~1"=="" goto arguments
echo Pilih database Cyber Security Lab:
echo [1] SQLite - tanpa service database
echo [2] MySQL / MariaDB - koneksi dari database.local.toml
choice /c 12 /n /m "Pilihan [1/2]: "
if "%errorlevel%"=="2" goto mysql
if not "%errorlevel%"=="1" goto done
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-lab.ps1" --db sqlite
goto done
:mysql
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-lab.ps1" --db mysql
goto done
:arguments
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-lab.ps1" %*
:done
pause
