from labcore.exercises import records


def run(db, data, context):
    account = data.get("account")
    if account not in {"alice", "bob"}:
        raise ValueError("Akun fixture hanya alice atau bob.")
    # Naif: hanya melihat error autentikasi; aktivitas sukses/audit/proxy diabaikan.
    rows = [row for row in records(db, "log") if row["account"] == account and row["event"] == "login_failed"]
    return dict(title="Pencarian login gagal saja", detail=f"{len(rows)} kegagalan ditemukan; hasil ini belum menyusun rantai insiden.", rows=rows)
