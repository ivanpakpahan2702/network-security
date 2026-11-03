from labcore.runtime import local_fetch


def run(db, data, context):
    url = data.get("url", "")[:2048]
    # RENTAN: pengguna dapat memilih path service internal tanpa otorisasi.
    status, body = local_fetch(url)
    return dict(title="Backend mengambil URL pilihan pengguna", detail="Respons HTTP service internal dummy:",
                trace=body, rows=[{"HTTP upstream": status, "URL": url}])
