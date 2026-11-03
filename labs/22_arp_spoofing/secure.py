import ipaddress
from labcore.exercises import records, save_state, validate_mac


def run(db, data, context):
    packet = dict(ip=str(ipaddress.IPv4Address(data.get("ip", ""))), mac=validate_mac(data.get("mac", "")), switch_port=data.get("switch_port", ""))
    # Model DAI: binding diperoleh dari konfigurasi tepercaya, bukan paket pengirim.
    if packet not in records(db, "arp_binding"):
        return dict(title="ARP binding ditolak", detail="Kombinasi IP/MAC/port tidak cocok dengan binding gateway.", status=403)
    save_state(db, "secure", packet["ip"], packet["mac"])
    return dict(title="ARP binding terverifikasi", detail="Mapping diterima dari port yang dipercaya.", rows=[packet])
