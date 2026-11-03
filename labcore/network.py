"""Alamat akses lab: loopback atau IP privat LAN/VPN, tanpa mempercayai proxy header."""
import argparse
import ipaddress
import socket
from urllib.parse import urlsplit

from flask import current_app, request

PRIVATE_NETWORKS = tuple(ipaddress.ip_network(value) for value in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10", "fc00::/7", "fe80::/10"))


def allowed_address(value, allow_lan=False):
    try:
        address = ipaddress.ip_address(value)
    except (ValueError, TypeError):
        return False
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    return address.is_loopback or (allow_lan and any(address in network for network in PRIVATE_NETWORKS))


def bind_address(value):
    try:
        address = ipaddress.ip_address(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Gunakan IP bind yang valid, misalnya 0.0.0.0 atau 127.0.0.1.") from error
    if address.is_unspecified or allowed_address(str(address), allow_lan=True):
        return str(address)
    raise argparse.ArgumentTypeError("Bind lab harus menggunakan loopback, IP privat LAN/VPN, atau alamat wildcard.")


def lan_enabled(host):
    return not ipaddress.ip_address(host).is_loopback


def service_url(port, path=""):
    host = urlsplit("http://" + request.host).hostname
    authority = f"[{host}]" if ":" in host else host
    port += current_app.config.get("PORT_OFFSET", 0)
    return f"{request.scheme}://{authority}:{port}{path}"


def request_lab(lab):
    """Salin katalog per request agar URL antarport mengikuti host yang dibuka."""
    visible = {**lab, "url": service_url(lab["port"]), "attack": dict(lab["attack"]),
               "fields": [dict(field) for field in lab["fields"]]}
    if lab["id"] == "11_open_redirect":
        target = service_url(5100, "/phishing-demo")
        visible["attack"]["next"] = target
        visible["fields"][0]["default"] = target
    if lab["id"] == "08_ssrf":
        port = current_app.config.get("SSRF_PORT", 5199)
        visible["normal"] = {"url": f"http://127.0.0.1:{port}/public/status"}
        visible["attack"]["url"] = f"http://127.0.0.1:{port}/internal/metadata"
        visible["fields"][0]["default"] = visible["attack"]["url"]
    if lab["id"] == "33_cors_policy":
        visible["normal"] = {"origin": service_url(5133)}
        visible["attack"]["origin"] = service_url(5100)
        visible["fields"][0]["default"] = visible["attack"]["origin"]
    return visible


def access_urls(host, port=5100):
    if not ipaddress.ip_address(host).is_unspecified:
        authority = f"[{host}]" if ":" in host else host
        return [f"http://{authority}:{port}"]
    urls = [f"http://127.0.0.1:{port}"]
    try:
        addresses = sorted({entry[4][0] for entry in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
                            if allowed_address(entry[4][0], allow_lan=True) and not ipaddress.ip_address(entry[4][0]).is_loopback})
    except OSError:
        addresses = []
    return urls + [f"http://{address}:{port}" for address in addresses]
