from urllib.parse import urlencode

from flask import render_template_string


def render_input(query):
    # DIPERBAIKI: template tetap, autoescape Jinja aktif.
    return render_template_string("<h2>Hasil pencarian</h2><div>{{ query }}</div>", query=query)


def run(db, data, context):
    query = data.get("query", "")[:4096]
    return dict(title="Input dirender sebagai teks", detail="Tag HTML di-escape; CSP tambahan memblokir script.",
                trace=render_input(query), preview="/preview/secure?" + urlencode({"query": query}))
