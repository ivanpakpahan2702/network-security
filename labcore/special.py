"""Route browser/HTTP untuk membuktikan hasil lab, terpisah dari halaman kontrol."""
import io
import secrets
from flask import Response, abort, g, redirect, render_template, request, send_file, session
from labcore.network import service_url


def attach_special_routes(app, lab_id, handlers):
    def check_mode(mode):
        if mode not in handlers:
            abort(404)

    def preview_response(html, mode):
        response = Response(html, content_type="text/html; charset=utf-8")
        # sandbox juga berlaku ketika URL pratinjau dibuka sebagai tab.
        response.headers["Content-Security-Policy"] = (
            "sandbox allow-scripts; default-src 'none'; "
            + ("script-src 'unsafe-inline'; " if mode == "vulnerable" else "script-src 'none'; ")
            + "style-src 'none'; connect-src 'none'; img-src 'none'; form-action 'none'; "
              "base-uri 'none'; frame-ancestors 'self'")
        return response

    if lab_id in {"02_reflected_xss", "03_stored_xss"}:
        @app.get("/preview/<mode>")
        def xss_preview(mode):
            check_mode(mode)
            if lab_id == "02_reflected_xss":
                html = handlers[mode].render_input(request.args.get("query", "")[:4096])
            else:
                comments = g.db.execute("SELECT body FROM comments WHERE mode=? ORDER BY id", (mode,)).fetchall()
                html = handlers[mode].render_comments([row["body"] for row in comments])
            return preview_response(html, mode)

    if lab_id == "04_csrf":
        @app.get("/bank/<mode>")
        def bank(mode):
            check_mode(mode)
            session["bank_user"] = "alice"
            session.setdefault("bank_csrf", secrets.token_urlsafe(32))
            balance = g.db.execute("SELECT balance FROM wallets WHERE mode=?", (mode,)).fetchone()["balance"]
            return render_template("bank.html", lab=app.config["LAB"], mode=mode, balance=balance,
                                   bank_token=session["bank_csrf"], result=None)

        @app.post("/bank/<mode>/transfer")
        def transfer(mode):
            check_mode(mode)
            try:
                result = handlers[mode].run(g.db, request.form, {
                    "authenticated": session.get("bank_user") == "alice",
                    "expected_token": session.get("bank_csrf", ""),
                    "origin": request.headers.get("Origin"), "expected_origin": request.host_url.rstrip("/")})
            except ValueError as error:
                result = dict(title="Input transfer ditolak", detail=str(error), status=400)
            g.db.execute("INSERT INTO events (mode, title, status) VALUES (?, ?, ?)",
                         (mode, result["title"], result.get("status", 200)))
            g.db.commit()
            balance = g.db.execute("SELECT balance FROM wallets WHERE mode=?", (mode,)).fetchone()["balance"]
            return render_template("bank.html", lab=app.config["LAB"], mode=mode, balance=balance,
                                   bank_token=session.get("bank_csrf", ""), result=result), result.get("status", 200)

    if lab_id == "11_open_redirect":
        @app.get("/redirect/<mode>")
        def redirect_demo(mode):
            check_mode(mode)
            destination = request.args.get("next", "/welcome")
            try:
                approved = handlers[mode].destination(destination, allowed_target=service_url(5100, "/phishing-demo"))
            except ValueError as error:
                abort(400, str(error))
            return redirect(approved, code=302)

        @app.get("/welcome")
        def welcome():
            return render_template("message.html", title="Redirect sah", message="Anda tiba di halaman internal /welcome.")

    if lab_id == "12_unsafe_upload":
        @app.get("/uploads/<mode>/<int:upload_id>")
        def uploaded(mode, upload_id):
            check_mode(mode)
            row = g.db.execute("SELECT * FROM uploads WHERE id=? AND mode=?", (upload_id, mode)).fetchone()
            if not row:
                abort(404)
            if mode == "secure":
                return send_file(io.BytesIO(row["body"]), mimetype="text/plain", as_attachment=True,
                                 download_name=row["name"])
            if row["mime"] == "text/html":
                return preview_response(row["body"], mode)
            return Response(row["body"], content_type="text/plain; charset=utf-8")
