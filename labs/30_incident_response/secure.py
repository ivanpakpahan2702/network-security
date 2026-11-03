import hashlib
from labcore.exercises import evidence_bytes, save_state, tokens


def run(db, data, context):
    actions = tokens(data.get("actions", ""), {"isolate", "preserve", "rotate", "recover", "validate", "wipe"})
    required = ["isolate", "preserve", "rotate", "recover", "validate"]
    rows = []
    for index, action in enumerate(actions):
        expected = required[index] if index < len(required) else "selesai"
        rows.append({"langkah": index + 1, "tindakan": action, "diharapkan": expected, "valid": action == expected})
        if action != expected:
            return dict(title="Urutan respons ditolak", detail=f"Pada skenario exfiltration aktif ini, langkah berikutnya adalah {expected}.", rows=rows, status=400)
    digest = hashlib.sha256(evidence_bytes(db)).hexdigest()
    save_state(db, "secure", "incident", {"actions": actions, "evidence_sha256": digest})
    finished = actions == required
    return dict(title="Respons dan validasi lengkap" if finished else "Respons masih berlangsung",
                detail="Semua tindakan hanya state virtual. Langkah tersisa: " + (", ".join(required[len(actions):]) or "tidak ada"),
                rows=rows, trace="SHA-256 paket bukti fixture: " + digest, grade=100 if finished else 20 * len(actions))
