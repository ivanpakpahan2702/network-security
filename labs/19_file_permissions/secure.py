def run(db, data, context):
    classes = {"owner": 0, "group": 1, "other": 2}
    operations = {"read": 4, "write": 2, "execute": 1}
    identity, operation = data.get("identity"), data.get("operation")
    if identity not in classes or operation not in operations:
        raise ValueError("Kelas identitas atau operasi tidak dikenal.")
    mode = "640"  # Profil perbaikan untuk file konfigurasi rahasia contoh.
    allowed = bool(int(mode[classes[identity]]) & operations[operation])
    return dict(title="Evaluasi profil least privilege 640", detail=f"{identity} melakukan {operation}: {'ALLOW' if allowed else 'DENY'}.",
                rows=[{"mode awal": data.get("mode", ""), "profil perbaikan": mode, "hasil": "ALLOW" if allowed else "DENY"}],
                trace="Owner read+write; group read; other tidak mendapat akses. Profil ini bukan aturan universal semua file.")
