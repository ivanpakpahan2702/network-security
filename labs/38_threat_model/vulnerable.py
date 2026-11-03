from labcore.exercises import tokens


def run(db, data, context):
    controls = tokens(data.get("controls", ""), {"tls", "authn", "object_authz", "segmentation", "secrets", "logging", "backup"})
    # Naif: hanya memeriksa TLS pada batas internet dan menganggap internal tepercaya.
    return dict(title="Review satu kontrol saja", detail="TLS ditemukan; sistem dianggap selesai direview." if "tls" in controls else "TLS belum ada.",
                rows=[{"jalur": "Internet → web", "kontrol": "TLS", "ada": "tls" in controls}],
                trace="Jalur akun yang sudah dikompromikan, akses objek, lateral movement, dan recovery belum dinilai.")
