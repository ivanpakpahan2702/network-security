import ipaddress
from labcore.exercises import save_state, state, validate_mac


def run(db, data, context):
    ip = str(ipaddress.IPv4Address(data.get("ip", "")))
    mac = validate_mac(data.get("mac", ""))
    old = state(db, "vulnerable", ip, "02:00:00:00:00:01")
    # RENTAN: mapping ditimpa tanpa verifikasi IP/MAC/port.
    save_state(db, "vulnerable", ip, mac)
    return dict(title="ARP cache ditimpa", detail="Frame berikutnya dalam model akan memakai MAC yang baru.",
                rows=[{"IP": ip, "MAC sebelum": old, "MAC sesudah": mac, "port": data.get("switch_port", "")}])
