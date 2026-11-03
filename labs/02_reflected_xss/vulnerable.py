from urllib.parse import urlencode

from flask import render_template_string
from markupsafe import Markup


def render_input(query):
    # RENTAN: Markup menonaktifkan escaping untuk input yang tidak dipercaya.
    return render_template_string("<h2>Hasil pencarian</h2><div>{{ query }}</div>", query=Markup(query))


def run(db, data, context):
    query = data.get("query", "")[:4096]
    return dict(title="Input dipantulkan sebagai HTML", detail="Lihat eksekusi JavaScript di pratinjau sandbox.",
                trace=render_input(query), preview="/preview/vulnerable?" + urlencode({"query": query}))
