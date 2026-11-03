import secrets


def run(db, data, context):
    if not context.get("authenticated"):
        return dict(title="Sesi bank diperlukan", detail="Buka Bank diperbaiki terlebih dahulu.", status=401)
    # DIPERBAIKI: token acak terikat sesi dan Origin harus valid sebelum mutasi.
    expected = context.get("expected_token", "")
    supplied = data.get("csrf_token", "")
    if not expected or not secrets.compare_digest(expected.encode(), supplied.encode()):
        return dict(title="CSRF ditolak", detail="Token anti-CSRF hilang atau tidak cocok.", status=403)
    if context.get("origin") != context.get("expected_origin"):
        return dict(title="Origin ditolak", detail="Transfer harus berasal dari origin bank yang sama.", status=403)
    amount = int(data.get("amount", "0"))
    if not 1 <= amount <= 1000:
        raise ValueError("Jumlah harus antara 1 dan 1000.")
    updated = db.execute("UPDATE wallets SET balance=balance-? WHERE mode='secure' AND balance>=?", (amount, amount))
    if not updated.rowcount:
        return dict(title="Transfer ditolak", detail="Saldo dummy tidak cukup.", status=400)
    return dict(title="Transfer sah berhasil", detail=f"{amount} unit dummy ditransfer dengan token dan Origin valid.")
