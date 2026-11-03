from labcore.exercises import json_object


def run(db, data, context):
    changes = json_object(data.get("profile", "{}"))
    profile = dict(db.execute("SELECT display_name,bio,role FROM profiles WHERE mode='vulnerable'").fetchone())
    # RENTAN: field role internal ikut dibinding dari input pengguna.
    for key in profile:
        if key in changes:
            if not isinstance(changes[key], str) or len(changes[key]) > 200:
                raise ValueError("Nilai profil harus teks maksimal 200 karakter.")
            profile[key] = changes[key]
    db.execute("UPDATE profiles SET display_name=?,bio=?,role=? WHERE mode='vulnerable'", tuple(profile.values()))
    return dict(title="Semua field model dapat diperbarui", detail="Perhatikan nilai role pada profil alice.", rows=[profile])
