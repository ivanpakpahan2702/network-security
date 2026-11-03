from werkzeug.security import check_password_hash
from labcore.dbqueries import query_display


def run(db, data, context):
    # DIPERBAIKI: input hanya menjadi data parameter, bukan sintaks SQL.
    query = "SELECT id, username, password_hash FROM accounts WHERE username = ?"
    row = db.execute(query, (data.get("username", "")[:256],)).fetchone()
    valid = row is not None and check_password_hash(row["password_hash"], data.get("password", "")[:256])
    return dict(title="Login berhasil" if valid else "Login ditolak",
                detail=f"Anda masuk sebagai {row['username']}." if valid else "Kredensial tidak cocok.",
                trace=query_display(db, query) + "\nParameter dikirim terpisah; password diverifikasi terhadap scrypt.",
                status=200 if valid else 401)
