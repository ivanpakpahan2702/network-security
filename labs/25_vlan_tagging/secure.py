from labcore.exercises import integer


def run(db, data, context):
    tag = integer(data, "tag", 0, 4094)
    if data.get("target") not in {"web", "database"}:
        raise ValueError("Tujuan hanya web atau database virtual.")
    # Access port ini hanya menerima untagged frame; VLAN berasal dari switch config.
    if tag != 0:
        return dict(title="Tag pada access port ditolak", detail="access-7 bukan trunk dan tetap dipetakan ke VLAN tamu 20.", status=403)
    allowed = data.get("target") == "web"
    return dict(title="ACL VLAN mengizinkan" if allowed else "ACL VLAN menolak",
                detail="VLAN 20 hanya boleh menuju layanan web dalam model ini.", rows=[{"VLAN efektif": 20, "izin": allowed}], status=200 if allowed else 403)
