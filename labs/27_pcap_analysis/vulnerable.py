from labcore.protocols import read_pcap


def run(db, data, context):
    name = data.get("capture", "")
    if name not in {"normal", "scan", "incomplete"}:
        raise ValueError("Capture tidak dikenal.")
    packets = read_pcap((context["fixture"] / "captures" / (name + ".pcap")).read_bytes())
    # Naif: setiap SYN dilabeli sebagai scan tanpa konteks handshake atau tujuan.
    count = sum(row["flags"] == "SYN" for row in packets)
    return dict(title="Alert dari setiap SYN", detail=f"{count} SYN diberi alert. Bahkan koneksi normal akan ditandai oleh rule ini.",
                rows=packets, link=f"/artifacts/{name}.pcap", link_label="Unduh PCAP")
