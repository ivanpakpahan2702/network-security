import time

from werkzeug.security import check_password_hash
from labcore.dbqueries import begin_write


def run(db, data, context):
    candidates = [line.strip() for line in data.get("candidates", "").splitlines() if line.strip()][:8]
    account = db.execute("SELECT password_hash FROM accounts WHERE username='alice'").fetchone()
    results = []
    # SQLite: BEGIN IMMEDIATE; MySQL: transaksi dengan row lock untuk limiter login.
    begin_write(db, lock="login")
    for password in candidates:
        now = time.time()
        failures = db.execute("SELECT COUNT(*) FROM attempts WHERE mode='secure' AND username='alice' AND success=0 AND occurred>?",
                              (now - 60,)).fetchone()[0]
        # DIPERBAIKI: rate limit disimpan di database, bukan di input pengguna.
        if failures >= 3:
            return dict(title="Percobaan dibatasi", detail="HTTP 429: tiga kegagalan dalam 60 detik. Tunggu atau reset lab.", rows=results, status=429)
        valid = check_password_hash(account["password_hash"], password[:256])
        db.execute("INSERT INTO attempts (mode, username, occurred, success) VALUES (?, ?, ?, ?)",
                   ("secure", "alice", now, int(valid)))
        results.append({"percobaan": len(results) + 1, "kandidat dummy": password[:256], "hasil": "berhasil" if valid else "gagal"})
        if valid:
            return dict(title="Login sah berhasil", detail="Password benar dan batas percobaan belum terlampaui.", rows=results)
    return dict(title="Login ditolak", detail="Kredensial tidak cocok; percobaan gagal dicatat.", rows=results, status=401)
