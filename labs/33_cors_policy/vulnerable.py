def cors_headers(origin, trusted_origin):
    # RENTAN: Origin apa pun direfleksikan dan cookie diizinkan.
    return {"Access-Control-Allow-Origin": origin, "Access-Control-Allow-Credentials": "true", "Vary": "Origin"} if origin else {}


def run(db, data, context):
    headers = cors_headers(data.get("origin", ""), context["trusted_origin"])
    return dict(title="Origin direfleksikan", detail="Header ini juga dipakai endpoint API demo nyata. Buat sesi korban lalu uji halaman pembaca lintas origin.",
                rows=[{"header": name, "nilai": value} for name, value in headers.items()], link="/account", link_label="Buka akun korban")
