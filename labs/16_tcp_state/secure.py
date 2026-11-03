from labcore.exercises import tokens


def run(db, data, context):
    segments = tokens(data.get("segments", ""), {"syn", "syn-ack", "ack", "data", "fin"})
    transitions = {("CLOSED", "syn"): "WAIT_SYN_ACK", ("WAIT_SYN_ACK", "syn-ack"): "WAIT_ACK",
                   ("WAIT_ACK", "ack"): "ESTABLISHED", ("ESTABLISHED", "data"): "ESTABLISHED", ("ESTABLISHED", "fin"): "CLOSED"}
    state, rows = "CLOSED", []
    for segment in segments:
        next_state = transitions.get((state, segment))
        rows.append({"sebelum": state, "segmen": segment.upper(), "sesudah": next_state or "DITOLAK"})
        if next_state is None:
            return dict(title="Urutan segmen tidak valid", detail="Model tidak menerima segmen ini pada state saat ini.", rows=rows, status=400)
        state = next_state
    return dict(title="Urutan segmen valid", detail=f"State akhir model: {state}. Nama WAIT_* adalah state pengamatan lab, bukan daftar lengkap state TCP RFC.", rows=rows)
