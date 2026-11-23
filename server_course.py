"""Serve the public server course from an allowlist of static files."""

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

COURSE = Path(__file__).resolve().parent / "server-course"
PUBLIC_HOST = "ivanpakpahan.my.id"
PUBLIC_AUTHORITIES = {PUBLIC_HOST, f"{PUBLIC_HOST}:80", f"{PUBLIC_HOST}:443"}
PROXY_HEADERS = (
    "HTTP_CF_RAY", "HTTP_CF_CONNECTING_IP", "HTTP_CF_VISITOR", "HTTP_CDN_LOOP",
    "HTTP_FORWARDED", "HTTP_X_FORWARDED_HOST", "HTTP_X_FORWARDED_FOR",
    "HTTP_X_FORWARDED_PROTO",
)
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/course.css": ("course.css", "text/css; charset=utf-8"),
    "/lessons.js": ("lessons.js", "text/javascript; charset=utf-8"),
    "/course.js": ("course.js", "text/javascript; charset=utf-8"),
}
SECURITY_HEADERS = (
    ("Cache-Control", "no-cache"),
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "strict-origin-when-cross-origin"),
    (
        "Content-Security-Policy",
        "default-src 'self'; object-src 'none'; base-uri 'none'; "
        "frame-ancestors 'none'; form-action 'none'; connect-src 'none'",
    ),
)


def response(status, body, content_type="text/plain; charset=utf-8"):
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
        *SECURITY_HEADERS,
    ]
    return status, headers, body


def course_response(path, method):
    if method not in {"GET", "HEAD"}:
        status, headers, body = response(HTTPStatus.METHOD_NOT_ALLOWED, b"Gunakan GET atau HEAD.\n")
        headers.append(("Allow", "GET, HEAD"))
        return status, headers, body
    resource = ASSETS.get(path)
    if not resource:
        return response(HTTPStatus.NOT_FOUND, b"Halaman tidak ditemukan.\n")
    filename, content_type = resource
    return response(HTTPStatus.OK, (COURSE / filename).read_bytes(), content_type)


def with_public_course(local_dashboard):
    """Dispatch the public hostname before any of the local dashboard routes."""
    def dispatch(environ, start_response):
        method = environ["REQUEST_METHOD"]
        if environ.get("HTTP_HOST", "").lower() in PUBLIC_AUTHORITIES:
            status, headers, body = course_response(environ["PATH_INFO"], method)
        elif any(name in environ for name in PROXY_HEADERS):
            status, headers, body = response(HTTPStatus.FORBIDDEN, b"Host tunnel tidak diizinkan.\n")
        else:
            return local_dashboard(environ, start_response)
        start_response(f"{status.value} {status.phrase}", headers)
        return [] if method == "HEAD" else [body]

    return dispatch


class CourseHandler(BaseHTTPRequestHandler):
    server_version = "ServerCourse"
    sys_version = ""
    timeout = 10

    def do_GET(self):
        self.serve_asset()

    def do_HEAD(self):
        self.serve_asset()

    def do_POST(self):
        self.serve_asset()

    def serve_asset(self):
        try:
            path = urlsplit(self.path).path
        except ValueError:
            path = ""
        status, headers, body = course_response(path, self.command)
        self.send_response(status)
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Portal belajar server untuk tunnel lokal")
    parser.add_argument("--port", type=int, default=5080)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port harus antara 1 dan 65535.")
    try:
        with ThreadingHTTPServer(("127.0.0.1", args.port), CourseHandler) as server:
            print(f"Ruang Server aktif di http://127.0.0.1:{args.port}/", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    except OSError as error:
        parser.exit(1, f"Gagal membuka port {args.port}: {error}\n")


if __name__ == "__main__":
    main()
