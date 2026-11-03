import hmac
from labcore.protocols import DEMO_KEY


def run(db, data, context):
    original = data.get("original", "")[:2048].encode()
    received = data.get("received", "")[:2048].encode()
    sender_mac = hmac.digest(DEMO_KEY, original, "sha256")
    expected_mac = hmac.digest(DEMO_KEY, received, "sha256")
    valid = hmac.compare_digest(sender_mac, expected_mac)
    return dict(title="Integritas pesan valid" if valid else "Perubahan pesan terdeteksi",
                detail="Kedua sisi fixture memiliki secret bersama; MAC dari pesan asli dibandingkan dengan pesan yang diterima.",
                rows=[{"MAC pengirim": sender_mac.hex(), "MAC penerima": expected_mac.hex(), "cocok": valid}], status=200 if valid else 403)
