"""Tes perilaku: buktikan exploit, perbaikan, input sah, dan batas lingkungan."""
import io
import re
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.serving import make_server

from labcore.catalog import BY_ID, LABS
from labcore.dashboard import create_dashboard
from labcore.database import connect
from labcore.factory import create_app
from labcore.runtime import local_fetch
from labcore.services import internal_app


class LabTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="security-lab-tests-")
        self.addCleanup(self.directory.cleanup)
        self.clients = {}
        self.apps = {}

    def client(self, lab_id):
        if lab_id not in self.clients:
            app = create_app(lab_id, data_dir=Path(self.directory.name) / lab_id, testing=True)
            self.apps[lab_id] = app
            self.clients[lab_id] = app.test_client()
        return self.clients[lab_id]

    def get(self, lab_id, path="/"):
        return self.client(lab_id).get(path, base_url=BY_ID[lab_id]["url"])

    def token(self, lab_id):
        response = self.get(lab_id)
        self.assertEqual(response.status_code, 200)
        return re.search(r'name="_lab_token" value="([^"]+)"', response.text).group(1)

    def post(self, lab_id, mode, data=None):
        values = dict(BY_ID[lab_id]["attack"] if data is None else data)
        values["_lab_token"] = self.token(lab_id)
        return self.client(lab_id).post("/run/" + mode, data=values, base_url=BY_ID[lab_id]["url"],
                                        headers={"Origin": BY_ID[lab_id]["url"]})

    def test_all_pages_render_actual_source(self):
        for lab in LABS:
            with self.subTest(lab=lab["id"]):
                response = self.get(lab["id"])
                self.assertEqual(response.status_code, 200)
                self.assertIn(f'labs/{lab["id"]}/vulnerable.py', response.text)
                self.assertIn(f'labs/{lab["id"]}/secure.py', response.text)
                self.assertIn("Kode yang dieksekusi", response.text)

    def test_sql_injection_bypasses_only_vulnerable(self):
        lab = "01_sql_injection"
        self.assertEqual(self.post(lab, "vulnerable").status_code, 200)
        self.assertEqual(self.post(lab, "secure").status_code, 401)
        for mode in ("vulnerable", "secure"):
            self.assertEqual(self.post(lab, mode, BY_ID[lab]["normal"]).status_code, 200)

    def test_sql_union_and_syntax_errors_are_contained(self):
        lab = "01_sql_injection"
        payload = {"username": "' UNION SELECT 999, 'injected-user' -- ", "password": "x"}
        self.assertIn("Anda masuk sebagai injected-user", self.post(lab, "vulnerable", payload).text)
        self.assertEqual(self.post(lab, "secure", payload).status_code, 401)
        self.assertEqual(self.post(lab, "vulnerable", {"username": "' OR (", "password": "x"}).status_code, 400)

    def test_reflected_xss_output_escaping_and_sandbox(self):
        lab = "02_reflected_xss"
        for mode in ("vulnerable", "secure"):
            self.assertEqual(self.post(lab, mode).status_code, 200)
            response = self.get(lab, f"/preview/{mode}?query=%3Cscript%3Ealert(1)%3C/script%3E")
            self.assertIn("sandbox allow-scripts", response.headers["Content-Security-Policy"])
            self.assertIn("connect-src 'none'", response.headers["Content-Security-Policy"])
            self.assertIn("<script>" if mode == "vulnerable" else "&lt;script&gt;", response.text)

    def test_stored_xss_persists_and_modes_do_not_mix(self):
        lab = "03_stored_xss"
        self.post(lab, "vulnerable")
        self.assertIn("<script>", self.get(lab, "/preview/vulnerable").text)
        self.assertNotIn("<script>", self.get(lab, "/preview/secure").text)
        self.post(lab, "secure")
        self.assertIn("&lt;script&gt;", self.get(lab, "/preview/secure").text)
        # Payload tetap tersimpan setelah instance Flask dibuat ulang.
        app = create_app(lab, data_dir=Path(self.directory.name) / lab, testing=True)
        response = app.test_client().get("/preview/vulnerable", base_url=BY_ID[lab]["url"])
        self.assertIn("<script>", response.text)

    def test_csrf_requires_session_then_blocks_missing_token(self):
        lab = "04_csrf"
        client = self.client(lab)
        url = BY_ID[lab]["url"]
        data = {"amount": "100", "recipient": "penyerang-demo"}
        self.assertEqual(client.post("/bank/vulnerable/transfer", data=data, base_url=url).status_code, 401)
        for mode in ("vulnerable", "secure"):
            self.get(lab, "/bank/" + mode)
            response = client.post(f"/bank/{mode}/transfer", data=data, base_url=url,
                                   headers={"Origin": "http://127.0.0.1:5100"})
            self.assertEqual(response.status_code, 200 if mode == "vulnerable" else 403)
            self.assertIn("900" if mode == "vulnerable" else "1000", response.text)

    def test_csrf_valid_token_and_origin_allow_legitimate_transfer(self):
        lab = "04_csrf"
        page = self.get(lab, "/bank/secure")
        token = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
        response = self.client(lab).post("/bank/secure/transfer", base_url=BY_ID[lab]["url"],
             data={"amount": "50", "recipient": "teman-demo", "csrf_token": token},
             headers={"Origin": BY_ID[lab]["url"]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("950", response.text)
        response = self.client(lab).post("/bank/secure/transfer", base_url=BY_ID[lab]["url"],
             data={"amount": "50", "csrf_token": token}, headers={"Origin": "http://127.0.0.1:5100"})
        self.assertEqual(response.status_code, 403)

    def test_csrf_invalid_amount_does_not_change_balance(self):
        lab = "04_csrf"
        self.get(lab, "/bank/vulnerable")
        response = self.client(lab).post("/bank/vulnerable/transfer", base_url=BY_ID[lab]["url"],
                                         data={"amount": "-100"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("1000", response.text)

    def test_idor_does_not_allow_changing_identity(self):
        lab = "05_idor"
        self.assertIn("RAHASIA DUMMY BOB", self.post(lab, "vulnerable").text)
        self.assertEqual(self.post(lab, "secure", {"invoice_id": "2", "user": "bob"}).status_code, 404)
        for mode in ("vulnerable", "secure"):
            self.assertEqual(self.post(lab, mode, {"invoice_id": "1"}).status_code, 200)

    def test_path_traversal_and_machine_boundary(self):
        lab = "06_path_traversal"
        self.assertIn("SECRET_PATH_DEMO_2026", self.post(lab, "vulnerable").text)
        self.assertEqual(self.post(lab, "secure").status_code, 400)
        for mode in ("vulnerable", "secure"):
            self.assertEqual(self.post(lab, mode, {"filename": "readme.txt"}).status_code, 200)
            self.assertEqual(self.post(lab, mode, {"filename": "../../../../README.md"}).status_code, 400)
            self.assertEqual(self.post(lab, mode, {"filename": str(Path(__file__).resolve())}).status_code, 400)

    def test_command_injection_is_emulated_and_secure_input_is_validated(self):
        lab = "07_command_injection"
        self.assertIn("lab-service-account", self.post(lab, "vulnerable").text)
        self.assertEqual(self.post(lab, "secure").status_code, 400)
        response = self.post(lab, "vulnerable", {"host": "127.0.0.1 && cat /lab/secret.txt"})
        self.assertIn("SECRET_COMMAND_DEMO_2026", response.text)
        for mode in ("vulnerable", "secure"):
            self.assertEqual(self.post(lab, mode, {"host": "127.0.0.1"}).status_code, 200)

    def test_ssrf_fixed_route_allowlist(self):
        lab = "08_ssrf"
        with patch("labcore.runtime.http.client.HTTPConnection") as transport:
            upstream = transport.return_value.getresponse.return_value
            upstream.status = 200
            upstream.read.return_value = b'{"api_key":"DUMMY-KEY"}'
            self.assertIn("DUMMY-KEY", self.post(lab, "vulnerable").text)
            self.assertEqual(self.post(lab, "secure").status_code, 400)
            self.assertEqual(self.post(lab, "secure", BY_ID[lab]["normal"]).status_code, 200)
            for url in ("http://example.com", "http://127.0.0.1:80", "file:///etc/passwd", "http://127.0.0.1:5199@evil.example/x"):
                self.assertEqual(self.post(lab, "vulnerable", {"url": url}).status_code, 400)

    def test_brute_force_limit_persists_between_requests(self):
        lab = "09_brute_force"
        self.assertIn("Password ditemukan", self.post(lab, "vulnerable").text)
        self.assertEqual(self.post(lab, "secure").status_code, 429)
        self.assertEqual(self.post(lab, "secure", {"candidates": "LabUser!2026"}).status_code, 429)
        self.client(lab).post("/reset", data={"_lab_token": self.token(lab)}, base_url=BY_ID[lab]["url"])
        self.assertEqual(self.post(lab, "secure", {"candidates": "LabUser!2026"}).status_code, 200)

    def test_hash_salt_and_correct_password_not_magic_prevention(self):
        lab = "10_password_hashing"
        for mode, expected in (("vulnerable", "True"), ("secure", "False")):
            response = self.post(lab, mode)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Kandidat ditemukan: LabUser!2026", response.text)
            self.assertIn("Digest alice == bob: " + expected, response.text)

    def test_open_redirect_real_location_header(self):
        lab = "11_open_redirect"
        target = "http://127.0.0.1:5100/phishing-demo"
        response = self.get(lab, "/redirect/vulnerable?next=" + target)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], target)
        self.assertEqual(self.get(lab, "/redirect/secure?next=" + target).status_code, 400)
        self.assertEqual(self.get(lab, "/redirect/secure?next=//127.0.0.1:5100/phishing-demo").status_code, 400)
        for mode in ("vulnerable", "secure"):
            response = self.get(lab, f"/redirect/{mode}?next=/welcome")
            self.assertEqual(response.headers["Location"], "/welcome")
        self.assertEqual(self.get(lab, "/redirect/vulnerable?next=https://example.com").status_code, 400)

    def test_upload_html_vs_attachment_and_multipart(self):
        lab = "12_unsafe_upload"
        self.assertEqual(self.post(lab, "vulnerable").status_code, 200)
        response = self.get(lab, "/uploads/vulnerable/1")
        self.assertIn("text/html", response.content_type)
        self.assertIn("sandbox", response.headers["Content-Security-Policy"])
        self.assertEqual(self.post(lab, "secure").status_code, 400)
        values = {"file": (io.BytesIO(b"<script>alert(1)</script>"), "memo.txt"), "_lab_token": self.token(lab)}
        self.assertEqual(self.client(lab).post("/run/secure", data=values, base_url=BY_ID[lab]["url"]).status_code, 200)
        response = self.get(lab, "/uploads/secure/2")
        self.assertIn("attachment", response.headers["Content-Disposition"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertTrue(response.content_type.startswith("text/plain"))

    def test_upload_size_and_binary_content_rejected(self):
        lab = "12_unsafe_upload"
        for body in (b"\x00\xff\x01", b"a" * 65537):
            values = {"file": (io.BytesIO(body), "memo.txt"), "_lab_token": self.token(lab)}
            response = self.client(lab).post("/run/secure", data=values, base_url=BY_ID[lab]["url"])
            self.assertEqual(response.status_code, 400)

    def test_ssti_executes_expression_but_not_in_secure_mode(self):
        lab = "13_ssti"
        vulnerable = self.post(lab, "vulnerable")
        self.assertIn("Halo 49", vulnerable.text)
        self.assertIn("SECRET_TEMPLATE_DEMO_2026", vulnerable.text)
        secure = self.post(lab, "secure")
        self.assertIn("Halo {{ 7 * 7 }}", secure.text)
        result_section = secure.text.split('<section class="panel result"')[1].split('<section class="panel source-panel"')[0]
        self.assertNotIn("SECRET_TEMPLATE_DEMO_2026", result_section)

    def test_ssti_sandbox_rejects_objects_calls_loops_and_amplification(self):
        lab = "13_ssti"
        for payload in ("{{ secret.__class__ }}", "{{ range(1000) }}", "{% for x in range(10) %}x{% endfor %}",
                        "{{ 999 * 999 }}", "{{ 'x' * 999 }}", "{{ 7 ** 7 }}"):
            with self.subTest(payload=payload):
                self.assertEqual(self.post(lab, "vulnerable", {"template": payload}).status_code, 400)

    def test_network_rules_and_legitimate_flows(self):
        lab = "14_network_segmentation"
        self.assertEqual(self.post(lab, "vulnerable").status_code, 200)
        self.assertEqual(self.post(lab, "secure").status_code, 403)
        for source, target, port in (("workstation", "web", "443"), ("web", "database", "5432"), ("admin", "admin", "22")):
            self.assertEqual(self.post(lab, "secure", {"source": source, "target": target, "port": port}).status_code, 200)

    def test_local_controls_reject_remote_hosts_and_origin(self):
        lab = "01_sql_injection"
        client = self.client(lab)
        self.assertEqual(client.get("/", base_url="http://evil.example").status_code, 403)
        self.assertEqual(client.get("/", base_url=BY_ID[lab]["url"], environ_overrides={"REMOTE_ADDR": "192.0.2.10"}).status_code, 403)
        self.assertEqual(client.post("/reset", base_url=BY_ID[lab]["url"]).status_code, 403)
        token = self.token(lab)
        response = client.post("/reset", base_url=BY_ID[lab]["url"], data={"_lab_token": token}, headers={"Origin": "https://evil.example"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(client.post("/reset", base_url=BY_ID[lab]["url"], data={"_lab_token": "ü"}).status_code, 403)

    def test_reset_is_scoped_and_restores_fixtures(self):
        lab = "03_stored_xss"
        self.post(lab, "vulnerable")
        other = "01_sql_injection"
        self.post(other, "vulnerable")
        response = self.client(lab).post("/reset", base_url=BY_ID[lab]["url"], data={"_lab_token": self.token(lab)})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("<script>", self.get(lab, "/preview/vulnerable").text)
        with connect(self.apps[other].config["DATABASE"]) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM events").fetchone()[0], 1)

    def test_dashboard_progress_persists(self):
        directory = Path(self.directory.name) / "dashboard"
        app = create_dashboard(list(BY_ID), data_dir=directory)
        client = app.test_client()
        response = client.get("/", base_url="http://127.0.0.1:5100")
        self.assertEqual(response.status_code, 200)
        token = re.search(r'name="_lab_token" value="([^"]+)"', response.text).group(1)
        response = client.post("/progress/01_sql_injection", base_url="http://127.0.0.1:5100", data={"_lab_token": token, "completed": "1"})
        self.assertEqual(response.status_code, 302)
        second_app = create_dashboard(data_dir=directory)
        response = second_app.test_client().get("/", base_url="http://127.0.0.1:5100")
        self.assertIn(f"1 / {len(LABS)}", response.text)
        for path in ("/attacker/csrf/vulnerable", "/attacker/csrf/secure", "/phishing-demo"):
            self.assertEqual(client.get(path, base_url="http://127.0.0.1:5100").status_code, 200)


class RealTransportTests(unittest.TestCase):
    def test_real_loopback_ssrf_transport(self):
        app = internal_app()
        server = make_server("127.0.0.1", 0, app, threaded=True)
        port = server.server_port
        app.config["SSRF_PORT"] = port
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with app.app_context():
                status, body = local_fetch(f"http://127.0.0.1:{port}/internal/metadata")
                self.assertEqual(status, 200)
                self.assertIn("DUMMY-KEY-NOT-A-REAL-SECRET", body)
                status, body = local_fetch(f"http://127.0.0.1:{port}/public/status")
                self.assertEqual(status, 200)
                self.assertIn("healthy", body)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
