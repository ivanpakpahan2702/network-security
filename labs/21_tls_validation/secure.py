from datetime import date


def run(db, data, context):
    fixtures = {"valid": ("bank.lab.test", "Lab CA", date(2027, 1, 1)),
                "wrong-host": ("other.lab.test", "Lab CA", date(2027, 1, 1)),
                "expired": ("bank.lab.test", "Lab CA", date(2025, 1, 1)),
                "untrusted": ("bank.lab.test", "Unknown CA", date(2027, 1, 1))}
    choice = data.get("certificate")
    if choice not in fixtures:
        raise ValueError("Fixture sertifikat tidak dikenal.")
    hostname, issuer, expiry = fixtures[choice]
    # Metadata saja: library TLS sungguhan juga memverifikasi signature dan chain.
    checks = {"hostname cocok": data.get("hostname") == hostname,
              "issuer dipercaya": issuer == "Lab CA", "belum kedaluwarsa": date(2026, 1, 15) < expiry}
    valid = all(checks.values())
    return dict(title="Metadata sertifikat valid" if valid else "Sertifikat dummy ditolak",
                detail="Tanggal evaluasi fixture: 2026-01-15. Tidak ada handshake TLS nyata.",
                rows=[{"pemeriksaan": key, "lulus": value} for key, value in checks.items()], status=200 if valid else 403)
