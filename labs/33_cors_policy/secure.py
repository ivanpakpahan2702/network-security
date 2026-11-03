def cors_headers(origin, trusted_origin):
    # DIPERBAIKI: Origin harus sama persis dengan origin yang dipercaya server.
    if origin == trusted_origin:
        return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true", "Vary": "Origin"}
    return {"Vary": "Origin"}


def run(db, data, context):
    headers = cors_headers(data.get("origin", ""), context["trusted_origin"])
    allowed = "Access-Control-Allow-Origin" in headers
    return dict(title="Origin diizinkan" if allowed else "Origin tidak masuk allowlist", detail="CORS hanya mengatur apakah browser boleh membaca respons; sesi API tetap harus valid.",
                rows=[{"header": name, "nilai": value} for name, value in headers.items()], status=200 if allowed else 403,
                link="/account", link_label="Buka akun korban")
