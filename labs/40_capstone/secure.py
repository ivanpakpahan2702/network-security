from labcore.analytics import string_list
from labcore.exercises import json_object


def run(db, data, context):
    report = json_object(data.get("report", "{}"))
    evidence = set(string_list(report, "evidence"))
    controls = set(string_list(report, "controls"))
    actions = string_list(report, "actions")
    criteria = [
        ("Aset terdampak", report.get("host") == "web-01", "E01 dan E04 menunjuk web-01."),
        ("Akun dan dugaan entry", report.get("account") == "alice" and report.get("entry") == "password-reuse", "E02 berisi konfirmasi penggunaan ulang password; E03 mengikatnya ke login alice."),
        ("Bukti autentikasi", {"E02", "E03"} <= evidence, "Cantumkan kegagalan dan login sukses; gagal login saja belum membuktikan kompromi."),
        ("Bukti akses data dan egress", {"E04", "E05"} <= evidence, "Hubungkan akses invoice bob dengan ekspor data tak disetujui."),
        ("Kontrol untuk tiap jalur", {"mfa", "object_authz", "egress"} <= controls, "MFA, otorisasi objek, dan kontrol egress mengatasi titik yang berbeda."),
        ("Respons sampai validasi", actions == ["isolate", "preserve", "rotate", "recover", "validate"], "Kasus ini memerlukan containment, preservasi, rotasi kredensial, recovery, dan validasi."),
    ]
    score = round(100 * sum(bool(passed) for _, passed, _ in criteria) / len(criteria))
    return dict(title=f"Penilaian capstone: {score}/100", detail="Skor menilai kecocokan laporan dengan bukti fixture; bukan sertifikasi atau jaminan kemahiran profesional.",
                rows=[{"kriteria": name, "lulus": bool(passed), "pembahasan": reason} for name, passed, reason in criteria],
                grade=score, link="/artifacts/evidence.json", link_label="Unduh bukti kasus")
