"""Progres kuis per browser; penilaian dan jawaban benar hanya diproses server."""
import secrets
from datetime import timedelta

from flask import Response, abort, redirect, render_template, request, session, url_for

from labcore.catalog import LABS
from labcore.curriculum import LEVELS, MODULES, MODULE_BY_ID
from labcore.database import connect
from labcore.network import request_lab
from labcore.mysql_schema import create_schema
from labcore.dbqueries import upsert


def persistent_secret(directory):
    path = directory / ".session-key"
    try:
        with path.open("x", encoding="ascii") as stream:
            stream.write(secrets.token_hex(32))
    except FileExistsError:
        pass
    return path.read_text(encoding="ascii").strip()


def attach_learning(app, database):
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)
    with connect(database) as db:
        create_schema(db, 'learning', """
            CREATE TABLE IF NOT EXISTS lesson_results (
                learner TEXT, module TEXT, best_score INTEGER, last_score INTEGER, attempts INTEGER,
                updated TEXT DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(learner,module));
            CREATE TABLE IF NOT EXISTS lesson_notes (
                learner TEXT, module TEXT, note TEXT, updated TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(learner,module));
        """)

    def learner():
        session.setdefault("learner", secrets.token_hex(24))
        session.permanent = True
        return session["learner"]

    def results():
        with connect(database) as db:
            return {row["module"]: dict(row) for row in db.execute(
                "SELECT * FROM lesson_results WHERE learner=?", (learner(),))}

    @app.context_processor
    def learning_context():
        progress = results()
        return {"modules": MODULES, "module_by_id": MODULE_BY_ID, "levels": LEVELS,
                "lesson_progress": progress, "passed_modules": sum(row["best_score"] >= 75 for row in progress.values())}

    def get_module(module_id):
        if module_id not in MODULE_BY_ID:
            abort(404)
        return MODULE_BY_ID[module_id]

    def lesson_page(item, feedback=None, score=None):
        with connect(database) as db:
            row = db.execute("SELECT note FROM lesson_notes WHERE learner=? AND module=?", (learner(), item["id"])).fetchone()
        return render_template("lesson.html", lesson=item, feedback=feedback, score=score,
                               note=row["note"] if row else "", saved=request.args.get("saved") == "1",
                               related_labs=[request_lab(lab) for lab in LABS if lab["number"] in item["lab_numbers"]])

    @app.get("/learn")
    def curriculum():
        return render_template("curriculum.html")

    @app.get("/learn/<module_id>")
    def lesson(module_id):
        return lesson_page(get_module(module_id))

    @app.post("/learn/<module_id>/quiz")
    def quiz(module_id):
        item = get_module(module_id)
        feedback = []
        for index, question in enumerate(item["questions"]):
            answers = request.form.getlist(f"q{index}")
            if len(answers) != 1 or answers[0] not in [str(i) for i in range(len(question["options"]))]:
                abort(400, "Jawab setiap pertanyaan dengan satu pilihan yang tersedia.")
            selected = int(answers[0])
            feedback.append(dict(question=question["question"], selected=question["options"][selected],
                                 correct=selected == question["answer"], answer=question["options"][question["answer"]],
                                 explanation=question["explanation"]))
        score = round(100 * sum(answer["correct"] for answer in feedback) / len(feedback))
        with connect(database) as db:
            upsert(db, 'lesson_results', dict(learner=learner(), module=module_id, best_score=score, last_score=score, attempts=1),
                   ('learner', 'module'), maximum=('best_score',), increment=('attempts',), timestamps=('updated',))
        return lesson_page(item, feedback, score)

    @app.post("/learn/<module_id>/notes")
    def notes(module_id):
        get_module(module_id)
        note = request.form.get("note", "")
        if len(note) > 4000:
            abort(400, "Catatan maksimal 4000 karakter.")
        with connect(database) as db:
            upsert(db, 'lesson_notes', dict(learner=learner(), module=module_id, note=note),
                   ('learner', 'module'), timestamps=('updated',))
        return redirect(url_for("lesson", module_id=module_id, saved=1) + "#notes")

    @app.get("/learning-report.md")
    def learning_report():
        progress = results()
        with connect(database) as db:
            notes = {row["module"]: row["note"] for row in db.execute("SELECT module,note FROM lesson_notes WHERE learner=?", (learner(),))}
        lines = ["# Laporan belajar Cyber Security Lab", "", "Kuis mengukur pemahaman materi; bukan sertifikasi kompetensi.", ""]
        for item in MODULES:
            result = progress.get(item["id"], {})
            lines += [f"## {item['number']:02d}. {item['title']} ({item['level']})", "",
                      f"Nilai terbaik: {result.get('best_score', 'Belum dikerjakan')} | Percobaan: {result.get('attempts', 0)}",
                      "", "### Tugas praktik", "", item["assignment"], "", "### Catatan peserta", "", notes.get(item["id"], "Belum ada catatan."), ""]
        return Response("\n".join(lines), content_type="text/markdown; charset=utf-8",
                        headers={"Content-Disposition": 'attachment; filename="laporan-belajar.md"'})
