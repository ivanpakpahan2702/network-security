from labcore.runtime import contained_read


def run(db, data, context):
    public = (context["fixture"] / "public").resolve()
    path = (public / data.get("filename", "")).resolve()
    # DIPERBAIKI: canonical path wajib tetap berada di dalam folder publik.
    if not path.is_relative_to(public):
        raise ValueError("Path traversal ditolak: file berada di luar direktori publik.")
    return dict(title="File publik terbaca", detail=contained_read(context["fixture"], path),
                trace="Containment setelah resolve() valid.")
