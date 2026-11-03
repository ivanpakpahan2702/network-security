from labcore.exercises import tokens


def run(db, data, context):
    controls = set(tokens(data.get("controls", ""), {"tls", "authn", "object_authz", "segmentation", "secrets", "logging", "backup"}))
    paths = [("Penyadap → trafik web", {"tls"}), ("Anonim → API privat", {"authn"}),
             ("Akun terkompromi → invoice bob", {"object_authz"}),
             ("Web terkompromi → DB management", {"segmentation"}), ("Artefak bocor → secret aplikasi", {"secrets"})]
    rows = []
    for path, prevention in paths:
        blocked = bool(controls & prevention)
        # Backup membantu recovery; ia tidak mengurangi dampak kebocoran pada jalur ini.
        likelihood, impact = (1 if blocked else 4), 5
        rows.append({"jalur": path, "kontrol pencegahan": ", ".join(sorted(prevention)), "terputus dalam model": blocked,
                     "skor residual L×I": likelihood * impact})
    return dict(title="Trust boundary dan residual risk", detail=f"{sum(not row['terputus dalam model'] for row in rows)} jalur belum diputus. Logging={'ada' if 'logging' in controls else 'belum ada'}; backup={'ada' if 'backup' in controls else 'belum ada'}.",
                rows=rows, trace="Skor ini rubric pembelajaran, bukan CVSS. Backup membantu recovery, bukan menghapus dampak kebocoran. Kontrol perlu diverifikasi implementasinya; keberadaan nama kontrol tidak cukup di sistem nyata.")
