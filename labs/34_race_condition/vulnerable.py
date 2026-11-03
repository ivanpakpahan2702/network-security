import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from labcore.database import connect
from labcore.exercises import integer


def run(db, data, context):
    amount = integer(data, "amount", 1, 100)
    wallet = uuid.uuid4().hex
    db.execute("INSERT INTO race_wallets VALUES (?,100)", (wallet,))
    db.commit()
    barrier = threading.Barrier(2, timeout=5)

    def withdraw(worker):
        with connect(context["database"]) as connection:
            balance = connection.execute("SELECT balance FROM race_wallets WHERE id=?", (wallet,)).fetchone()[0]
        barrier.wait()  # Kedua worker sudah melihat saldo awal yang sama.
        if balance >= amount:
            with connect(context["database"]) as connection:
                # RENTAN: pemeriksaan sebelumnya tidak atomik dengan mutasi ini.
                connection.execute("UPDATE race_wallets SET balance=balance-? WHERE id=?", (amount, wallet))
            return {"worker": worker, "saldo yang dibaca": balance, "penarikan": "diterima"}
        return {"worker": worker, "saldo yang dibaca": balance, "penarikan": "ditolak"}

    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(withdraw, (1, 2)))
    final = db.execute("SELECT balance FROM race_wallets WHERE id=?", (wallet,)).fetchone()[0]
    return dict(title="Check-then-act dijalankan bersamaan", detail=f"Saldo akhir: {final}. Dua worker membaca saldo sebelum update.", rows=rows)
