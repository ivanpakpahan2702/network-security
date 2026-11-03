def run(db, data, context):
    source = data.get("source", "")
    if source not in {"workstation", "web", "admin"}:
        raise ValueError("Zona sumber tidak dikenal.")
    port = int(data.get("port", "0"))
    service = db.execute("SELECT * FROM services WHERE name=? AND port=?", (data.get("target", ""), port)).fetchone()
    if not service:
        return dict(title="Layanan tidak tersedia", detail="Tidak ada service virtual pada kombinasi host dan port ini.", status=404)
    # RENTAN: tidak ada segmentasi, rule allow-all menerima semua zona.
    return dict(title="Koneksi virtual DIIZINKAN", detail=f"{source} dapat menjangkau {service['name']}:{port}.",
                rows=[dict(service)], trace="Rule #1: source=ANY destination=ANY port=ANY action=ALLOW\nTidak ada paket jaringan nyata yang dikirim.")
