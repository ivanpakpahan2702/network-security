from pathlib import Path


def run(db, data, context):
    name = data.get("filename", "catatan.html")[:128]
    body = data.get("body", data.get("content", "").encode("utf-8"))
    if len(body) > 65536:
        raise ValueError("Ukuran file melampaui batas 64 KiB.")
    # RENTAN: HTML unggahan disajikan inline sebagai konten aktif.
    mime = "text/html" if Path(name).suffix.lower() in {".html", ".htm"} else "text/plain"
    inserted = db.execute("INSERT INTO uploads (mode, name, body, mime) VALUES (?, ?, ?, ?)",
                          ("vulnerable", name, body, mime))
    url = f"/uploads/vulnerable/{inserted.lastrowid}"
    return dict(title="Upload diterima tanpa pembatasan format", detail=f"File {name} disajikan sebagai {mime}.",
                preview=url if mime == "text/html" else None, link=url, link_label="Buka file hasil upload")
