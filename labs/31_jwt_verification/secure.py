from labcore.protocols import verify_token


def run(db, data, context):
    # Verifikasi HS256 + signature + expiry + issuer + audience sebelum memakai role.
    claims = verify_token(data.get("token", ""))
    return dict(title="Token dan claims terverifikasi", detail=f"Identitas: {claims['sub']}; role: {claims['role']}.",
                rows=[{"sub": claims["sub"], "role": claims["role"], "verified": True}],
                trace="Implementasi kriptografi pembelajaran: labcore/protocols.py. Produksi menggunakan library JWT terawat.")
