"""Transport terbatas untuk demo. Ini batas keselamatan lab, bukan mitigasi bug aplikasi."""
import http.client
import ipaddress
import re
from urllib.parse import urlsplit
from flask import current_app, has_app_context


def contained_read(fixture, path):
    resolved = path.resolve()
    if not resolved.is_relative_to(fixture.resolve()):
        raise ValueError("Batas lab: hanya file di direktori fixture yang boleh dibaca.")
    if not resolved.is_file():
        raise ValueError("File fixture tidak ditemukan.")
    if resolved.stat().st_size > 65536:
        raise ValueError("File terlalu besar.")
    return resolved.read_text(encoding="utf-8")


def local_fetch(url):
    """HTTP nyata; koneksi selalu hardcoded, proxy dan redirect tidak digunakan."""
    parsed = urlsplit(url)
    port = current_app.config.get("SSRF_PORT", 5199) if has_app_context() else 5199
    if (parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.port != port
            or parsed.username or parsed.password or parsed.fragment):
        raise ValueError(f"Batas transport lab: hanya http://127.0.0.1:{port} diizinkan.")
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", parsed.path + ("?" + parsed.query if parsed.query else ""))
        response = connection.getresponse()
        return response.status, response.read(65536).decode("utf-8", errors="replace")
    except OSError as error:
        raise ValueError("Service internal belum aktif. Jalankan python run.py atau app SSRF.") from error
    finally:
        connection.close()


def shell_emulator(command):
    outputs = []
    for part in re.split(r";|&&", command):
        words = part.strip().split()
        if not words:
            continue
        if words[0] == "ping" and len(words) == 2:
            try:
                host = str(ipaddress.ip_address(words[1]))
            except ValueError:
                outputs.append("ping dummy: host tidak valid")
            else:
                outputs.append(f"ping dummy: balasan dari {host}")
        elif words == ["whoami"]:
            outputs.append("lab-service-account (DUMMY)")
        elif words == ["cat", "/lab/secret.txt"]:
            outputs.append("SECRET_COMMAND_DEMO_2026 (DUMMY)")
        else:
            outputs.append("Batas emulator: perintah ini tidak tersedia.")
    return "\n".join(outputs)


def argv_emulator(arguments):
    if len(arguments) != 2 or arguments[0] != "ping":
        raise ValueError("Argumen diagnostik tidak valid.")
    return f"ping dummy: balasan dari {ipaddress.ip_address(arguments[1])}"
