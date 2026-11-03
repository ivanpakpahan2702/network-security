from labcore.protocols import framing


def run(db, data, context):
    parsed, body, lengths, encodings, cl_end, te_end = framing(data.get("raw_request", ""))
    # Kebijakan ketat lab: tolak framing ambigu sebelum pesan diteruskan.
    if (lengths and encodings) or len(lengths) > 1 or len(encodings) > 1:
        return dict(title="Framing ambigu ditolak", detail="Kombinasi TE+CL atau header panjang ganda tidak diterima.", status=400)
    end = te_end if te_end is not None else cl_end
    if end != len(body):
        return dict(title="Byte sisa ditolak", detail="Lab hanya menerima satu pesan lengkap, tanpa pipelining atau byte tambahan.", status=400)
    return dict(title="Satu batas pesan terverifikasi", detail=f"Panjang body: {end} byte. Tidak ada request yang dikirim ke jaringan.",
                rows=[{"method": parsed["method"], "path": parsed["path"], "body bytes": end}])
