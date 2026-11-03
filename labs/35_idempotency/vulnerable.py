from labcore.exercises import integer


def run(db, data, context):
    amount = integer(data, "amount", 1, 100)
    repeats = integer(data, "repeats", 1, 5)
    key = data.get("request_id", "")[:64]
    if not key:
        raise ValueError("Request ID diperlukan.")
    for _ in range(repeats):
        # RENTAN: setiap pengiriman dianggap sebagai transaksi baru.
        db.execute("INSERT INTO payments (mode,request_id,amount) VALUES ('vulnerable',?,?)", (key, amount))
    row = db.execute("SELECT COUNT(*) AS pembayaran,SUM(amount) AS total FROM payments WHERE mode='vulnerable' AND request_id=?", (key,)).fetchone()
    return dict(title="Retry dibukukan berulang", detail="Jumlah dan nominal kumulatif untuk request ID ini:", rows=[dict(row)])
