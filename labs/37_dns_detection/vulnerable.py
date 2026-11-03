from labcore.exercises import records


def run(db, data, context):
    # Naif: semua label panjang dianggap tunneling, termasuk CDN sah.
    flagged = [row for row in records(db, "dns_log") if len(row["label"]) >= 24]
    return dict(title="Alert berdasarkan panjang label", detail=f"{len(flagged)} query ditandai; CDN fixture juga ikut terkena.", rows=flagged)
