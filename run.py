"""Dashboard dan aplikasi lab di loopback atau LAN; service SSRF tetap internal."""
import argparse
import threading
import time
from pathlib import Path

from werkzeug.serving import make_server

from labcore.catalog import BY_ID, LABS
from labcore.dashboard import create_dashboard
from labcore.factory import create_app
from labcore.services import internal_app
from labcore.network import access_urls, bind_address, lan_enabled
from labcore.dbconfig import add_database_arguments, load_settings
from labcore.database import database_errors


def main():
    parser = argparse.ArgumentParser(description="Cyber Security Lab lokal — Flask + SQLite/MySQL")
    parser.add_argument("--lab", nargs="+", choices=list(BY_ID), help="Jalankan hanya lab pilihan beserta dashboard")
    parser.add_argument("--list", action="store_true", help="Daftar lab dan port, lalu keluar")
    parser.add_argument("--host", type=bind_address, default="0.0.0.0", help="IP bind, default 0.0.0.0 (akses LAN)")
    parser.add_argument("--port-offset", type=int, default=0, help="Geser semua port, misalnya 1000 untuk dashboard 6100")
    parser.add_argument("--data-dir", type=Path, help="Direktori data alternatif; default database per folder lab")
    add_database_arguments(parser)
    args = parser.parse_args()
    if not 0 <= args.port_offset <= 60000:
        parser.error("Offset port harus antara 0 dan 60000.")
    if args.list:
        for lab in LABS:
            print(f"{lab['id']:<28} port {lab['port'] + args.port_offset}  {lab['level']:<9} {lab['title']}")
        return
    selected = list(dict.fromkeys(args.lab or BY_ID))
    allow_lan = lan_enabled(args.host)
    try:
        settings = load_settings(args.db, args.db_config)
        print(f"Menyiapkan {len(selected)} lab dengan backend {settings.backend}...", flush=True)
        applications = [(args.host, 5100, create_dashboard(selected, allow_lan=allow_lan,
                        data_dir=args.data_dir / "dashboard" if args.data_dir else None, database_settings=settings))]
        for index, lab_id in enumerate(selected, 1):
            app = create_app(lab_id, allow_lan=allow_lan,
                             data_dir=args.data_dir / lab_id if args.data_dir else None, database_settings=settings)
            applications.append((args.host, BY_ID[lab_id]["port"], app))
            if index % 10 == 0 or index == len(selected):
                print(f"  Database dan fixture siap: {index}/{len(selected)} lab", flush=True)
    except (ValueError, RuntimeError, *database_errors()) as error:
        parser.error(f"Inisialisasi database gagal: {error}. Periksa database.local.toml dan panduan MYSQL.md.")
    if "08_ssrf" in selected:
        applications.append(("127.0.0.1", 5199, internal_app()))
    for _, _, app in applications:
        app.config.update(PORT_OFFSET=args.port_offset, SSRF_PORT=5199 + args.port_offset)
    servers = []
    started = set()
    try:
        # Bind semua port sebelum menerima request. Konflik port tidak menyisakan lab parsial.
        for host, port, app in applications:
            servers.append(make_server(host, port + args.port_offset, app, threaded=True))
        for server in servers:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            started.add(server)
        print("\nSecurity Lab aktif. Buka salah satu alamat berikut:", flush=True)
        for url in access_urls(args.host, 5100 + args.port_offset):
            print(f"  {url}", flush=True)
        backend_label = 'MySQL schema per lab' if settings.backend == 'mysql' else 'SQLite per folder'
        print(f"{len(selected)} lab terpisah | {backend_label} | Ctrl+C untuk berhenti", flush=True)
        print(f"Dashboard/lab bind {args.host}; service SSRF 127.0.0.1:{5199 + args.port_offset}; debugger nonaktif.\n", flush=True)
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nMenghentikan seluruh lab...", flush=True)
    finally:
        for server in servers:
            if server in started:
                server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
