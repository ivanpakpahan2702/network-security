from labcore.runtime import local_fetch
from flask import current_app

def run(db, data, context):
    # DIPERBAIKI: pilih endpoint dari allowlist eksak, lalu fetch konstanta server.
    endpoint = f"http://127.0.0.1:{current_app.config.get('SSRF_PORT', 5199)}/public/status"
    if data.get("url", "") != endpoint:
        raise ValueError("URL ditolak: hanya endpoint publik yang terdaftar boleh diambil.")
    status, body = local_fetch(endpoint)
    return dict(title="Endpoint publik terverifikasi", detail="Path internal tidak tersedia melalui fitur fetch ini.",
                trace=body, rows=[{"HTTP upstream": status, "URL": endpoint}])
