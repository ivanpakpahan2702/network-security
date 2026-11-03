from labcore.protocols import parse_http


def run(db, data, context):
    parsed = parse_http(data.get("raw_request", ""))
    # Keliru untuk logging: seluruh header dan body disalin.
    return dict(title="Struktur HTTP dan log mentah", detail="Perhatikan kredensial dummy yang ikut masuk contoh log.",
                rows=[{"bagian": key, "nilai": parsed[key]} for key in ("method", "path", "version")],
                trace="\n".join(f"{name}: {value}" for name, value in parsed["headers"]) + "\n\n" + parsed["body"])
