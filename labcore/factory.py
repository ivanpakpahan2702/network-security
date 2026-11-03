import importlib.util
import secrets
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, abort, g, jsonify, redirect, render_template, request, session, url_for

from labcore.catalog import BY_ID, ROOT
from labcore.database import connect, initialize, database_errors
from labcore.exercises import initialize_exercises, records
from labcore.dbconfig import target_for, describe, add_database_arguments, load_settings
from labcore.network import allowed_address, bind_address, lan_enabled, request_lab, service_url


def load_handler(lab_id, mode):
    path = ROOT / "labs" / lab_id / f"{mode}.py"
    spec = importlib.util.spec_from_file_location(f"labs_{lab_id}_{mode}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def secure_local_app(app):
    @app.before_request
    def local_only():
        host = urlsplit("http://" + request.host).hostname
        allow_lan = app.config.get("ALLOW_LAN", False)
        if host != "localhost" and not allowed_address(host, allow_lan):
            abort(403, "Host ditolak. Gunakan IP server lab yang diizinkan.")
        if not allowed_address(request.remote_addr, allow_lan):
            abort(403, "Koneksi ditolak. Lab hanya menerima loopback atau jaringan privat pada mode LAN.")
        if request.method == "POST":
            # Satu endpoint sengaja menerima POST lintas origin untuk demo CSRF.
            csrf_demo = request.path.startswith("/bank/") and request.path.endswith("/transfer")
            if not csrf_demo:
                origin = request.headers.get("Origin")
                if origin and origin != request.host_url.rstrip("/"):
                    app.logger.warning("Origin ditolak: %r; origin aplikasi: %r", origin, request.host_url.rstrip("/"))
                    abort(403, "Origin asing ditolak oleh batas aplikasi lab.")
                expected = session.get("lab_token", "")
                supplied = request.form.get("_lab_token", "")
                if not expected or not secrets.compare_digest(expected.encode(), supplied.encode()):
                    abort(403, "Token kontrol lab tidak valid. Muat ulang halaman.")

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        # no-referrer dapat membuat Origin POST navigasi menjadi 'null' di browser.
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        dashboard_origin = service_url(5100)
        bank_origin = service_url(5104)
        response.headers.setdefault("Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'none'; "
            f"form-action 'self' {dashboard_origin} {bank_origin}; frame-ancestors 'self'")
        return response

    @app.context_processor
    def context():
        session.setdefault("lab_token", secrets.token_urlsafe(32))
        return {"lab_token": session["lab_token"], "catalog": list(BY_ID.values()),
                "db_label": app.config.get('DB_LABEL', 'SQLite'), "database_display": app.config.get('DATABASE_DISPLAY', ''),
                "service_url": service_url, "lab_host": urlsplit("http://" + request.host).hostname,
                "network_label": "LAN / LOCAL LAB" if app.config.get("ALLOW_LAN", False) else "LOCAL ENVIRONMENT"}


def create_app(lab_id, data_dir=None, testing=False, allow_lan=False, database_settings=None):
    lab = BY_ID[lab_id]
    app = Flask(lab_id, template_folder=str(ROOT / "templates"), static_folder=str(ROOT / "static"))
    instance = Path(data_dir) if data_dir else ROOT / "labs" / lab_id / "instance"
    instance.mkdir(parents=True, exist_ok=True)
    fixture = instance / "fixtures"
    (fixture / "public").mkdir(parents=True, exist_ok=True)
    (fixture / "private").mkdir(parents=True, exist_ok=True)
    (fixture / "public" / "readme.txt").write_text("File publik lab. Selamat belajar keamanan!", encoding="utf-8")
    (fixture / "private" / "secret.txt").write_text("SECRET_PATH_DEMO_2026 - rahasia dummy", encoding="utf-8")
    database_path = target_for(instance / "lab.sqlite3", lab_id, database_settings)
    initialize(database_path)
    if lab["number"] >= 15:
        with connect(database_path) as db:
            initialize_exercises(db)
    if lab_id == "27_pcap_analysis":
        from labcore.protocols import capture_bytes
        captures = fixture / "captures"
        captures.mkdir(exist_ok=True)
        for name in ("normal", "scan", "incomplete"):
            (captures / f"{name}.pcap").write_bytes(capture_bytes(name))
    app.config.update(SECRET_KEY=secrets.token_hex(32), TESTING=testing, MAX_CONTENT_LENGTH=96 * 1024,
                      SESSION_COOKIE_NAME=f"lab_{lab_id}", SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE="Lax", DATABASE=database_path, FIXTURE=fixture, LAB=lab,
                      ALLOW_LAN=allow_lan, **describe(database_path))
    handlers = {mode: load_handler(lab_id, mode) for mode in ("vulnerable", "secure")}
    app.extensions["handlers"] = handlers
    secure_local_app(app)

    @app.before_request
    def open_database():
        g.db = connect(database_path)

    @app.teardown_request
    def close_database(error):
        db = g.pop("db", None)
        if db is not None:
            if error:
                db.rollback()
            db.close()

    def page(result=None, mode=None, values=None):
        visible_lab = request_lab(lab)
        sources = {}
        for key in handlers:
            path = ROOT / "labs" / lab_id / f"{key}.py"
            sources[key] = {"path": f"labs/{lab_id}/{key}.py", "lines": path.read_text(encoding="utf-8").splitlines()}
        events = g.db.execute("SELECT occurred, mode, title, status FROM events ORDER BY id DESC LIMIT 10").fetchall()
        comments = g.db.execute("SELECT mode, COUNT(*) AS total FROM comments GROUP BY mode").fetchall()
        return render_template("lab.html", lab=visible_lab, sources=sources, result=result, mode=mode,
                               values=values or {f["name"]: f["default"] for f in visible_lab["fields"]},
                               events=events, comments=comments,
                               evidence=records(g.db, "evidence") if lab_id in ("30_incident_response", "40_capstone") else [])

    @app.get("/")
    def index():
        return page()

    @app.get("/health")
    def health():
        return jsonify(status="ok", lab=lab_id, database=app.config['DB_BACKEND'])

    @app.post("/run/<mode>")
    def run(mode):
        if mode not in handlers:
            abort(404)
        data = request.form.to_dict()
        if lab_id == "12_unsafe_upload" and request.files.get("file") and request.files["file"].filename:
            upload = request.files["file"]
            body = upload.read(65537)
            data.update(filename=upload.filename, body=body)
        try:
            result = handlers[mode].run(g.db, data, {"fixture": fixture, "user": "alice", "authenticated": False,
                                                    "redirect_target": service_url(5100, "/phishing-demo"),
                                                    "database": database_path, "trusted_origin": request.host_url.rstrip("/")})
        except (ValueError, UnicodeError) as error:
            result = {"title": "Input ditolak", "detail": str(error), "status": 400}
        except Exception:
            if testing:
                raise
            app.logger.exception("Kesalahan lab %s / %s", lab_id, mode)
            result = {"title": "Kesalahan lab", "detail": "Lihat terminal untuk rincian. Tidak ada traceback yang dikirim ke browser.", "status": 500}
        g.db.execute("INSERT INTO events (mode, title, status) VALUES (?, ?, ?)",
                     (mode, result["title"], result.get("status", 200)))
        g.db.commit()
        return page(result=result, mode=mode, values=data), result.get("status", 200)

    @app.post("/reset")
    def reset():
        initialize(database_path, reset=True)
        if lab["number"] >= 15:
            with connect(database_path) as db:
                for table in ("exercise_records", "exercise_state", "profiles", "race_wallets", "payments", "idempotency"):
                    db.execute(f"DELETE FROM {table}")
                initialize_exercises(db)
        session.clear()
        return redirect(url_for("index"))

    from labcore.special import attach_special_routes
    attach_special_routes(app, lab_id, handlers)
    from labcore.advanced_routes import attach_advanced_routes
    attach_advanced_routes(app, lab_id, handlers)
    return app


def run_single(lab_id):
    import argparse
    parser = argparse.ArgumentParser(description=f"Lab {lab_id}")
    parser.add_argument("--host", type=bind_address, default="0.0.0.0", help="IP bind, default 0.0.0.0 (akses LAN)")
    parser.add_argument("--port-offset", type=int, default=0, help="Geser port lab dan service internal")
    parser.add_argument("--data-dir", type=Path, help="Direktori database/fixture alternatif untuk lab ini")
    add_database_arguments(parser)
    args = parser.parse_args()
    if not 0 <= args.port_offset <= 60000:
        parser.error("Offset port harus antara 0 dan 60000.")
    try:
        settings = load_settings(args.db, args.db_config)
        app = create_app(lab_id, allow_lan=lan_enabled(args.host), data_dir=args.data_dir, database_settings=settings)
    except (ValueError, RuntimeError, *database_errors()) as error:
        parser.error(f"Inisialisasi database gagal: {error}")
    app.config.update(PORT_OFFSET=args.port_offset, SSRF_PORT=5199 + args.port_offset)
    service = None
    if lab_id == "08_ssrf":
        from labcore.services import start_internal
        service = start_internal(port=5199 + args.port_offset)
    try:
        app.run(host=args.host, port=BY_ID[lab_id]["port"] + args.port_offset, debug=False, use_reloader=False)
    finally:
        if service:
            service.shutdown()
            service.server_close()
