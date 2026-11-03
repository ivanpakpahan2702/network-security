$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$labPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $labPython)) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Gagal membuat virtual environment. Pastikan Python 3.11+ tersedia.' }
}
& $labPython -c "from importlib.util import find_spec; from importlib.metadata import version; import sys; sys.exit(0 if find_spec('flask') and version('flask') == '3.1.3' else 1)"
if ($LASTEXITCODE -ne 0) {
    & $labPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Gagal memasang dependensi Flask.' }
}
$labBackend = & $labPython -c "import argparse; from labcore.dbconfig import add_database_arguments,load_settings; p=argparse.ArgumentParser(add_help=False); add_database_arguments(p); a,_=p.parse_known_args(); print(load_settings(a.db,a.db_config).backend)" @args
if ($LASTEXITCODE -ne 0) { throw 'Konfigurasi database tidak valid. Periksa database.local.toml atau --db-config.' }
if ($labBackend -eq 'mysql') {
    & $labPython -c "from importlib.util import find_spec; import sys; sys.exit(0 if find_spec('pymysql') and find_spec('cryptography') else 1)"
    if ($LASTEXITCODE -ne 0) {
        & $labPython -m pip install -r requirements-mysql.txt
        if ($LASTEXITCODE -ne 0) { throw 'Gagal memasang driver MySQL.' }
    }
}
& $labPython run.py @args
exit $LASTEXITCODE
