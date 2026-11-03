"""Primitive pembelajaran yang terbatas: HTTP offline, JWT dummy, dan PCAP sintetis."""
import base64
import hashlib
import hmac
import ipaddress
import json
import struct
import time

DEMO_KEY = b"lab-only-signing-key-do-not-use-in-production"
PACKAGES = {"original": b"demo-package version=1\noperation=show-help\n",
            "tampered": b"demo-package version=1\noperation=altered-dummy\n"}


def package_digest(name):
    if name not in PACKAGES:
        raise ValueError("Pilih artefak original atau tampered.")
    return hashlib.sha256(PACKAGES[name]).hexdigest()


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def decode64(value):
    try:
        return base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
    except (ValueError, UnicodeError) as error:
        raise ValueError("Base64url tidak valid.") from error


def demo_token(forged=False):
    header = {"alg": "none" if forged else "HS256", "typ": "JWT"}
    claims = {"sub": "alice", "role": "admin" if forged else "user", "iss": "security-lab", "aud": "lab-api", "exp": 4102444800}
    unsigned = ".".join(b64url(json.dumps(item, separators=(",", ":")).encode()) for item in (header, claims))
    return unsigned + "." + ("" if forged else b64url(hmac.digest(DEMO_KEY, unsigned.encode(), "sha256")))


def decode_token(token):
    if len(token) > 4096 or token.count(".") != 2:
        raise ValueError("Token harus memiliki tiga segmen dan maksimal 4096 karakter.")
    head, body, signature = token.split(".")
    try:
        header, claims = json.loads(decode64(head)), json.loads(decode64(body))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ValueError("JSON token tidak valid.") from error
    if not isinstance(header, dict) or not isinstance(claims, dict):
        raise ValueError("Header dan claims harus objek JSON.")
    return header, claims, (head + "." + body).encode(), signature


def verify_token(token):
    header, claims, unsigned, signature = decode_token(token)
    if header.get("alg") != "HS256":
        raise ValueError("Algoritma ditolak; server hanya menerima HS256.")
    if not hmac.compare_digest(hmac.digest(DEMO_KEY, unsigned, "sha256"), decode64(signature)):
        raise ValueError("Signature JWT tidak valid.")
    expiry = claims.get("exp")
    if type(expiry) not in (int, float) or not time.time() < expiry <= 4102444800:
        raise ValueError("Token kedaluwarsa atau exp tidak valid.")
    if claims.get("iss") != "security-lab" or claims.get("aud") != "lab-api":
        raise ValueError("Issuer atau audience tidak cocok.")
    if claims.get("sub") != "alice" or not isinstance(claims.get("role"), str) or claims["role"] not in {"user", "admin"}:
        raise ValueError("Identitas atau role token tidak dikenal.")
    return claims


def parse_http(raw):
    if len(raw) > 8192:
        raise ValueError("Request offline maksimal 8192 karakter.")
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    head, separator, body = raw.partition("\n\n")
    lines = head.split("\n")
    parts = lines[0].split()
    if len(parts) != 3 or not parts[2].startswith("HTTP/"):
        raise ValueError("Baris awal harus METHOD /path HTTP/1.1.")
    headers = []
    for line in lines[1:]:
        name, colon, value = line.partition(":")
        if not colon or not name or any(char.isspace() for char in name):
            raise ValueError("Header tidak valid.")
        headers.append((name.lower(), value.strip()))
    return dict(method=parts[0], path=parts[1], version=parts[2], headers=headers,
                body=body if separator else "")


def smuggling_sample():
    body = "0\r\n\r\nGET /admin-demo HTTP/1.1\r\nHost: lab.test\r\n\r\n"
    return f"POST / HTTP/1.1\r\nHost: lab.test\r\nContent-Length: {len(body.encode())}\r\nTransfer-Encoding: chunked\r\n\r\n{body}"


def framing(raw):
    # Normalisasi line ending textarea kembali menjadi CRLF sebelum menghitung BYTE.
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
    parsed = parse_http(normalized)
    _, separator, body = normalized.partition("\r\n\r\n")
    body = body.encode("utf-8") if separator else b""
    lengths = [value for name, value in parsed["headers"] if name == "content-length"]
    encodings = [value.lower() for name, value in parsed["headers"] if name == "transfer-encoding"]
    cl_end = int(lengths[0]) if lengths else 0
    if cl_end < 0 or cl_end > len(body):
        raise ValueError("Content-Length di luar ukuran body yang tersedia.")
    te_end = None
    if encodings:
        if encodings != ["chunked"]:
            raise ValueError("Parser lab hanya mendukung satu Transfer-Encoding: chunked.")
        cursor = 0
        for _ in range(64):
            line_end = body.find(b"\r\n", cursor)
            if line_end < 0:
                raise ValueError("Ukuran chunk tidak lengkap.")
            try:
                size = int(body[cursor:line_end], 16)
            except ValueError as error:
                raise ValueError("Ukuran chunk bukan hex.") from error
            if size < 0 or size > 8192:
                raise ValueError("Ukuran chunk tidak didukung.")
            cursor = line_end + 2
            if body[cursor + size:cursor + size + 2] != b"\r\n":
                raise ValueError("Chunk tidak lengkap; trailer tidak didukung dalam lab ini.")
            cursor += size + 2
            if size == 0:
                te_end = cursor
                break
        if te_end is None:
            raise ValueError("Terlalu banyak chunk.")
    return parsed, body, lengths, encodings, cl_end, te_end


def checksum(data):
    if len(data) % 2:
        data += b"\0"
    value = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while value >> 16:
        value = (value & 0xffff) + (value >> 16)
    return (~value) & 0xffff


def tcp_frame(source, destination, sport, dport, flags, sequence=100, ack=0):
    src, dst = ipaddress.IPv4Address(source).packed, ipaddress.IPv4Address(destination).packed
    tcp = struct.pack("!HHIIBBHHH", sport, dport, sequence, ack, 5 << 4, flags, 64240, 0, 0)
    pseudo = src + dst + struct.pack("!BBH", 0, 6, len(tcp))
    tcp = tcp[:16] + struct.pack("!H", checksum(pseudo + tcp)) + tcp[18:]
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 40, 1, 0x4000, 64, 6, 0, src, dst)
    ip = ip[:10] + struct.pack("!H", checksum(ip)) + ip[12:]
    ethernet = bytes.fromhex("0200000000020200000000010800")
    return ethernet + ip + tcp


def capture_bytes(name):
    src, dst = "192.0.2.10", "192.0.2.20"
    if name == "normal":
        frames = [tcp_frame(src, dst, 49152, 443, 2), tcp_frame(dst, src, 443, 49152, 18, 200, 101),
                  tcp_frame(src, dst, 49152, 443, 16, 101, 201)]
    elif name == "scan":
        frames = [tcp_frame(src, dst, 49152 + i, port, 2) for i, port in enumerate((22, 23, 80, 443, 445, 3389))]
    elif name == "incomplete":
        frames = [tcp_frame(src, dst, 49152, 443, 2)]
    else:
        raise ValueError("Capture harus normal, scan, atau incomplete.")
    result = struct.pack("<IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    for i, frame in enumerate(frames):
        result += struct.pack("<IIII", 1761955200 + i, 0, len(frame), len(frame)) + frame
    return result


def read_pcap(data):
    if len(data) < 24 or data[:4] != b"\xd4\xc3\xb2\xa1" or len(data) > 65536:
        raise ValueError("PCAP lab tidak valid.")
    if struct.unpack_from("<I", data, 20)[0] != 1:
        raise ValueError("Hanya Ethernet PCAP didukung.")
    rows, cursor = [], 24
    while cursor < len(data):
        if len(rows) >= 100 or cursor + 16 > len(data):
            raise ValueError("PCAP terpotong atau melebihi 100 paket.")
        timestamp, micros, length, original = struct.unpack_from("<IIII", data, cursor)
        cursor += 16
        frame = data[cursor:cursor + length]
        cursor += length
        if len(frame) != length or length < 54 or frame[12:14] != b"\x08\x00" or frame[23] != 6:
            raise ValueError("Parser lab hanya mendukung frame IPv4/TCP lengkap.")
        ihl = (frame[14] & 0xf) * 4
        offset = 14 + ihl
        if ihl < 20 or offset + 20 > len(frame):
            raise ValueError("Header IPv4/TCP terpotong.")
        sport, dport = struct.unpack_from("!HH", frame, offset)
        flags = frame[offset + 13]
        label = "SYN-ACK" if flags & 0x12 == 0x12 else "SYN" if flags & 2 else "ACK" if flags & 16 else str(flags)
        rows.append(dict(packet=len(rows) + 1, epoch=timestamp + micros / 1e6,
                         source=str(ipaddress.IPv4Address(frame[26:30])), destination=str(ipaddress.IPv4Address(frame[30:34])),
                         source_port=sport, destination_port=dport, flags=label))
    return rows
