"""QA Chrome nyata dengan data temporer; tidak mengubah progres/data pengguna."""
import argparse
import contextlib
import sys
import tempfile
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import WSGIRequestHandler, make_server

from labcore.catalog import BY_ID, LABS
from labcore.dashboard import create_dashboard
from labcore.factory import create_app
from labcore.services import internal_app
from labcore.network import allowed_address
from labcore.curriculum import MODULES


class QuietHandler(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", default="chrome", choices=("chrome", "msedge", "chromium"))
    parser.add_argument("--address", default="127.0.0.1", help="IP server untuk uji loopback atau LAN")
    parser.add_argument("--port-offset", type=int, default=0, help="Offset seluruh port uji agar tidak mengganggu launcher aktif")
    parser.add_argument("--db-config", type=Path, help="Koneksi MySQL QA; suite memakai schema acak qa_ dan membersihkannya")
    args = parser.parse_args()
    if not allowed_address(args.address, allow_lan=True) or ":" in args.address:
        parser.error("Gunakan alamat IPv4 loopback atau privat milik komputer ini.")
    if not 0 <= args.port_offset <= 60000:
        parser.error("Offset port harus antara 0 dan 60000.")

    def url(port, path=""):
        return f"http://{args.address}:{port + args.port_offset}{path}"

    def lab_url(lab_id):
        return url(BY_ID[lab_id]["port"])
    output = PROJECT_ROOT / ".runtime"
    output.mkdir(exist_ok=True)
    checks = []

    def passed(message):
        checks.append(message)
        print("PASS:", message, flush=True)

    with tempfile.TemporaryDirectory(prefix="security-browser-") as directory, contextlib.ExitStack() as stack:
        root = Path(directory)
        database_settings = None
        if args.db_config:
            from tests.mysql_support import temporary_mysql
            database_settings = stack.enter_context(temporary_mysql(args.db_config))
        apps = [(5100, create_dashboard(list(BY_ID), data_dir=root / "dashboard", allow_lan=True, database_settings=database_settings)), (5199, internal_app())]
        apps += [(lab["port"], create_app(lab["id"], data_dir=root / lab["id"], testing=True, allow_lan=True, database_settings=database_settings)) for lab in LABS]
        for port, app in apps:
            app.config.update(PORT_OFFSET=args.port_offset, SSRF_PORT=5199 + args.port_offset)
            host = "127.0.0.1" if port == 5199 else args.address
            server = make_server(host, port + args.port_offset, app, threaded=True, request_handler=QuietHandler)
            stack.callback(server.server_close)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            stack.callback(server.shutdown)

        with sync_playwright() as playwright, contextlib.ExitStack() as browser_cleanup:
            options = {"headless": True, "args": ["--no-proxy-server"]}
            if args.channel != "chromium":
                options["channel"] = args.channel
            browser = playwright.chromium.launch(**options)
            browser_cleanup.callback(browser.close)
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            response = page.goto(url(5100))
            assert response.status == 200
            expect(page.locator('#database-status h2')).to_have_text('Database aktif: MySQL' if database_settings else 'Database aktif: SQLite')
            expect(page.locator(".lab-card:visible")).to_have_count(len(LABS))
            expect(page.locator(".lab-card h3 a").first).to_have_attribute("href", url(5101))
            page.screenshot(path=str(output / "dashboard-desktop.png"), full_page=True)
            page.get_by_role("button", name="Network", exact=True).click()
            expect(page.locator(".lab-card:visible")).to_have_count(sum(lab['category'] == 'Network' for lab in LABS))
            page.get_by_role('button',name='Dasar',exact=True).click()
            expect(page.locator('.lab-card:visible')).to_have_count(2)
            page.locator('#lab-search').fill('TCP')
            expect(page.locator('.lab-card:visible')).to_have_count(1)
            page.locator('#lab-search').fill('no-such-lab')
            expect(page.locator('#filter-empty')).to_be_visible()
            page.locator('#lab-search').fill('')
            page.get_by_role('button',name='Semua tingkat',exact=True).click()
            page.get_by_role("button", name="Semua", exact=True).click()
            expect(page.locator(".lab-card:visible")).to_have_count(len(LABS))
            page.locator(".lab-card").first.get_by_role("button", name="Tandai dipelajari").click()
            expect(page.locator(".lab-card").first.get_by_role("button", name="✓ Dipelajari")).to_be_visible()
            passed(f"Dashboard: {len(LABS)} kartu, filter gabungan, progres {'MySQL' if database_settings else 'SQLite'}")

            for lab in LABS:
                response = page.goto(lab_url(lab["id"]))
                assert response.status == 200, lab["id"]
                expect(page.get_by_role("heading", name=lab["title"], exact=True)).to_be_visible()
            passed(f"Seluruh {len(LABS)} halaman lab dirender di Chrome")

            page.goto(url(5100,'/learn'))
            expect(page.locator('.lab-card')).to_have_count(len(MODULES))
            for lesson in MODULES:
                response = page.goto(url(5100,'/learn/'+lesson['id']))
                assert response.status == 200, lesson['id']
                expect(page.get_by_role('heading',name=lesson['title'],exact=True)).to_be_visible()
            lesson = MODULES[0]
            page.goto(url(5100,'/learn/'+lesson['id']))
            for index, question in enumerate(lesson['questions']):
                page.locator(f'input[name="q{index}"][value="{question["answer"]}"]').check()
            page.get_by_role('button',name='Periksa jawaban',exact=True).click()
            expect(page.locator('#quiz-result h2')).to_have_text('Nilai 100 / 100')
            expect(page.locator('.quiz-feedback')).to_have_count(4)
            page.locator('#note').fill('Bukti latihan: <script>alert(1)</script>')
            page.get_by_role('button',name='Simpan catatan',exact=True).click()
            expect(page.locator('#notes .notice')).to_have_text('Catatan tersimpan.')
            expect(page.locator('#note')).to_have_value('Bukti latihan: <script>alert(1)</script>')
            with page.expect_download() as download_info:
                page.locator('#notes').get_by_role('link',name='Unduh laporan belajar').click()
            assert download_info.value.suggested_filename == 'laporan-belajar.md'
            page.goto(url(5100,'/learn'))
            expect(page.locator('.lab-card').first).to_contain_text('Nilai terbaik 100%')
            page.screenshot(path=str(output/'curriculum-desktop.png'),full_page=True)
            passed('12 modul: kuis dinilai, pembahasan, catatan tersimpan aman, laporan dapat diunduh')

            page.goto(url(5133,'/account'))
            for mode in ('vulnerable','secure'):
                page.goto(url(5100,'/attacker/cors/'+mode))
                page.get_by_role('button',name='Baca API dengan cookie').click()
                expect(page.locator('#cors-output')).to_contain_text('DATA-API-DUMMY' if mode == 'vulnerable' else 'Browser tidak dapat membaca respons')
            passed('CORS Chrome: cookie nyata, API rentan terbaca lintas origin, versi diperbaiki diblokir')

            page.goto(url(5127))
            with page.expect_download() as download_info:
                page.get_by_role('link',name='normal.pcap',exact=True).click()
            assert download_info.value.suggested_filename == 'normal.pcap'
            page.get_by_role('button',name='Isi input normal',exact=True).click()
            page.get_by_role('button',name='Jalankan analisis lengkap',exact=True).click()
            expect(page.locator('#result')).to_contain_text('Handshake lengkap: 1')
            passed('PCAP: unduhan biner dan analisis handshake melalui UI')

            page.goto(url(5134))
            page.get_by_role('button',name='Uji mode rentan',exact=True).click()
            expect(page.locator('#result')).to_contain_text('Saldo akhir: -60')
            page.get_by_role('button',name='Uji mode diperbaiki',exact=True).click()
            expect(page.locator('#result')).to_contain_text('Saldo akhir: 20')
            page.goto(url(5140))
            page.get_by_role('button',name='Isi input normal',exact=True).click()
            page.get_by_role('button',name='Jalankan analisis lengkap',exact=True).click()
            expect(page.locator('#result .grade')).to_contain_text('100 / 100')
            page.screenshot(path=str(output/'capstone-desktop.png'),full_page=True)
            passed('UI race condition memperlihatkan saldo; capstone menampilkan nilai dan rubrik')

            page.goto(lab_url("01_sql_injection"))
            page.get_by_role("button", name="Isi input normal", exact=True).click()
            expect(page.locator("#username")).to_have_value("admin")
            page.get_by_role("button", name="Uji mode diperbaiki", exact=True).click()
            expect(page.locator("#result h2")).to_have_text("Login berhasil")
            page.get_by_role("button", name="Isi contoh serangan", exact=True).click()
            expect(page.locator("#username")).to_have_value("admin' -- ")
            page.get_by_role("button", name="Uji mode rentan", exact=True).click()
            expect(page.locator("#result h2")).to_have_text("Login berhasil")
            page.screenshot(path=str(output / "sql-injection.png"), full_page=True)
            page.get_by_role("button", name="Uji mode diperbaiki", exact=True).click()
            expect(page.locator("#result h2")).to_have_text("Login ditolak")
            passed("SQL injection: input normal sah, payload hanya membypass versi rentan")

            for lab_id in ("02_reflected_xss", "03_stored_xss", "12_unsafe_upload"):
                page.goto(lab_url(lab_id))
                page.get_by_role("button", name="Uji mode rentan", exact=True).click()
                frame = page.frame_locator("#result iframe")
                expect(frame.locator("body")).to_have_attribute("data-xss", "executed")
                if lab_id != "12_unsafe_upload":
                    page.get_by_role("button", name="Uji mode diperbaiki", exact=True).click()
                    frame = page.frame_locator("#result iframe")
                    expect(frame.locator("body")).not_to_have_attribute("data-xss", "executed")
                    expect(frame.locator("body")).to_contain_text("<script>")
                else:
                    page.get_by_role("button", name="Uji mode diperbaiki", exact=True).click()
                    expect(page.locator("#result h2")).to_have_text("Input ditolak")
                passed(f"{lab_id}: script benar-benar berjalan di sandbox rentan; perbaikan efektif")

            bank = context.new_page()
            attacker = context.new_page()
            for mode in ("vulnerable", "secure"):
                bank.goto(url(5104, f"/bank/{mode}"))
                attacker.goto(url(5100, f"/attacker/csrf/{mode}"))
                with attacker.expect_popup() as popup_info:
                    attacker.get_by_role("button", name="Klaim hadiah (kirim POST lintas origin)").click()
                popup = popup_info.value
                popup.wait_for_load_state()
                expect(popup.locator(".balance")).to_contain_text("900" if mode == "vulnerable" else "1000")
                expect(popup.locator(".notice")).to_contain_text("Transfer berhasil tanpa token" if mode == "vulnerable" else "CSRF ditolak")
                popup.close()
            bank.goto(url(5104, "/bank/secure"))
            bank.get_by_role("button", name="Transfer sah dari bank").click()
            expect(bank.locator(".balance")).to_contain_text("950")
            passed("CSRF browser nyata: cookie ikut lintas origin, token menolak serangan, transfer sah berhasil")

            page.goto(lab_url("08_ssrf"))
            page.get_by_role("button", name="Uji mode rentan", exact=True).click()
            expect(page.locator("#result .trace")).to_contain_text("DUMMY-KEY-NOT-A-REAL-SECRET")
            page.get_by_role("button", name="Uji mode diperbaiki", exact=True).click()
            expect(page.locator("#result h2")).to_have_text("Input ditolak")
            page.get_by_role("button", name="Isi input normal", exact=True).click()
            page.get_by_role("button", name="Uji mode diperbaiki", exact=True).click()
            expect(page.locator("#result .trace")).to_contain_text("healthy")
            passed("SSRF: backend benar-benar mengambil HTTP internal; allowlist memblokir metadata")

            page.goto(lab_url("11_open_redirect"))
            expect(page.locator("#next")).to_have_value(url(5100, "/phishing-demo"))
            page.get_by_role("button", name="Uji mode rentan", exact=True).click()
            with page.expect_popup() as popup_info:
                page.get_by_role("link", name="Buka respons HTTP").click()
            popup = popup_info.value
            popup.wait_for_load_state()
            assert popup.url == url(5100, "/phishing-demo"), popup.url
            popup.close()
            page.get_by_role("button", name="Uji mode diperbaiki", exact=True).click()
            expect(page.locator("#result h2")).to_have_text("Input ditolak")
            passed("Tautan antarport dan open redirect mengikuti alamat server yang dibuka")

            page.goto(lab_url("12_unsafe_upload"))
            page.get_by_role("button", name="Isi input normal", exact=True).click()
            page.get_by_role("button", name="Uji mode diperbaiki", exact=True).click()
            with page.expect_download() as download_info:
                page.get_by_role("link", name="Unduh teks sebagai attachment").click()
            assert download_info.value.suggested_filename.endswith(".txt")
            passed("Upload diperbaiki: unduhan attachment nyata")

            mobile = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            mobile_page = mobile.new_page()
            for target_url, filename in ((url(5100), "dashboard-mobile.png"),
                                         (url(5101), "lab-mobile.png"),
                                         (url(5100,'/learn'), 'curriculum-mobile.png'),
                                         (url(5100,'/learn/'+MODULES[0]['id']), 'lesson-mobile.png'),
                                         (url(5140), 'capstone-mobile.png')):
                mobile_page.goto(target_url)
                assert mobile_page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), target_url
                mobile_page.screenshot(path=str(output / filename), full_page=True)
            passed("Layout mobile 390px: tidak ada overflow horizontal halaman")
            assert not errors, errors
            passed("Tidak ada JavaScript pageerror pada UI kontrol")
    print(f"\n{len(checks)} pemeriksaan browser lulus. Screenshot: {output}", flush=True)


if __name__ == "__main__":
    main()
