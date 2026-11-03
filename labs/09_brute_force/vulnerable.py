import time

from werkzeug.security import check_password_hash


def run(db, data, context):
    candidates = [line.strip() for line in data.get("candidates", "").splitlines() if line.strip()][:8]
    account = db.execute("SELECT password_hash FROM accounts WHERE username='alice'").fetchone()
    results = []
    for password in candidates:
        # RENTAN: tidak ada pembatasan jumlah kegagalan login.
        valid = check_password_hash(account["password_hash"], password[:256])
        db.execute("INSERT INTO attempts (mode, username, occurred, success) VALUES (?, ?, ?, ?)",
                   ("vulnerable", "alice", time.time(), int(valid)))
        results.append({"percobaan": len(results) + 1, "kandidat dummy": password[:256], "hasil": "berhasil" if valid else "gagal"})
        if valid:
            return dict(title="Password ditemukan", detail="Tidak ada throttle: semua kandidat dapat diuji.", rows=results)
    return dict(title="Belum ditemukan", detail="Daftar habis. Mode ini tetap menerima percobaan berikutnya.", rows=results, status=401)
