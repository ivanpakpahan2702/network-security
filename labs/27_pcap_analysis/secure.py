from collections import defaultdict
from labcore.protocols import read_pcap


def run(db, data, context):
    name = data.get("capture", "")
    if name not in {"normal", "scan", "incomplete"}:
        raise ValueError("Capture tidak dikenal.")
    packets = read_pcap((context["fixture"] / "captures" / (name + ".pcap")).read_bytes())
    syns, synacks, ports, completed = set(), set(), defaultdict(set), set()
    for row in packets:
        flow = (row["source"], row["destination"], row["source_port"], row["destination_port"])
        reverse = (flow[1], flow[0], flow[3], flow[2])
        if row["flags"] == "SYN":
            syns.add(flow)
            ports[row["source"]].add(row["destination_port"])
        elif row["flags"] == "SYN-ACK" and reverse in syns:
            synacks.add(reverse)
        elif row["flags"] == "ACK" and flow in synacks:
            completed.add(flow)
    suspects = [source for source, destinations in ports.items() if len(destinations) >= 4]
    return dict(title="Korelasi paket selesai", detail=f"Handshake lengkap: {len(completed)}. Indikasi banyak port: {', '.join(suspects) or 'tidak ada'}. SYN tunggal bisa berarti koneksi gagal, bukan otomatis scan.",
                rows=packets, link=f"/artifacts/{name}.pcap", link_label="Unduh PCAP",
                trace="Parser membaca header biner Ethernet/IPv4/TCP. Analisis terbatas fixture; sequence validation/reassembly penuh tidak diimplementasikan.")
