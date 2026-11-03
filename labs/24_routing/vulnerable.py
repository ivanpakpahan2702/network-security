import ipaddress
from labcore.exercises import records


def run(db, data, context):
    destination = ipaddress.IPv4Address(data.get("destination", ""))
    routes = records(db, "route")
    # Keliru: memilih kecocokan pertama, termasuk default route yang terlalu luas.
    selected = next(route for route in routes if destination in ipaddress.IPv4Network(route["prefix"]))
    return dict(title="Route dari kecocokan pertama", detail=f"Next hop: {selected['next_hop']} melalui {selected['interface']}.",
                rows=routes, trace="Prefix terpilih: " + selected["prefix"])
