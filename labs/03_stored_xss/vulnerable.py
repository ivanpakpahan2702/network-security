from flask import render_template_string
from markupsafe import Markup


def render_comments(comments):
    # RENTAN saat output, meskipun INSERT sudah memakai parameter binding.
    return render_template_string("<h2>Komentar tersimpan</h2>{% for item in comments %}<article>{{ item }}</article>{% endfor %}",
                                  comments=[Markup(comment) for comment in comments])


def run(db, data, context):
    if db.execute("SELECT COUNT(*) FROM comments WHERE mode='vulnerable'").fetchone()[0] >= 50:
        raise ValueError("Batas 50 komentar. Reset lab untuk mengulang.")
    db.execute("INSERT INTO comments (mode, body) VALUES (?, ?)", ("vulnerable", data.get("comment", "")[:4096]))
    return dict(title="Komentar tersimpan tanpa escaping output", detail="Muat ulang pratinjau untuk membuktikan payload bertahan di database.",
                preview="/preview/vulnerable")
