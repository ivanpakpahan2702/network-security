from labcore.exercises import integer, records
from labcore.analytics import classification


def run(db, data, context):
    threshold = integer(data, "threshold", 2, 20)
    events = records(db, "ids")
    detected, windows = set(), []
    for source in sorted({row["source"] for row in events}):
        selected = [row for row in events if row["source"] == source and row["syn"]]
        peak = max(len({item["port"] for item in selected if first["second"] <= item["second"] < first["second"] + 60}) for first in selected)
        if peak >= threshold:
            detected.add(source)
        windows.append(f"{source}: peak={peak} port unik / 60 detik")
    return dict(title="Evaluasi rule berjendela waktu", detail="Sumber diberi alert: " + (", ".join(sorted(detected)) or "tidak ada"),
                rows=[classification(events, detected)], trace="\n".join(windows) + "\nThreshold rendah tetap dapat memicu false positive; gunakan konteks dan tuning.")
