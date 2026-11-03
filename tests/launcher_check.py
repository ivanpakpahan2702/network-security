"""Startup seluruh aplikasi pada port dan database terpisah dari sesi pengguna."""
import argparse
import contextlib
import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from labcore.catalog import LABS

OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def wait_for(process, url):
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError('Launcher berhenti lebih awal:\n' + process.communicate()[0])
        try:
            with OPENER.open(url, timeout=1) as response:
                return json.load(response)
        except (OSError, urllib.error.URLError):
            time.sleep(0.1)
    raise RuntimeError('Startup melewati batas waktu.')


def launch(arguments):
    return subprocess.Popen([sys.executable, '-X', 'utf8', *arguments], cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')


def stop(process):
    if process.poll() is None:
        process.terminate()
    process.communicate(timeout=10)


def exclusive_socket():
    sock = socket.socket()
    if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    return sock


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port-offset', type=int, default=2000)
    parser.add_argument('--db-config',type=Path,help='MySQL QA pada schema acak, tanpa memakai data pengguna')
    args = parser.parse_args()
    if not 0 <= args.port_offset <= 60000:
        parser.error('Offset port harus antara 0 dan 60000.')
    offset = args.port_offset
    ports = [*range(5100 + offset, 5101 + len(LABS) + offset), 5199 + offset]
    # Jangan menganggap server pengguna yang sudah aktif sebagai proses uji.
    for port in ports:
        with exclusive_socket() as probe:
            probe.bind(('127.0.0.1', port))

    def url(port, path='/health'):
        return f'http://127.0.0.1:{port + offset}{path}'

    with tempfile.TemporaryDirectory(prefix='launcher-check-') as directory, contextlib.ExitStack() as stack:
        backend = 'mysql' if args.db_config else 'sqlite'
        common = ['--host','127.0.0.1','--port-offset',str(offset),'--data-dir',directory,'--db',backend]
        if args.db_config:
            from tests.mysql_support import temporary_mysql
            settings = stack.enter_context(temporary_mysql(args.db_config))
            config = Path(directory)/'database.toml'
            config.write_text('[mysql]\n' + '\n'.join(f'{key} = {json.dumps(getattr(settings,key))}' for key in ('host','port','user','password','prefix'))+'\n',encoding='utf-8')
            common += ['--db-config',str(config)]
        process = launch(['run.py',*common])
        try:
            status = wait_for(process,url(5100))
            assert status['labs'] == len(LABS), status
            assert status['database'] == backend, status
            for lab in LABS:
                with OPENER.open(url(lab['port']),timeout=2) as response:
                    assert json.load(response)['lab'] == lab['id']
            with OPENER.open(url(5199,'/public/status'),timeout=2) as response:
                assert json.load(response)['status'] == 'healthy'
            with OPENER.open(url(5100,'/learn'),timeout=2) as response:
                assert response.status == 200
            print(f'PASS: launcher menjalankan dashboard, {len(LABS)} aplikasi, materi, dan SSRF',flush=True)
        finally:
            stop(process)

        with exclusive_socket() as occupied:
            occupied.bind(('127.0.0.1',5101 + offset))
            occupied.listen(1)
            process = launch(['run.py','--lab','01_sql_injection',*common])
            try:
                output, _ = process.communicate(timeout=20)
                assert process.returncode != 0, output
                with exclusive_socket() as probe:
                    probe.bind(('127.0.0.1',5100 + offset))
                print('PASS: konflik port membatalkan startup tanpa meninggalkan dashboard',flush=True)
            finally:
                stop(process)

        for lab_id, port in (('08_ssrf',5108),('40_capstone',5140)):
            process = launch([f'labs/{lab_id}/app.py',*common])
            try:
                assert wait_for(process,url(port))['lab'] == lab_id
                if lab_id == '08_ssrf':
                    with OPENER.open(url(5199,'/internal/metadata'),timeout=2) as response:
                        assert 'DUMMY-KEY' in json.load(response)['api_key']
                print(f'PASS: aplikasi mandiri {lab_id}',flush=True)
            finally:
                stop(process)

    for port in ports:
        with socket.socket() as probe:
            probe.settimeout(0.2)
            assert probe.connect_ex(('127.0.0.1',port)) != 0, f'Server uji tertinggal pada {port}'
    print('PASS: seluruh server dan data uji dibersihkan',flush=True)


if __name__ == '__main__':
    main()
