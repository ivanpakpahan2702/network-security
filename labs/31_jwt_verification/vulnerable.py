from labcore.protocols import decode_token


def run(db, data, context):
    # RENTAN: hanya decode, lalu mempercayai claims yang disuplai klien.
    header, claims, unsigned, signature = decode_token(data.get("token", ""))
    return dict(title="Claims dipercaya tanpa signature", detail=f"Identitas: {claims.get('sub')}; role: {claims.get('role')}.",
                rows=[{"alg": header.get("alg"), "sub": claims.get("sub"), "role": claims.get("role"), "verified": False}])
