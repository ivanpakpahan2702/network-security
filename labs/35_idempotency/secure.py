from labcore.exercises import integer
from labcore.dbqueries import begin_write


def run(db, data, context):
    amount = integer(data, "amount", 1, 100)
    repeats = integer(data, "repeats", 1, 5)
    key = data.get("request_id", "")
    if not key or len(key) > 64:
        raise ValueError("Request ID wajib diisi dan maksimal 64 karakter.")
    # Mode ini memakai satu identitas server tetap (alice) dan satu operasi pembayaran.
    begin_write(db, lock="payments")
    rows = []
    for index in range(repeats):
        prior = db.execute("SELECT amount,payment_id FROM idempotency WHERE mode='secure' AND request_id=?", (key,)).fetchone()
        if prior:
            if prior["amount"] != amount:
                return dict(title="Key dipakai dengan parameter berbeda", detail="HTTP 409: buat key baru untuk transaksi berbeda.", status=409)
            payment_id, result = prior["payment_id"], "hasil tersimpan"
        else:
            payment_id = db.execute("INSERT INTO payments (mode,request_id,amount) VALUES ('secure',?,?)", (key, amount)).lastrowid
            db.execute("INSERT INTO idempotency VALUES ('secure',?,?,?)", (key, amount, payment_id))
            result = "pembayaran baru"
        rows.append({"pengiriman": index + 1, "payment_id": payment_id, "hasil": result})
    return dict(title="Satu pembayaran per idempotency key", detail="Pencatatan key dan pembayaran berada dalam transaksi database yang sama.", rows=rows)
