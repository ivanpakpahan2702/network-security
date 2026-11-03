import ipaddress
from labcore.exercises import records


def run(db, data, context):
    destination = ipaddress.IPv4Address(data.get("destination", ""))
    routes = records(db, "route")
    matches = [route for route in routes if destination in ipaddress.IPv4Network(route["prefix"])]
    selected = max(matches, key=lambda route: ipaddress.IPv4Network(route["prefix"]).prefixlen)
    return dict(title="Route dari longest prefix match", detail=f"Next hop: {selected['next_hop']} melalui {selected['interface']}.",
                rows=matches, trace="Prefix paling spesifik: " + selected["prefix"])
