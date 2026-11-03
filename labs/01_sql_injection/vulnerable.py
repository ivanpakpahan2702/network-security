from labcore.database import database_errors


def run(db, data, context):
    username = data.get("username", "")[:256]
    password = data.get("password", "")[:256]
    # RENTAN: input menjadi bagian dari sintaks SQL.
    query = f"SELECT id, username FROM accounts WHERE username = '{username}' AND password_demo = '{password}'"
    try:
        row = db.execute(query).fetchone()
    except database_errors() as error:
        return dict(title="Query SQL gagal", detail=str(error), trace=query, status=400)
    return dict(title="Login berhasil" if row else "Login ditolak",
                detail=f"Anda masuk sebagai {row['username']}." if row else "Kredensial tidak cocok.",
                trace=query, status=200 if row else 401)
