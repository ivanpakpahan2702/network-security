import ipaddress


def run(db, data, context):
    host = ipaddress.IPv4Interface(data.get("interface", ""))
    peer = ipaddress.IPv4Address(data.get("peer", ""))
    # Asumsi keliru: semua alamat dianggap memakai prefix /24.
    assumed = ipaddress.IPv4Network(f"{host.ip}/24", strict=False)
    return dict(title="Asumsi subnet /24", detail=f"Peer dianggap {'langsung terhubung' if peer in assumed else 'memerlukan gateway'}.",
                rows=[{"prefix input": str(host.network), "asumsi": str(assumed), "peer": str(peer), "satu subnet": peer in assumed}],
                trace="Prefix pengguna diabaikan. Bandingkan dengan perhitungan CIDR yang benar.")
