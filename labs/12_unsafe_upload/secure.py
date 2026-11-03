import uuid
from pathlib import Path


def run(db, data, context):
    body = data.get("body", data.get("content", "").encode("utf-8"))
    if len(body) > 65536:
        raise ValueError("Ukuran file melampaui batas 64 KiB.")
    if Path(data.get("filename", "")).suffix.lower() != ".txt":
        raise ValueError("Format ditolak: lab diperbaiki hanya menerima .txt UTF-8.")
    text = body.decode("utf-8")
    if any(ord(character) < 32 and character not in "\r\n\t" for character in text):
        raise ValueError("File mengandung byte kontrol, bukan dokumen teks yang didukung.")
    # DIPERBAIKI: nama acak, format terbatas, simpan sebagai data di luar webroot.
    name = uuid.uuid4().hex + ".txt"
    inserted = db.execute("INSERT INTO uploads (mode, name, body, mime) VALUES (?, ?, ?, ?)",
                          ("secure", name, body, "text/plain"))
    # Endpoint download mengirim Content-Disposition: attachment + nosniff.
    return dict(title="Upload teks diterima", detail=f"Nama internal: {name}. File diunduh, bukan dirender sebagai HTML.",
                link=f"/uploads/secure/{inserted.lastrowid}", link_label="Unduh teks sebagai attachment")
