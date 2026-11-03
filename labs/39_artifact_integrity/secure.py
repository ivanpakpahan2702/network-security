import hmac
from labcore.protocols import package_digest


def run(db, data, context):
    actual = package_digest(data.get("artifact", ""))
    # Pembanding berasal dari rilis dummy tepercaya yang dipin server, bukan request.
    trusted = package_digest("original")
    valid = hmac.compare_digest(actual, trusted)
    return dict(title="Artefak sesuai rilis tepercaya" if valid else "Artefak berubah / ditolak",
                detail="claimed_hash pengguna tidak digunakan sebagai akar kepercayaan.", rows=[{"SHA-256 aktual": actual, "SHA-256 tepercaya": trusted, "diterima": valid}], status=200 if valid else 403)
