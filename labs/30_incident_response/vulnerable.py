from labcore.exercises import save_state, tokens


def run(db, data, context):
    actions = tokens(data.get("actions", ""), {"isolate", "preserve", "rotate", "recover", "validate", "wipe"})
    # Naif: menjalankan tindakan tanpa mengecek prasyarat dan preservasi bukti.
    evidence = "hilang pada model" if "wipe" in actions and ("preserve" not in actions or actions.index("wipe") < actions.index("preserve")) else "tersedia"
    save_state(db, "vulnerable", "incident", {"actions": actions, "evidence": evidence})
    return dict(title="Tindakan diterapkan tanpa pemeriksaan", detail=f"Status bukti: {evidence}. Recovery yang dipanggil belum berarti insiden selesai.",
                rows=[{"urutan": index + 1, "tindakan virtual": action} for index, action in enumerate(actions)])
