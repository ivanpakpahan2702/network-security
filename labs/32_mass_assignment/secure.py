from labcore.exercises import json_object


def run(db, data, context):
    changes = json_object(data.get("profile", "{}"))
    if set(changes) - {"display_name", "bio"}:
        return dict(title="Field perubahan tidak diizinkan", detail="Role dan atribut internal tidak boleh diubah melalui endpoint profil.", status=403)
    profile = dict(db.execute("SELECT display_name,bio,role FROM profiles WHERE mode='secure'").fetchone())
    for key, value in changes.items():
        if not isinstance(value, str) or len(value) > 200:
            raise ValueError("Nilai profil harus teks maksimal 200 karakter.")
        profile[key] = value
    db.execute("UPDATE profiles SET display_name=?,bio=? WHERE mode='secure'", (profile["display_name"], profile["bio"]))
    return dict(title="Field profil yang diizinkan diperbarui", detail="Role tetap dikendalikan server.", rows=[profile])
