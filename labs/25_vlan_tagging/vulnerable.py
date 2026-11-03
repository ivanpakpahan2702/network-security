from labcore.exercises import integer


def run(db, data, context):
    tag = integer(data, "tag", 0, 4094)
    target = data.get("target")
    if target not in {"web", "database"}:
        raise ValueError("Tujuan hanya web atau database virtual.")
    # RENTAN: access port mempercayai VLAN tag yang dikirim klien.
    vlan = tag or 20
    allowed = target == "web" or vlan == 10
    return dict(title="Frame virtual diizinkan" if allowed else "Frame virtual ditolak",
                detail=f"access-7 dianggap VLAN {vlan}; tujuan {target}.", rows=[{"tag klien": tag, "VLAN efektif": vlan, "izin": allowed}], status=200 if allowed else 403)
