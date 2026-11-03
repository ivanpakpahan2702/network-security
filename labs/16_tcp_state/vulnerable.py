from labcore.exercises import tokens


def run(db, data, context):
    segments = tokens(data.get("segments", ""), {"syn", "syn-ack", "ack", "data", "fin"})
    state, rows = "CLOSED", []
    for segment in segments:
        # Keliru: ACK apa pun dianggap cukup untuk menyatakan koneksi terbentuk.
        if segment == "ack":
            state = "ESTABLISHED"
        accepted = segment != "data" or state == "ESTABLISHED"
        rows.append({"segmen": segment.upper(), "state": state, "diterima": accepted})
    return dict(title="Penilaian tanpa urutan handshake", detail="ACK dipercaya tanpa membuktikan SYN dan SYN-ACK sebelumnya.", rows=rows)
