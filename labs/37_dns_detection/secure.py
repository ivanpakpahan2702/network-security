from collections import defaultdict
from labcore.analytics import entropy
from labcore.exercises import integer, records


def run(db, data, context):
    threshold = float(data.get("entropy", "0"))
    minimum = integer(data, "minimum", 2, 10)
    if not 1 <= threshold <= 5:
        raise ValueError("Entropy harus antara 1.0 dan 5.0.")
    grouped = defaultdict(list)
    for row in records(db, "dns_log"):
        grouped[row["domain"]].append(row)
    rows = []
    for domain, queries in sorted(grouped.items()):
        unique = {item["label"] for item in queries if len(item["label"]) >= 24 and entropy(item["label"]) >= threshold}
        approved = all(item["approved"] for item in queries)
        alert = not approved and len(unique) >= minimum
        rows.append({"domain": domain, "label unik memenuhi entropy": len(unique), "disetujui": approved, "alert": alert})
    return dict(title="Korelasi DNS selesai", detail="Alert perlu ditindaklanjuti; label panjang atau entropy tinggi saja bukan bukti kebocoran data.", rows=rows)
