import ipaddress
from labcore.exercises import save_state


def run(db, data, context):
    lease = dict(gateway=str(ipaddress.IPv4Address(data.get("gateway", ""))), dns=str(ipaddress.IPv4Address(data.get("dns", ""))), server_port=data.get("server_port", ""))
    # DHCP snooping memfilter offer berdasarkan trusted switch port.
    if lease["server_port"] != "uplink-1":
        return dict(title="Rogue DHCP offer ditolak", detail="Offer berasal dari port klien yang tidak dipercaya.", status=403)
    save_state(db, "secure", "lease", lease)
    return dict(title="Offer dari trusted port diterima", detail="Isi konfigurasi server DHCP tepercaya masih perlu diaudit secara terpisah.", rows=[lease])
