import threading

from flask import Flask, jsonify
from werkzeug.serving import make_server

from labcore.factory import secure_local_app


def internal_app():
    app = Flask("internal_dummy")
    secure_local_app(app)

    @app.get("/public/status")
    def status():
        return jsonify(service="inventory-demo", status="healthy", data="informasi publik dummy")

    @app.get("/internal/metadata")
    def metadata():
        return jsonify(service="metadata-demo", api_key="DUMMY-KEY-NOT-A-REAL-SECRET", role="lab-only")

    return app


def start_internal(port=5199):
    # Jangan memakai service lain yang kebetulan sudah menduduki port tersebut.
    server = make_server("127.0.0.1", port, internal_app(), threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True, name="internal-dummy").start()
    return server
