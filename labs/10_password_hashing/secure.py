import time

from werkzeug.security import check_password_hash


def run(db, data, context):
    accounts = db.execute("SELECT username, password_hash FROM accounts WHERE username IN ('alice','bob') ORDER BY username").fetchall()
    target = accounts[0]["password_hash"]
    candidates = [line.strip() for line in data.get("candidates", "").splitlines() if line.strip()][:8]
    started = time.perf_counter()
    found = None
    attempts = 0
    for password in candidates:
        attempts += 1
        # DIPERBAIKI: hash scrypt dengan salt acak per akun dan cost tersimpan.
        # Dibuat saat seed: generate_password_hash(password, method='scrypt:32768:8:3').
        if check_password_hash(target, password[:256]):
            found = password[:256]
            break
    elapsed = (time.perf_counter() - started) * 1000
    return dict(title="Uji offline scrypt bersalt", detail=f"Kandidat ditemukan: {found or '(tidak ada)'}. {attempts} tebakan dalam {elapsed:.3f} ms. Password lemah tetap bisa ditebak.",
                rows=[dict(row) for row in accounts], trace="Digest alice == bob: " + str(accounts[0]["password_hash"] == accounts[1]["password_hash"]))
