from flask import render_template_string


def run(db, data, context):
    message = data.get("template", "")[:2048]
    # DIPERBAIKI: template tetap; input pengguna hanya parameter data.
    output = render_template_string("{{ message }}", message=message)
    return dict(title="Input diperlakukan sebagai data", detail=output,
                trace="Template source tetap: {{ message }}\n\nHasil render:\n" + output)
