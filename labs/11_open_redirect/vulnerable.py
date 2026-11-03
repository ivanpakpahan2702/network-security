from urllib.parse import urlencode, urlsplit


def destination(value, allowed_target="http://127.0.0.1:5100/phishing-demo"):
    # Batas lab: hanya path internal dan halaman penyerang dummy pada host lab.
    parsed = urlsplit(allowed_target)
    allowed_in_lab = {"/welcome", allowed_target, "//" + parsed.netloc + parsed.path}
    if value not in allowed_in_lab:
        raise ValueError("Batas lab: gunakan /welcome atau URL phishing-demo pada host lab yang sama.")
    # RENTAN: tujuan di luar origin aplikasi tetap diterima.
    return value


def run(db, data, context):
    target = destination(data.get("next", "/welcome"), context.get("redirect_target", "http://127.0.0.1:5100/phishing-demo"))
    return dict(title="Tujuan redirect diterima tanpa validasi origin", detail="Klik untuk melihat respons HTTP 302 nyata.",
                trace="HTTP/1.1 302 Found\nLocation: " + target,
                link="/redirect/vulnerable?" + urlencode({"next": target}))
