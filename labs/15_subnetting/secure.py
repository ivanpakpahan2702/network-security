import ipaddress


def run(db, data, context):
    host = ipaddress.IPv4Interface(data.get("interface", ""))
    peer = ipaddress.IPv4Address(data.get("peer", ""))
    network = host.network
    # /31 adalah point-to-point; /32 merepresentasikan satu alamat.
    special = network.prefixlen >= 31
    first = network.network_address if special else network.network_address + 1
    last = network.broadcast_address if special else network.broadcast_address - 1
    count = network.num_addresses if special else network.num_addresses - 2
    return dict(title="Perhitungan CIDR", detail=f"Peer {'ada di subnet yang sama' if peer in network else 'di luar subnet; butuh route/gateway'}.",
                rows=[{"network": str(network), "netmask": str(network.netmask), "broadcast": str(network.broadcast_address),
                       "host awal": str(first), "host akhir": str(last), "jumlah host": count, "peer satu subnet": peer in network}],
                trace="Bit network berasal dari prefix input. /31 dan /32 ditangani tanpa mengurangi dua alamat.")
