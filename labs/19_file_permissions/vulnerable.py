def run(db, data, context):
    mode = data.get("mode", "")
    if len(mode) != 3 or any(char not in "01234567" for char in mode):
        raise ValueError("Mode harus tiga digit oktal, misalnya 640.")
    classes = {"owner": 0, "group": 1, "other": 2}
    operations = {"read": 4, "write": 2, "execute": 1}
    identity, operation = data.get("identity"), data.get("operation")
    if identity not in classes or operation not in operations:
        raise ValueError("Kelas identitas atau operasi tidak dikenal.")
    allowed = bool(int(mode[classes[identity]]) & operations[operation])
    return dict(title="Evaluasi mode yang diberikan", detail=f"{identity} melakukan {operation}: {'ALLOW' if allowed else 'DENY'}.",
                rows=[{"mode": mode, "owner bits": mode[0], "group bits": mode[1], "other bits": mode[2]}],
                trace="read=4, write=2, execute=1. Evaluasi hanya bit rwx, bukan keseluruhan model akses Linux.")
