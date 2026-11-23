import unittest

from werkzeug.test import Client
from werkzeug.wrappers import Response

from server_course import ASSETS, PUBLIC_HOST, with_public_course


class TestPublicCourse(unittest.TestCase):
    def setUp(self):
        local = Response("Local dashboard")
        self.client = Client(with_public_course(local))
        self.public_url = f"https://{PUBLIC_HOST}"

    def test_public_host_serves_only_course_assets(self):
        for path in ASSETS:
            with self.subTest(path=path):
                result = self.client.get(path, base_url=self.public_url)
                self.assertEqual(result.status_code, 200)
                self.assertIn("connect-src 'none'", result.headers["Content-Security-Policy"])
                self.assertNotIn("Set-Cookie", result.headers)
                if path == "/":
                    self.assertIn("Ruang Server", result.text)
        for path in ("/health", "/learn", "/static/style.css", "/database.local.toml", "/labs/"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path, base_url=self.public_url).status_code, 404)

    def test_public_head_and_post(self):
        head = self.client.head("/", base_url=self.public_url)
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.data, b"")
        post = self.client.post("/", base_url=self.public_url)
        self.assertEqual(post.status_code, 405)
        self.assertEqual(post.headers["Allow"], "GET, HEAD")

    def test_proxied_private_host_cannot_reach_dashboard(self):
        for headers in ({"CF-Ray": "test"}, {"X-Forwarded-Host": PUBLIC_HOST}):
            with self.subTest(headers=headers):
                result = self.client.get("/", base_url="http://localhost:5100", headers=headers)
                self.assertEqual(result.status_code, 403)
                self.assertNotIn("Local dashboard", result.text)

    def test_direct_local_access_preserves_dashboard(self):
        result = self.client.get("/", base_url="http://localhost:5100")
        self.assertEqual(result.text, "Local dashboard")
