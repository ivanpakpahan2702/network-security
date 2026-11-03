import argparse
import re
import tempfile
import unittest
from pathlib import Path

from labcore.dashboard import create_dashboard
from labcore.factory import create_app
from labcore.network import allowed_address, bind_address
from labcore.services import internal_app


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="lab-lan-tests-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.server = "192.168.5.51"
        self.remote = {"REMOTE_ADDR": "192.168.5.60"}

    def test_lan_address_scope_and_bind_validation(self):
        for address in ("127.0.0.1", "::1", "192.168.5.51", "10.1.2.3", "172.18.0.1", "100.95.254.61", "fd00::1"):
            with self.subTest(address=address):
                self.assertTrue(allowed_address(address, allow_lan=True))
        for address in ("203.0.113.10", "192.0.2.10", "8.8.8.8", "0.0.0.0", "evil.example", None):
            self.assertFalse(allowed_address(address, allow_lan=True))
        self.assertFalse(allowed_address("192.168.5.51"))
        self.assertEqual(bind_address("0.0.0.0"), "0.0.0.0")
        with self.assertRaises(argparse.ArgumentTypeError):
            bind_address("0.0.00")

    def test_dashboard_links_and_csp_follow_lan_ip(self):
        app = create_dashboard(data_dir=self.root, allow_lan=True)
        response = app.test_client().get("/", base_url=f"http://{self.server}:5100", environ_overrides=self.remote)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'href="http://{self.server}:5101"', response.text)
        self.assertNotIn('href="http://127.0.0.1:', response.text)
        self.assertIn(f"http://{self.server}:5104", response.headers["Content-Security-Policy"])
        self.assertNotIn("127.0.0.1", response.headers["Content-Security-Policy"])

    def test_lan_forms_keep_token_and_origin_validation(self):
        app = create_app("01_sql_injection", data_dir=self.root, testing=True, allow_lan=True)
        client = app.test_client()
        base = f"http://{self.server}:5101"
        response = client.get("/", base_url=base, environ_overrides=self.remote)
        token = re.search(r'name="_lab_token" value="([^"]+)"', response.text).group(1)
        data = {"username": "admin", "password": "LabAdmin!2026", "_lab_token": token}
        response = client.post("/run/secure", base_url=base, data=data, headers={"Origin": base}, environ_overrides=self.remote)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Login berhasil", response.text)
        response = client.post("/run/secure", base_url=base, data=data, headers={"Origin": "https://evil.example"}, environ_overrides=self.remote)
        self.assertEqual(response.status_code, 403)
        response = client.post("/run/secure", base_url=base, data={"username": "admin"}, headers={"Origin": base}, environ_overrides=self.remote)
        self.assertEqual(response.status_code, 403)

    def test_lan_enabled_still_rejects_public_clients_and_dns_hosts(self):
        app = create_app("01_sql_injection", data_dir=self.root, testing=True, allow_lan=True)
        client = app.test_client()
        for base, remote in ((f"http://{self.server}:5101", "203.0.113.10"),
                             ("http://evil.example:5101", "192.168.5.60"), ("http://0.0.0.0:5101", "127.0.0.1")):
            self.assertEqual(client.get("/", base_url=base, environ_overrides={"REMOTE_ADDR": remote}).status_code, 403)

    def test_csrf_attacker_targets_same_lan_server(self):
        app = create_dashboard(data_dir=self.root, allow_lan=True)
        response = app.test_client().get("/attacker/csrf/secure", base_url=f"http://{self.server}:5100", environ_overrides=self.remote)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'action="http://{self.server}:5104/bank/secure/transfer"', response.text)
        self.assertNotIn("127.0.0.1", response.text)

    def test_redirect_example_and_response_use_lan_ip(self):
        app = create_app("11_open_redirect", data_dir=self.root, testing=True, allow_lan=True)
        client = app.test_client()
        base = f"http://{self.server}:5111"
        target = f"http://{self.server}:5100/phishing-demo"
        page = client.get("/", base_url=base, environ_overrides=self.remote)
        self.assertIn(f'value="{target}"', page.text)
        token = re.search(r'name="_lab_token" value="([^"]+)"', page.text).group(1)
        response = client.post("/run/vulnerable", data={"next": target, "_lab_token": token}, base_url=base,
                               headers={"Origin": base}, environ_overrides=self.remote)
        self.assertEqual(response.status_code, 200)
        response = client.get("/redirect/vulnerable", query_string={"next": target}, base_url=base, environ_overrides=self.remote)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], target)
        self.assertEqual(client.get("/redirect/secure", query_string={"next": target}, base_url=base, environ_overrides=self.remote).status_code, 400)

    def test_internal_ssrf_service_remains_loopback_only(self):
        client = internal_app().test_client()
        response = client.get("/internal/metadata", base_url=f"http://{self.server}:5199", environ_overrides=self.remote)
        self.assertEqual(response.status_code, 403)
        response = client.get("/internal/metadata", base_url="http://127.0.0.1:5199", environ_overrides=self.remote)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(client.get("/internal/metadata", base_url="http://127.0.0.1:5199").status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
