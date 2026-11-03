import base64
import hashlib


def run(db, data, context):
    message = data.get("received", "")[:2048].encode()
    encoded = base64.b64encode(message).decode()
    # Keliru: encoding dapat didekode ulang, tetapi tidak membuktikan asal/integritas.
    accepted = base64.b64decode(encoded) == message
    return dict(title="Encoding diterima tanpa autentikasi pesan", detail=f"Dapat didekode: {accepted}. Ini tidak mendeteksi perubahan dari pesan asli.",
                rows=[{"Base64": encoded, "SHA-256 tanpa key": hashlib.sha256(message).hexdigest()}])
