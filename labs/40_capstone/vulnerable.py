from labcore.exercises import json_object


def run(db, data, context):
    report = json_object(data.get("report", "{}"))
    # Review dangkal: keberadaan judul/identitas dianggap cukup, tanpa menilai bukti.
    present = bool(report.get("host") and report.get("entry"))
    return dict(title="Review kelengkapan permukaan", detail="Identitas dan dugaan awal ada; bukti, dampak, kontrol, serta rencana validasi belum dinilai." if present else "Identitas atau dugaan awal belum diisi.",
                rows=[{"host diisi": bool(report.get("host")), "entry diisi": bool(report.get("entry"))}],
                link="/artifacts/evidence.json", link_label="Unduh bukti kasus")
