from labcore.protocols import framing


def run(db, data, context):
    parsed, body, lengths, encodings, cl_end, te_end = framing(data.get("raw_request", ""))
    # RENTAN: frontend memilih CL, backend memilih TE tanpa menolak konflik.
    backend_end = te_end if te_end is not None else cl_end
    return dict(title="Dua parser menentukan batas pesan", detail=f"Batas frontend={cl_end} byte; backend={backend_end} byte. Berbeda: {cl_end != backend_end}.",
                rows=[{"parser": "frontend CL", "akhir body": cl_end}, {"parser": "backend TE/CL", "akhir body": backend_end}],
                trace="Sisa byte menurut backend:\n" + body[backend_end:].decode("utf-8", errors="replace"))
