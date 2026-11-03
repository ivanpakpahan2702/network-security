ALLOWED_FLOWS = {("workstation", "web", 443), ("web", "database", 5432), ("admin", "admin", 22)}


def run(db, data, context):
    source = data.get("source", "")
    target = data.get("target", "")
    port = int(data.get("port", "0"))
    if source not in {"workstation", "web", "admin"}:
        raise ValueError("Zona sumber tidak dikenal.")
    service = db.execute("SELECT * FROM services WHERE name=? AND port=?", (target, port)).fetchone()
    if not service:
        return dict(title="Layanan tidak tersedia", detail="Tidak ada service virtual pada kombinasi host dan port ini.", status=404)
    # DIPERBAIKI: allowlist flow yang diperlukan; sisanya default-deny.
    allowed = (source, target, port) in ALLOWED_FLOWS
    return dict(title="Koneksi virtual DIIZINKAN" if allowed else "Koneksi virtual DITOLAK",
                detail=f"{source} → {target}:{port}: {'ALLOW' if allowed else 'DENY'}.",
                rows=[dict(service)] if allowed else [], status=200 if allowed else 403,
                trace="Rule diizinkan: workstation→web:443; web→database:5432; admin→admin:22\nSelain itu: DENY. Tidak mengubah firewall OS.")
