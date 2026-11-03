import ipaddress
from labcore.exercises import save_state


def run(db, data, context):
    lease = dict(gateway=str(ipaddress.IPv4Address(data.get("gateway", ""))), dns=str(ipaddress.IPv4Address(data.get("dns", ""))), server_port=data.get("server_port", ""))
    # RENTAN: offer pertama dipercaya tanpa melihat port sumber.
    save_state(db, "vulnerable", "lease", lease)
    return dict(title="Offer DHCP diterima", detail="Gateway dan DNS fixture telah diganti oleh offer tersebut.", rows=[lease])
