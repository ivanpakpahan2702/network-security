def run(db, data, context):
    invoice_id = int(data.get("invoice_id", "0"))
    # RENTAN: pengguna sesi tidak disertakan sebagai batas akses objek.
    row = db.execute("SELECT id, owner, body FROM invoices WHERE id=?", (invoice_id,)).fetchone()
    return dict(title="Invoice ditemukan" if row else "Invoice tidak ditemukan",
                detail="Pengguna sesi: alice. Mode ini tidak memeriksa pemilik invoice.",
                rows=[dict(row)] if row else [], status=200 if row else 404)
