import ipaddress
from labcore.exercises import integer, records


def run(db, data, context):
    ip = str(ipaddress.IPv4Address(data.get("source_ip", "")))
    source_port = integer(data, "source_port", 1, 65535)
    destination_port = integer(data, "destination_port", 1, 65535)
    mapping = next((row for row in records(db, "conntrack") if row["state"] == "ESTABLISHED"
                    and (row["source_ip"], row["source_port"], row["destination_port"]) == (ip, source_port, destination_port)), None)
    return dict(title="Paket balasan cocok dengan state" if mapping else "Paket masuk tidak diminta",
                detail="Model mencocokkan reverse tuple; NAT saja tidak digunakan sebagai bukti izin.",
                rows=[mapping] if mapping else [], status=200 if mapping else 403)
