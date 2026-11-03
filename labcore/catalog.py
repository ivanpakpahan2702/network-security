from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OWASP = "https://cheatsheetseries.owasp.org/cheatsheets/"


def field(name, label, default, kind="text"):
    return {"name": name, "label": label, "default": default, "kind": kind}


LABS = [
    dict(id="01_sql_injection", title="SQL injection", category="Web", cwe="CWE-89",
         summary="Ubah struktur query login dan masuk tanpa mengetahui password.",
         mechanism="Input digabung ke query SQL. database menafsirkan input sebagai sintaks, sehingga kondisi autentikasi bisa diabaikan.",
         fields=[field("username", "Username", "admin' -- "), field("password", "Password", "salah")],
         normal={"username": "admin", "password": "LabAdmin!2026"},
         steps=["Jalankan input normal untuk melihat login yang sah.", "Gunakan username admin' -- dengan spasi setelah -- dan password sembarang.", "Bandingkan hasil serta query pada kedua mode."],
         expected="Mode rentan masuk sebagai admin. Mode diperbaiki menolak username injeksi.",
         mitigation="Gunakan parameter binding (?) dan verifikasi hash password setelah mencari username. Jangan membangun SQL dengan f-string dari input.",
         boundary="Query nyata pada database lab. Password plaintext hanya tersedia sebagai properti fixture untuk memperlihatkan query lama.",
         reference="SQL_Injection_Prevention_Cheat_Sheet.html"),
    dict(id="02_reflected_xss", title="Reflected XSS", category="Web", cwe="CWE-79",
         summary="Jalankan JavaScript lewat parameter pencarian yang dipantulkan ke HTML.",
         mechanism="Input ditandai sebagai HTML tepercaya. Browser membaca tag script sebagai kode, bukan teks pencarian.",
         fields=[field("query", "Pencarian / payload", "<script>document.body.dataset.xss='executed';document.body.append(' XSS BERHASIL')</script>", "textarea")],
         normal={"query": "belajar Flask"},
         steps=["Kirim payload ke mode rentan dan lihat tulisan XSS BERHASIL di pratinjau.", "Jalankan payload yang sama pada mode diperbaiki.", "Pada versi diperbaiki tag tampil sebagai teks dan JavaScript tidak berjalan."],
         expected="JavaScript berjalan hanya di pratinjau rentan; versi diperbaiki melakukan escaping.",
         mitigation="Pertahankan autoescape Jinja, hindari Markup/|safe pada input, dan tambahkan CSP sebagai lapisan tambahan.",
         boundary="JavaScript nyata di iframe sandbox tanpa akses origin/cookie halaman lab. Tidak ada pengiriman data keluar.",
         reference="Cross_Site_Scripting_Prevention_Cheat_Sheet.html"),
    dict(id="03_stored_xss", title="Stored XSS", category="Web", cwe="CWE-79",
         summary="Simpan komentar berbahaya lalu lihat kode berjalan saat halaman dibuka lagi.",
         mechanism="Payload disimpan di database dan dirender sebagai HTML tepercaya pada kunjungan berikutnya. Menyimpan di database tidak membuat input aman.",
         fields=[field("comment", "Komentar", "<script>document.body.dataset.xss='executed';document.body.append(' STORED XSS BERHASIL')</script>", "textarea")],
         normal={"comment": "Komentar biasa dari peserta lab."},
         steps=["Simpan komentar pada mode rentan dan buka pratinjau tersimpan.", "Muat ulang pratinjau: kode tetap berjalan karena tersimpan di database.", "Simpan payload di mode diperbaiki; tag akan tampil sebagai teks. Reset menghapus komentar lab ini."],
         expected="Stored XSS bertahan di mode rentan; mode diperbaiki meng-escape saat output.",
         mitigation="Lakukan encoding sesuai konteks output. Jika HTML memang dibutuhkan, gunakan sanitizer dengan allowlist yang terawat.",
         boundary="Penyimpanan dan eksekusi browser nyata; kedua mode memakai kumpulan komentar terpisah dan iframe sandbox.",
         reference="Cross_Site_Scripting_Prevention_Cheat_Sheet.html"),
    dict(id="04_csrf", title="CSRF transfer saldo", category="Web", cwe="CWE-352",
         summary="Halaman di origin lain memanfaatkan cookie korban untuk mengirim transfer.",
         mechanism="Browser melampirkan cookie sesi ke request yang sesuai. Endpoint rentan percaya pada cookie tanpa memeriksa token anti-CSRF.",
         fields=[field("amount", "Jumlah transfer dummy", "100"), field("recipient", "Penerima", "penyerang-demo")],
         normal={"amount": "50", "recipient": "teman-demo"},
         steps=["Buka Bank rentan untuk membuat sesi korban (saldo awal 1000).", "Buka Halaman penyerang dari dashboard port 5100, lalu klik tombol transfer palsu.", "Saldo rentan berkurang tanpa token. Ulangi dengan Bank diperbaiki: request ditolak.", "Form transfer sah pada Bank diperbaiki menyertakan token dan tetap berhasil."],
         expected="POST lintas origin berhasil pada bank rentan, tetapi ditolak pada bank diperbaiki.",
         mitigation="Validasi token acak yang terikat sesi dan Origin pada operasi perubahan data. Gunakan SameSite sebagai lapisan tambahan.",
         boundary="Request dan cookie browser nyata. Port 5100 dan 5104 berbeda origin tetapi masih same-site, sehingga SameSite saja tidak cukup di skenario ini.",
         reference="Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html"),
    dict(id="05_idor", title="IDOR / broken access control", category="Web", cwe="CWE-639",
         summary="Ganti ID invoice untuk membaca dokumen milik pengguna lain.",
         mechanism="Aplikasi mencari objek berdasarkan ID tanpa membatasi pemiliknya. Login tidak otomatis memberikan izin ke seluruh objek.",
         fields=[field("invoice_id", "ID invoice (sesi selalu alice)", "2")], normal={"invoice_id": "1"},
         steps=["Ambil invoice 1 milik alice (pengguna sesi dummy).", "Ganti ID menjadi 2, milik bob.", "Versi diperbaiki menolak objek yang tidak dimiliki alice dengan respons 404."],
         expected="Mode rentan membocorkan invoice bob. Mode diperbaiki hanya mengembalikan invoice alice.",
         mitigation="Ambil identitas dari sesi server, lalu cek otorisasi pada setiap objek. UUID tidak menggantikan pemeriksaan pemilik.",
         boundary="Identitas alice ditetapkan server untuk mengisolasi pelajaran otorisasi; input tidak dapat memilih identitas.",
         reference="Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html"),
    dict(id="06_path_traversal", title="Path traversal", category="Web", cwe="CWE-22",
         summary="Keluar dari folder unduhan lewat ../ untuk membaca file rahasia dummy.",
         mechanism="Path input digabung ke folder publik tanpa memastikan hasil canonical path masih berada di direktori yang diizinkan.",
         fields=[field("filename", "Nama file", "../private/secret.txt")], normal={"filename": "readme.txt"},
         steps=["Baca readme.txt sebagai unduhan normal.", "Gunakan ../private/secret.txt untuk keluar dari folder public.", "Versi diperbaiki memeriksa path final setelah resolve() dan menolak traversal."],
         expected="Rahasia dummy terbaca pada mode rentan, sedangkan versi diperbaiki menolak path.",
         mitigation="Resolve path lalu periksa containment terhadap direktori publik; lebih baik petakan ID file ke path server yang sudah dikenal.",
         boundary="Pembacaan file nyata, tetapi lapisan lab membatasi semua akses ke fixture lab; file mesin di luar fixture tidak dapat dibaca.",
         reference="File_Upload_Cheat_Sheet.html"),
    dict(id="07_command_injection", title="Command injection", category="Web", cwe="CWE-78",
         summary="Tambahkan perintah kedua pada fitur diagnostik ping.",
         mechanism="Menggabungkan input ke string perintah memungkinkan operator ; atau && mengubah struktur perintah.",
         fields=[field("host", "Host diagnostik", "127.0.0.1; whoami")], normal={"host": "127.0.0.1"},
         steps=["Kirim host normal 127.0.0.1.", "Tambahkan ; whoami atau && cat /lab/secret.txt.", "Versi diperbaiki memvalidasi IP dan memakai daftar argumen, sehingga metakarakter ditolak."],
         expected="Interpreter lab menjalankan perintah dummy tambahan pada mode rentan.",
         mitigation="Hindari shell; gunakan API langsung atau subprocess.run dengan daftar argumen, shell=False, validasi argumen, dan timeout.",
         boundary="EMULASI interpreter terbatas: hanya ping, whoami, dan cat /lab/secret.txt. Tidak mengeksekusi shell OS atau ping jaringan nyata.",
         reference="OS_Command_Injection_Defense_Cheat_Sheet.html"),
    dict(id="08_ssrf", title="SSRF ke layanan internal", category="Network", cwe="CWE-918",
         summary="Fitur fetch URL dipakai untuk membaca metadata internal dummy.",
         mechanism="Backend mengambil URL yang dipilih pengguna dengan hak akses jaringan server. URL yang seharusnya internal ikut dapat diakses.",
         fields=[field("url", "URL target lab", "http://127.0.0.1:5199/internal/metadata")], normal={"url": "http://127.0.0.1:5199/public/status"},
         steps=["Fetch /public/status untuk melihat request HTTP normal.", "Ubah path menjadi /internal/metadata; backend rentan membaca kunci dummy.", "Versi diperbaiki memetakan URL ke satu endpoint publik yang diizinkan, tanpa mengikuti redirect."],
         expected="HTTP ke service 5199 sungguhan membocorkan metadata dummy pada mode rentan.",
         mitigation="Petakan pilihan pengguna ke endpoint tetap, batasi egress, validasi scheme/host/port/path dan semua tujuan redirect. Cegah DNS rebinding jika hostname dinamis digunakan.",
         boundary="HTTP loopback nyata. Transport lab hanya boleh menuju 127.0.0.1:5199, tanpa proxy/redirect; tidak dapat menjangkau internet atau layanan lokal lain.",
         reference="Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"),
    dict(id="09_brute_force", title="Brute force login", category="Password", cwe="CWE-307",
         summary="Bandingkan tebakan password berulang dengan pembatasan percobaan login.",
         mechanism="Tanpa throttling, penyerang dapat menguji banyak kandidat password secara online. Hash yang kuat saja tidak menghentikan tebakan ke endpoint login.",
         fields=[field("candidates", "Kandidat (satu per baris, maksimal 8)", "123456\npassword\nadmin123\nrahasia\nLabUser!2026", "textarea")],
         normal={"candidates": "LabUser!2026"},
         steps=["Jalankan daftar default: password benar berada pada percobaan kelima.", "Mode rentan terus mencoba hingga berhasil.", "Mode diperbaiki membatasi 3 kegagalan per akun per 60 detik, lalu mengembalikan 429. Reset untuk mengulang."],
         expected="Login rentan berhasil pada kandidat kelima; mode diperbaiki menghentikan tebakan setelah tiga kegagalan.",
         mitigation="Gabungkan throttling akun dan sumber, backoff, MFA, monitoring, serta pesan error generik. Pertimbangkan risiko lockout sebagai denial of service.",
         boundary="Verifikasi hash nyata terhadap satu akun lab tetap (alice), tanpa target URL, concurrency, atau wordlist eksternal. Throttle sederhana ini bahan belajar, bukan sistem produksi lengkap.",
         reference="Authentication_Cheat_Sheet.html"),
    dict(id="10_password_hashing", title="Hash password lemah", category="Password", cwe="CWE-916",
         summary="Lihat MD5 cepat ditebak dan bandingkan dengan scrypt bersalt.",
         mechanism="Hash cepat tanpa salt menghasilkan digest sama untuk password sama dan murah diuji offline. Salt tidak membuat password lemah menjadi kuat.",
         fields=[field("candidates", "Kandidat offline (maksimal 8)", "123456\npassword\nrahasia\nLabUser!2026", "textarea")],
         normal={"candidates": "LabUser!2026"},
         steps=["Jalankan daftar yang sama di mode MD5 dan scrypt.", "Bandingkan digest dua akun dengan password sama, jumlah tebakan, serta waktu verifikasi.", "Perhatikan password lemah tetap bisa ditemukan pada scrypt jika kandidat benar tersedia."],
         expected="Digest MD5 sama untuk dua akun; scrypt berbeda karena salt acak dan lebih mahal diverifikasi. Kedua mode tetap dapat menemukan password dalam daftar.",
         mitigation="Gunakan Argon2id atau scrypt dengan parameter yang ditinjau, salt unik, password panjang, dan rencana upgrade hash saat login. Jangan gunakan MD5/SHA biasa untuk password.",
         boundary="Hash dan verifikasi kriptografis nyata; waktu bergantung mesin. Scrypt memakai N=32768, r=8, p=3; maksimal delapan kandidat dummy.",
         reference="Password_Storage_Cheat_Sheet.html"),
    dict(id="11_open_redirect", title="Open redirect", category="Web", cwe="CWE-601",
         summary="Ubah tujuan redirect agar pengguna diarahkan ke halaman penyerang dummy.",
         mechanism="Parameter next langsung dipakai menjadi Location, sehingga domain aplikasi bisa menyamarkan tujuan tautan.",
         fields=[field("next", "Tujuan setelah login", "http://127.0.0.1:5100/phishing-demo")], normal={"next": "/welcome"},
         steps=["Gunakan /welcome untuk redirect yang sah.", "Uji URL absolut menuju phishing-demo dashboard.", "Buka respons redirect dan lihat header Location; versi diperbaiki hanya menerima path yang ada dalam allowlist."],
         expected="Mode rentan mengirim HTTP 302 ke URL dummy penyerang; mode diperbaiki menolak URL absolut.",
         mitigation="Gunakan ID tujuan atau allowlist path lokal. Jangan hanya memeriksa awalan '/' karena //host adalah URL lintas host.",
         boundary="Header redirect nyata. Batas lab menahan URL di dashboard pada host lab yang sama; tidak ada halaman yang meminta kredensial.",
         reference="Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html"),
    dict(id="12_unsafe_upload", title="Upload file berbahaya", category="Web", cwe="CWE-434",
         summary="Unggah HTML aktif yang dianggap sebagai dokumen biasa oleh aplikasi.",
         mechanism="Aplikasi percaya nama dan MIME dari pengguna lalu menampilkan file sebagai HTML pada origin aplikasi.",
         fields=[field("filename", "Nama file fallback (atau pilih file lokal)", "catatan.html"), field("content", "Isi file fallback", "<h2>Dokumen unggahan</h2><script>document.body.dataset.xss='executed';document.body.append(' UPLOAD XSS BERHASIL')</script>", "textarea")],
         normal={"filename": "catatan.txt", "content": "Dokumen teks biasa."},
         steps=["Kirim file HTML default atau pilih file sendiri (maksimal 64 KiB).", "Mode rentan menyajikan HTML inline; JavaScript berjalan di pratinjau.", "Mode diperbaiki hanya menerima teks UTF-8 berekstensi .txt dan menyajikannya sebagai attachment dengan nosniff."],
         expected="HTML aktif berjalan di iframe rentan. Mode diperbaiki menolak .html dan menawarkan unduhan untuk .txt.",
         mitigation="Terapkan allowlist format, cek isi, batasi ukuran, gunakan nama internal acak, simpan di luar webroot, dan sajikan sebagai attachment dari origin terpisah bila perlu.",
         boundary="Upload multipart dan database BLOB nyata. Tidak ada eksekusi PHP/Python server; demo terbatas pada active content browser di sandbox.",
         reference="File_Upload_Cheat_Sheet.html"),
    dict(id="13_ssti", title="Server-side template injection", category="Web", cwe="CWE-1336",
         summary="Bedakan input template yang dieksekusi server dari data teks biasa.",
         mechanism="Input pengguna dijadikan sumber template, sehingga ekspresi {{ ... }} dievaluasi oleh Jinja di sisi server.",
         fields=[field("template", "Template / pesan", "Halo {{ 7 * 7 }} — {{ secret }}", "textarea")], normal={"template": "Halo peserta lab!"},
         steps=["Jalankan payload {{ 7 * 7 }} untuk melihat evaluasi menjadi 49.", "Akses {{ secret }} untuk membaca konteks rahasia dummy.", "Mode diperbaiki memakai template tetap dan memperlakukan seluruh input sebagai data."],
         expected="Mode rentan mengevaluasi ekspresi dan membocorkan secret dummy; mode diperbaiki menampilkan ekspresi literal.",
         mitigation="Jangan pernah menjadikan input sebagai template source. Render template tetap dengan parameter data dan autoescape.",
         boundary="Evaluasi Jinja nyata memakai sandbox khusus yang menolak atribut, pemanggilan fungsi, loop, perkalian besar, dan eksponen. Tidak menyediakan akses objek Flask, filesystem, atau shell.",
         reference="Injection_Prevention_Cheat_Sheet.html"),
    dict(id="14_network_segmentation", title="Firewall & segmentasi jaringan", category="Network", cwe="CWE-284",
         summary="Uji koneksi antarzona untuk melihat dampak firewall allow-all.",
         mechanism="Jaringan datar membuat workstation dapat menjangkau layanan database dan administrasi. Aturan berdasarkan zona dan port mengurangi jalur akses.",
         fields=[field("source", "Zona sumber: workstation / web / admin", "workstation"), field("target", "Layanan tujuan: web / database / admin", "database"), field("port", "Port tujuan", "5432")],
         normal={"source": "web", "target": "database", "port": "5432"},
         steps=["Uji workstation ke database:5432 pada kedua mode.", "Uji web ke database:5432, lalu admin ke admin:22.", "Periksa rule yang cocok. Port terbuka hanya menunjukkan reachability, bukan akses data atau autentikasi."],
         expected="Allow-all mengizinkan jalur berisiko; default-deny hanya mengizinkan aliran yang dibutuhkan.",
         mitigation="Gunakan default-deny, segmentasi, pembatasan ingress/egress, autentikasi per layanan, dan audit aturan. Segmentasi tidak menggantikan patching.",
         boundary="SIMULASI topologi virtual dan evaluasi rule di database. Tidak memindai jaringan nyata dan tidak mengubah firewall Windows.",
         reference="Network_Segmentation_Cheat_Sheet.html"),
]

from labcore.advanced_catalog import NEW_LABS
from labcore.curriculum import LAB_MODULES

LABS.extend(NEW_LABS)
for index, lab in enumerate(LABS, 1):
    lab["number"] = index
    lab["port"] = 5100 + index
    lab["url"] = f"http://127.0.0.1:{lab['port']}"
    lab["reference_url"] = lab.get("reference_url") or OWASP + lab["reference"]
    lab["attack"] = {item["name"]: item["default"] for item in lab["fields"]}
    lab.setdefault("level", "Dasar" if index == 10 else "Lanjutan" if index in (8, 13) else "Menengah")
    lab.setdefault("kind", "attack")
    lab.setdefault("duration", 45)
    lab["module_ids"] = LAB_MODULES[index]
    lab["mode_names"] = ({"vulnerable": "Mode rentan", "secure": "Mode diperbaiki"} if lab["kind"] == "attack" else
                         {"vulnerable": "Analisis awal", "secure": "Analisis lengkap"})
    lab["mode_buttons"] = ({"vulnerable": "Uji mode rentan", "secure": "Uji mode diperbaiki"} if lab["kind"] == "attack" else
                           {"vulnerable": "Jalankan analisis awal", "secure": "Jalankan analisis lengkap"})

BY_ID = {lab["id"]: lab for lab in LABS}
