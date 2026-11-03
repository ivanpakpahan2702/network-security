from labcore.exercises import integer, records


def run(db, data, context):
    port = integer(data, "destination_port", 1, 65535)
    mapping = next((row for row in records(db, "conntrack") if row["destination_port"] == port), None)
    # RENTAN: keberadaan mapping NAT disamakan dengan izin paket masuk.
    return dict(title="Mapping NAT ditemukan" if mapping else "Tidak ada mapping",
                detail="Sumber paket tidak dibandingkan dengan state koneksi.", rows=[mapping] if mapping else [], status=200 if mapping else 403)
