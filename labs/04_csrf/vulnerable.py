def run(db, data, context):
    if not context.get("authenticated"):
        return dict(title="Sesi bank diperlukan", detail="Buka Bank rentan terlebih dahulu untuk membuat sesi korban.", status=401)
    # RENTAN: cookie sesi dipercaya tanpa memeriksa token atau Origin.
    amount = int(data.get("amount", "0"))
    if not 1 <= amount <= 1000:
        raise ValueError("Jumlah harus antara 1 dan 1000.")
    updated = db.execute("UPDATE wallets SET balance=balance-? WHERE mode='vulnerable' AND balance>=?", (amount, amount))
    if not updated.rowcount:
        return dict(title="Transfer ditolak", detail="Saldo dummy tidak cukup.", status=400)
    return dict(title="Transfer berhasil tanpa token", detail=f"{amount} unit dummy ditransfer ke {data.get('recipient', 'demo')[:64]}.")
