import ipaddress
from labcore.exercises import save_state, state


def run(db, data, context):
    answer = str(ipaddress.IPv4Address(data.get("answer_ip", "")))
    # Respons harus cocok dengan query outstanding dan resolver yang dituju.
    if data.get("transaction_id") != "4201" or data.get("resolver") != "192.0.2.53":
        return dict(title="Respons DNS ditolak", detail="Transaction ID atau resolver tidak cocok. Cache tidak diubah.", status=403)
    old = state(db, "secure", "dns", "192.0.2.10")
    save_state(db, "secure", "dns", answer)
    return dict(title="Respons cocok dengan transaksi", detail="Pemeriksaan transaksi lulus; ini bukan verifikasi DNSSEC.",
                rows=[{"nama": "portal.lab.test", "sebelum": old, "sesudah": answer}])
