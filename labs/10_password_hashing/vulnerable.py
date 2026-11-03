import hashlib
import time


def run(db, data, context):
    accounts = db.execute("SELECT username, md5 FROM accounts WHERE username IN ('alice','bob') ORDER BY username").fetchall()
    target = accounts[0]["md5"]
    candidates = [line.strip() for line in data.get("candidates", "").splitlines() if line.strip()][:8]
    started = time.perf_counter()
    found = None
    attempts = 0
    for password in candidates:
        attempts += 1
        # RENTAN: MD5 cepat dan tidak memakai salt unik per akun.
        if hashlib.md5(password[:256].encode()).hexdigest() == target:
            found = password[:256]
            break
    elapsed = (time.perf_counter() - started) * 1000
    return dict(title="Uji offline MD5", detail=f"Kandidat ditemukan: {found or '(tidak ada)'}. {attempts} tebakan dalam {elapsed:.3f} ms.",
                rows=[dict(row) for row in accounts], trace="Digest alice == bob: " + str(accounts[0]["md5"] == accounts[1]["md5"]))
