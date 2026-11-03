from labcore.protocols import parse_http


def run(db, data, context):
    parsed = parse_http(data.get("raw_request", ""))
    # Allowlist metadata; query dan body sengaja tidak dimasukkan contoh log.
    safe_headers = [(name, value if name in {"host", "content-type", "content-length"} else "[REDACTED]")
                    for name, value in parsed["headers"]]
    path = parsed["path"].split("?", 1)[0]
    return dict(title="Struktur HTTP dan log terpilih", detail="Method/path tetap berguna untuk observasi; header lain dan body tidak disalin mentah.",
                rows=[{"method": parsed["method"], "path tanpa query": path, "version": parsed["version"], "ukuran body": len(parsed["body"].encode())}],
                trace="\n".join(f"{name}: {value}" for name, value in safe_headers) + "\n\n[BODY OMITTED]")
