import uuid
from concurrent.futures import ThreadPoolExecutor
from labcore.database import connect
from labcore.exercises import integer
from labcore.dbqueries import begin_write


def run(db, data, context):
    amount = integer(data, "amount", 1, 100)
    wallet = uuid.uuid4().hex
    db.execute("INSERT INTO race_wallets VALUES (?,100)", (wallet,))
    db.commit()

    def withdraw(worker):
        with connect(context["database"]) as connection:
            begin_write(connection)
            # DIPERBAIKI: syarat saldo dan mutasi berada dalam operasi atomik.
            changed = connection.execute("UPDATE race_wallets SET balance=balance-? WHERE id=? AND balance>=?", (amount, wallet, amount)).rowcount
        return {"worker": worker, "penarikan": "diterima" if changed else "ditolak"}

    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(withdraw, (1, 2)))
    final = db.execute("SELECT balance FROM race_wallets WHERE id=?", (wallet,)).fetchone()[0]
    return dict(title="Transaksi atomik menjaga saldo", detail=f"Saldo akhir: {final}. Penarikan yang melebihi saldo ditolak.", rows=rows)
