from collections import Counter
from labcore.exercises import integer, records
from labcore.analytics import classification


def run(db, data, context):
    threshold = integer(data, "threshold", 2, 20)
    events = records(db, "ids")
    # Naif: menghitung semua event tanpa jendela waktu atau port unik.
    counts = Counter(row["source"] for row in events)
    detected = {source for source, count in counts.items() if count >= threshold}
    return dict(title="Evaluasi rule hitungan mentah", detail="Sumber diberi alert: " + (", ".join(sorted(detected)) or "tidak ada"),
                rows=[classification(events, detected)], trace="Label ground truth hanya dipakai menghitung metrik evaluasi.")
