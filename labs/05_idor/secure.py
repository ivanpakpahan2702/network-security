def run(db, data, context):
    invoice_id = int(data.get("invoice_id", "0"))
    # DIPERBAIKI: identitas berasal dari server, bukan parameter pengguna.
    row = db.execute("SELECT id, owner, body FROM invoices WHERE id=? AND owner=?",
                     (invoice_id, context["user"])).fetchone()
    return dict(title="Invoice ditemukan" if row else "Invoice tidak ditemukan",
                detail="Query selalu dibatasi ke pemilik alice dari konteks server.",
                rows=[dict(row)] if row else [], status=200 if row else 404)
