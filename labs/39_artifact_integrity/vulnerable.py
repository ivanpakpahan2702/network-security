import hmac
from labcore.protocols import package_digest


def run(db, data, context):
    actual = package_digest(data.get("artifact", ""))
    claimed = data.get("claimed_hash", "").lower()
    # RENTAN: file dan checksum pembanding sama-sama dikendalikan pemasok tak tepercaya.
    valid = hmac.compare_digest(actual.encode(), claimed.encode())
    return dict(title="Checksum pemasok cocok" if valid else "Checksum tidak cocok",
                detail="Kecocokan ini belum membuktikan keaslian jika nilai pembanding juga diganti.", rows=[{"SHA-256 aktual": actual, "diterima": valid}], status=200 if valid else 403)
