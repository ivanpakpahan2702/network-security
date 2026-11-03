import secrets
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, session

from labcore.catalog import BY_ID, LABS, ROOT
from labcore.database import connect, prepare_database
from labcore.dbconfig import target_for, describe
from labcore.mysql_schema import create_schema
from labcore.dbqueries import upsert
from labcore.factory import secure_local_app
from labcore.network import request_lab
from labcore.learning import attach_learning, persistent_secret


def create_dashboard(active_ids=None, data_dir=None, allow_lan=False, database_settings=None):
    app = Flask("security_dashboard", template_folder=str(ROOT / "templates"), static_folder=str(ROOT / "static"))
    directory = Path(data_dir) if data_dir else ROOT / "instance"
    directory.mkdir(parents=True, exist_ok=True)
    database = target_for(directory / "dashboard.sqlite3", 'dashboard', database_settings)
    prepare_database(database)
    with connect(database) as db:
        create_schema(db, 'dashboard', "CREATE TABLE IF NOT EXISTS progress (lab_id TEXT PRIMARY KEY, completed INTEGER NOT NULL);")
    app.config.update(SECRET_KEY=persistent_secret(directory), SESSION_COOKIE_NAME="lab_dashboard",
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", MAX_CONTENT_LENGTH=8192,
                      ALLOW_LAN=allow_lan, DATABASE=database, **describe(database))
    secure_local_app(app)
    attach_learning(app, database)
    active = set(active_ids or [])

    @app.get("/")
    def index():
        with connect(database) as db:
            completed = {row["lab_id"] for row in db.execute("SELECT lab_id FROM progress WHERE completed=1")}
        return render_template("dashboard.html", labs=[request_lab(lab) for lab in LABS], active=active, completed=completed)

    @app.get("/health")
    def health():
        return jsonify(status="ok", active=sorted(active), labs=len(active), database=app.config['DB_BACKEND'])

    @app.post("/progress/<lab_id>")
    def progress(lab_id):
        if lab_id not in BY_ID:
            abort(404)
        completed = int(request.form.get("completed") == "1")
        with connect(database) as db:
            upsert(db, 'progress', dict(lab_id=lab_id, completed=completed), ('lab_id',))
        return redirect("/#" + lab_id)

    @app.get("/attacker/csrf/<mode>")
    def attacker(mode):
        if mode not in {"vulnerable", "secure"}:
            abort(404)
        return render_template("attacker.html", mode=mode)

    @app.get("/attacker/cors/<mode>")
    def cors_attacker(mode):
        if mode not in {"vulnerable", "secure"}:
            abort(404)
        from labcore.network import service_url
        response = app.make_response(render_template("cors_attacker.html", mode=mode))
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            f"connect-src 'self' {service_url(5133)}; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'")
        return response

    @app.get("/phishing-demo")
    def phishing_demo():
        return render_template("message.html", title="Tujuan penyerang dummy", message=(
            "Anda telah meninggalkan origin lab open redirect (port 5111) dan tiba di dashboard port 5100. "
            "Dalam serangan nyata, tujuan ini dapat berupa situs phishing. Demo ini tidak meminta atau menyimpan kredensial."))

    return app
