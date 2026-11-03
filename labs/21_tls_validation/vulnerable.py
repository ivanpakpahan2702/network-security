def run(db, data, context):
    if data.get("certificate") not in {"valid", "wrong-host", "expired", "untrusted"}:
        raise ValueError("Fixture sertifikat tidak dikenal.")
    # RENTAN: model verify=False menerima sertifikat tanpa verifikasi identitas.
    return dict(title="Sertifikat diterima tanpa verifikasi", detail="Transport diasumsikan terenkripsi, tetapi identitas server belum terbukti.",
                rows=[{"tujuan": data.get("hostname", ""), "sertifikat": data["certificate"], "hostname/chain/expiry": "diabaikan"}])
