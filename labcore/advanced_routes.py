"""Artefak latihan serta demo CORS browser dengan sesi dan respons HTTP nyata."""
from flask import Response, abort, g, jsonify, render_template, request, send_file, session
from labcore.exercises import evidence_bytes


def attach_advanced_routes(app, lab_id, handlers):
    if lab_id == "27_pcap_analysis":
        @app.get("/artifacts/<name>.pcap")
        def pcap(name):
            if name not in {"normal", "scan", "incomplete"}:
                abort(404)
            return send_file(app.config["FIXTURE"] / "captures" / f"{name}.pcap",
                             mimetype="application/vnd.tcpdump.pcap", as_attachment=True)

    if lab_id in {"30_incident_response", "40_capstone"}:
        @app.get("/artifacts/evidence.json")
        def evidence():
            response = Response(evidence_bytes(g.db), content_type="application/json; charset=utf-8")
            response.headers["Content-Disposition"] = 'attachment; filename="evidence.json"'
            return response

    if lab_id == "33_cors_policy":
        @app.get("/account")
        def account():
            session["cors_user"] = "alice"
            return render_template("message.html", title="Sesi API Alice aktif", message=(
                "Cookie sesi dummy telah dibuat. Buka halaman penyerang CORS dari dashboard pada host yang sama; "
                "bandingkan pembacaan API rentan dan diperbaiki. Port berbeda berarti origin berbeda."))

        @app.get("/api/<mode>/account")
        def api_account(mode):
            if mode not in handlers:
                abort(404)
            response = (jsonify(account="alice", balance=250000, note="DATA-API-DUMMY") if session.get("cors_user") == "alice"
                        else jsonify(error="Buka /account dahulu untuk membuat sesi dummy."))
            if not session.get("cors_user"):
                response.status_code = 401
            for name, value in handlers[mode].cors_headers(request.headers.get("Origin", ""), request.host_url.rstrip("/")).items():
                response.headers[name] = value
            response.vary.add("Origin")
            return response
