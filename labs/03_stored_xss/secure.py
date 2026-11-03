from flask import render_template_string


def render_comments(comments):
    # DIPERBAIKI: database menyimpan data, Jinja melakukan escaping saat output.
    return render_template_string("<h2>Komentar tersimpan</h2>{% for item in comments %}<article>{{ item }}</article>{% endfor %}",
                                  comments=comments)


def run(db, data, context):
    if db.execute("SELECT COUNT(*) FROM comments WHERE mode='secure'").fetchone()[0] >= 50:
        raise ValueError("Batas 50 komentar. Reset lab untuk mengulang.")
    db.execute("INSERT INTO comments (mode, body) VALUES (?, ?)", ("secure", data.get("comment", "")[:4096]))
    return dict(title="Komentar tersimpan dengan escaping output", detail="Payload tetap data teks, termasuk ketika pratinjau dimuat ulang.",
                preview="/preview/secure")
