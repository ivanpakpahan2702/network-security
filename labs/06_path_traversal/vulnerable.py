from labcore.runtime import contained_read


def run(db, data, context):
    fixture = context["fixture"]
    # RENTAN: hasil path tidak dibatasi terhadap folder public.
    path = fixture / "public" / data.get("filename", "")
    # Batas transport lab hanya melindungi mesin; private fixture masih bocor.
    content = contained_read(fixture, path)
    return dict(title="File terbaca", detail=content, trace="public/" + data.get("filename", ""))
