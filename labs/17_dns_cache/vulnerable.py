import ipaddress
from labcore.exercises import save_state, state


def run(db, data, context):
    answer = str(ipaddress.IPv4Address(data.get("answer_ip", "")))
    old = state(db, "vulnerable", "dns", "192.0.2.10")
    # RENTAN: tidak mencocokkan transaksi atau sumber respons.
    save_state(db, "vulnerable", "dns", answer)
    return dict(title="Cache DNS diperbarui", detail="Jawaban diterima tanpa pemeriksaan respons.",
                rows=[{"nama": "portal.lab.test", "sebelum": old, "sesudah": answer}])
