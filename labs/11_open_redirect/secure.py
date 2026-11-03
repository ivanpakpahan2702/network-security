from urllib.parse import urlencode


def destination(value, allowed_target=None):
    # DIPERBAIKI: allowlist path lokal eksak; //host dan URL absolut ditolak.
    if value not in {"/welcome"}:
        raise ValueError("Redirect ditolak: tujuan bukan path internal yang terdaftar.")
    return value


def run(db, data, context):
    target = destination(data.get("next", "/welcome"))
    return dict(title="Redirect lokal diterima", detail="Hanya tujuan internal /welcome tersedia.",
                trace="HTTP/1.1 302 Found\nLocation: " + target,
                link="/redirect/secure?" + urlencode({"next": target}))
