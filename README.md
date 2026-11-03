# Cyber Security Lab — Flask + SQLite / MySQL

**40 aplikasi terpisah, 12 modul belajar, 48 soal dengan pembahasan.**
Materi berbahasa Indonesia mencakup dasar, menengah, dan lanjutan: sistem, jaringan komputer,
web/API, password, kriptografi, deteksi, respons insiden, dan arsitektur.
Setiap lab memiliki folder, kode mode awal/rentan dan mode validasi/perbaikan, serta database sendiri: berkas SQLite atau schema MySQL.
SQLite tetap tersedia tanpa service database. MySQL/MariaDB dapat dipilih sebagai backend alternatif.

## Mulai menggunakan

Dari `C:\xampp\htdocs\network-security`, jalankan:

```powershell
.\start-lab.bat
```

Atau klik dua kali `start-lab.bat`, lalu pilih **1: SQLite** atau **2: MySQL/MariaDB**. Buka:

- Dashboard: **http://127.0.0.1:5100**
- Jalur belajar: **http://127.0.0.1:5100/learn**
- Dari perangkat LAN: **http://192.168.5.51:5100/learn**, jika itu masih IP komputer server.

Jika proses versi lama masih berjalan, tekan **Ctrl+C** pada terminalnya lalu jalankan kembali
`start-lab.bat`. Debugger dan automatic reloader nonaktif, sehingga perubahan kode memerlukan restart.
Alamat bind adalah **0.0.0.0**, bukan `0.0.00`; browser tetap memakai IP server atau localhost.
Tautan antarport mengikuti alamat yang sedang dibuka. Gunakan host/IP yang sama secara konsisten
untuk mempertahankan sesi kuis, CSRF, dan CORS.

Launcher `.bat` memakai execution policy PowerShell hanya untuk proses tersebut, tanpa mengubah
kebijakan komputer. `.venv` sudah tersedia di workspace. Pada komputer baru, launcher membuat
environment dan menginstal Flask; instalasi pertama memerlukan internet. Alternatif manual:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Python minimum **3.11**; diuji dengan **Python 3.14 / Flask 3.1.3**. Aplikasi dijalankan Python,
bukan Apache/XAMPP, walaupun folder berada dalam `htdocs`.

## Pilihan database MySQL / MariaDB

HeidiSQL adalah aplikasi pengelola database; backend lab dapat berupa SQLite atau MySQL/MariaDB.
Gunakan menu `start-lab.bat`, atau jalankan `start-lab.bat --db sqlite` / `start-lab.bat --db mysql`.
Untuk MySQL, siapkan service dan akun database, salin `database.example.toml` menjadi
`database.local.toml`, lalu isi host/port/user/password. Launcher memasang driver MySQL bila diperlukan.
Panduan lengkap, hak akun, dan pengaturan HeidiSQL: **[MYSQL.md](MYSQL.md)**.

Mode MySQL menggunakan schema terpisah per lab serta dashboard, dengan InnoDB dan utf8mb4.
UI dan `/health` menunjukkan backend aktif. SQLite dan MySQL memiliki data/progres terpisah;
beralih backend tidak menghapus atau menyalin data lama. Satu proses memakai satu backend.
`--data-dir` tetap mengatur fixture dan kunci sesi; pemisahan database MySQL ditentukan oleh `prefix`.

## Cara belajar

1. Buka **Jalur belajar** dan ikuti prasyarat modul.
2. Baca konsep dan contoh, lalu buka lab terkait.
3. Coba input normal dan skenario latihan; bandingkan kedua mode.
4. Baca kode beserta nomor baris, jejak hasil, batas praktik, dan mitigasi.
5. Kerjakan tugas praktik, simpan bukti pada catatan, lalu jawab kuis.
6. Setelah materi lanjutan, selesaikan capstone dengan laporan berbasis evidence ID.

Kuis dinilai server, menampilkan pembahasan setelah dikirim, dan lulus pada **75%**.
Nilai terbaik, nilai terakhir, jumlah percobaan, dan catatan disimpan per browser di database aktif.
Cookie dashboard bertahan setelah restart server. Browser/perangkat lain mempunyai identitas sendiri;
menghapus cookie atau mengganti host memutus akses ke progres sebelumnya. Tidak ada akun peserta
atau sinkronisasi antarperangkat. Gunakan **Unduh laporan belajar** untuk mengekspor nilai dan catatan
ke Markdown sebelum berpindah perangkat. Jangan bagikan berkas `.session-key`.

Checklist “Tandai dipelajari” pada dashboard adalah **catatan bersama**, bukan nilai pribadi dan bukan
bukti keberhasilan exploit. Data eksperimen pada backend yang aktif juga dibagikan ke pengguna server yang sama.
Kuis dan rubrik capstone membantu latihan, bukan sertifikasi profesional atau penilaian lengkap atas
kualitas investigasi. Laporan praktik tetap perlu pemeriksaan Anda atau mentor.

## Jalur materi

| Modul | Tingkat | Materi | Lab terkait |
| --- | --- | --- | --- |
| 01 | Dasar | Cara berpikir keamanan & dasar sistem | 19 |
| 02 | Dasar | TCP/IP, subnet, port & alur paket | 15, 16 |
| 03 | Dasar | HTTP, browser, cookie & sesi | 18 |
| 04 | Dasar | Kriptografi dasar & keamanan password | 10, 20 |
| 05 | Menengah | Keamanan infrastruktur jaringan | 14, 17, 21, 22, 23, 24, 25, 26 |
| 06 | Menengah | Keamanan aplikasi web & secure coding | 01, 02, 03, 04, 05, 06, 07, 11, 12 |
| 07 | Menengah | Identitas, sesi & keamanan API | 09, 32 |
| 08 | Menengah | Membaca paket & log | 27 |
| 09 | Lanjutan | AppSec lanjutan: trust & concurrency | 08, 13, 31, 33, 34, 35, 36 |
| 10 | Lanjutan | Detection engineering & SIEM | 28, 29, 37 |
| 11 | Lanjutan | Incident response & bukti | 30 |
| 12 | Lanjutan | Arsitektur, supply chain & capstone | 38, 39, 40 |

Rincian tujuan dan rubrik tersedia di UI dan [LEARNING_PATH.md](LEARNING_PATH.md).
Gunakan [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) untuk menyusun laporan temuan/investigasi.

## Daftar 40 aplikasi

| Folder | Port | Tingkat | Praktik |
| --- | --- | --- | --- |
| `01_sql_injection` | 5101 | Menengah | SQL injection |
| `02_reflected_xss` | 5102 | Menengah | Reflected XSS |
| `03_stored_xss` | 5103 | Menengah | Stored XSS |
| `04_csrf` | 5104 | Menengah | CSRF transfer saldo |
| `05_idor` | 5105 | Menengah | IDOR / broken access control |
| `06_path_traversal` | 5106 | Menengah | Path traversal |
| `07_command_injection` | 5107 | Menengah | Command injection |
| `08_ssrf` | 5108 | Lanjutan | SSRF ke layanan internal |
| `09_brute_force` | 5109 | Menengah | Brute force login |
| `10_password_hashing` | 5110 | Dasar | Hash password lemah |
| `11_open_redirect` | 5111 | Menengah | Open redirect |
| `12_unsafe_upload` | 5112 | Menengah | Upload file berbahaya |
| `13_ssti` | 5113 | Lanjutan | Server-side template injection |
| `14_network_segmentation` | 5114 | Menengah | Firewall & segmentasi jaringan |
| `15_subnetting` | 5115 | Dasar | IPv4 & subnetting |
| `16_tcp_state` | 5116 | Dasar | TCP handshake & state |
| `17_dns_cache` | 5117 | Menengah | DNS cache & respons palsu |
| `18_http_basics` | 5118 | Dasar | Anatomi HTTP & data sensitif |
| `19_file_permissions` | 5119 | Dasar | Linux permissions & least privilege |
| `20_hash_hmac` | 5120 | Dasar | Encoding, hash & HMAC |
| `21_tls_validation` | 5121 | Menengah | TLS & validasi sertifikat |
| `22_arp_spoofing` | 5122 | Menengah | ARP spoofing & binding |
| `23_dhcp_rogue` | 5123 | Menengah | Rogue DHCP & DHCP snooping |
| `24_routing` | 5124 | Menengah | Routing & longest prefix match |
| `25_vlan_tagging` | 5125 | Menengah | VLAN tagging & access port |
| `26_stateful_firewall` | 5126 | Menengah | NAT & stateful firewall |
| `27_pcap_analysis` | 5127 | Menengah | Analisis file PCAP |
| `28_ids_tuning` | 5128 | Lanjutan | IDS: threshold & false positive |
| `29_siem_correlation` | 5129 | Lanjutan | SIEM: korelasi lintas log |
| `30_incident_response` | 5130 | Lanjutan | Incident response & evidence |
| `31_jwt_verification` | 5131 | Lanjutan | JWT signature & claims |
| `32_mass_assignment` | 5132 | Menengah | Mass assignment |
| `33_cors_policy` | 5133 | Lanjutan | CORS & credentialed requests |
| `34_race_condition` | 5134 | Lanjutan | Race condition & transaksi atomik |
| `35_idempotency` | 5135 | Lanjutan | Replay & idempotency |
| `36_request_smuggling` | 5136 | Lanjutan | HTTP framing & request smuggling |
| `37_dns_detection` | 5137 | Lanjutan | Deteksi pola DNS tunneling |
| `38_threat_model` | 5138 | Lanjutan | Threat modeling & trust boundary |
| `39_artifact_integrity` | 5139 | Lanjutan | Supply chain & integritas artefak |
| `40_capstone` | 5140 | Lanjutan | Capstone: investigasi & rencana perbaikan |

## Eksekusi nyata dan batas simulasi

- SQLite, SQL injection, kepemilikan objek, upload BLOB, hashing scrypt, HMAC, dan verifikasi JWT
  benar-benar dijalankan. Race condition memakai dua thread dan transaksi SQLite nyata;
  replay/idempotency menyimpan hasil pembayaran dummy ke database.
- XSS berjalan di sandbox browser. CSRF memakai sesi/cookie dan POST lintas origin nyata.
  CORS memakai API bersesi di port 5133 dan halaman pembaca di dashboard; browser menerapkan header CORS.
- SSRF mengakses HTTP service dummy loopback. Open redirect memakai respons HTTP 302 dengan tujuan dummy.
  SSTI mengevaluasi Jinja dalam sandbox terbatas; command injection memakai emulator, tanpa shell sistem.
- Lab PCAP membuat **berkas biner Ethernet/IPv4/TCP yang valid**, membaca paketnya, dan menyediakan
  unduhan untuk Wireshark. Paket berasal dari fixture sintetis, bukan sniffing jaringan pengguna.
- ARP, DHCP, DNS cache, VLAN, routing, NAT, firewall, dan TLS memakai model/fixture terbatas.
  Validasi TLS memeriksa metadata sertifikat dummy, bukan handshake atau verifikasi X.509 kriptografis.
  Request smuggling membandingkan framing secara offline, tanpa proxy rentan sungguhan.
- IDS, SIEM, dan DNS detection menganalisis log sintetis di SQLite. Label ground truth hanya digunakan
  untuk evaluasi metrik; rule tidak membaca label tersebut untuk mendeteksi serangan.
- Incident response mengubah state virtual. `evidence.json` yang diunduh memiliki byte yang sama
  dengan input SHA-256 pada hasil analisis; hash dapat diperiksa dengan `Get-FileHash`.
  Capstone memberi umpan balik enam kriteria, dengan penjelasan batas penilaiannya.

Lab tidak memindai, menyadap, atau mengubah firewall jaringan pengguna, tidak mengirim data keluar,
dan tidak mengimplementasikan eksploit kernel atau serangan Wi-Fi. “Versi diperbaiki” membahas
kontrol untuk celah tertentu, bukan aplikasi produksi yang sudah lengkap keamanannya.
Gunakan data dummy; jangan memasukkan password atau dokumen pribadi ke form lab.

## Port dan pilihan launcher

Dashboard **5100**, lab **5101–5140**, service internal SSRF **127.0.0.1:5199**.
Dashboard dan lab bind ke **0.0.0.0** secara default dan menerima loopback/IP privat LAN/VPN.
Service SSRF selalu loopback. Tidak diperlukan port forwarding internet.
Jika firewall Windows menghalangi akses perangkat LAN, rentang UI adalah **TCP 5100–5140**
pada profil privat; port 5199 tidak perlu dibuka.

```powershell
# Loopback saja
.\start-lab.bat --host 127.0.0.1
# IP LAN tertentu
.\.venv\Scripts\python.exe run.py --host 192.168.5.51
# Daftar / pilih lab
.\.venv\Scripts\python.exe run.py --list
.\.venv\Scripts\python.exe run.py --lab 15_subnetting 16_tcp_state 27_pcap_analysis
# Geser semua port (dashboard 6100, lab 6101–6140, SSRF 6199)
.\.venv\Scripts\python.exe run.py --port-offset 1000
# Data terpisah, berguna untuk kelas/eksperimen lain
.\.venv\Scripts\python.exe run.py --port-offset 1000 --data-dir .runtime\kelas-b
# Satu aplikasi mandiri
.\.venv\Scripts\python.exe labs\40_capstone\app.py
```

Folder aplikasi tetap bergantung pada komponen bersama di root. Aplikasi mandiri menerima
`--host`, `--port-offset`, dan `--data-dir`; pada app mandiri, data-dir langsung menjadi direktori
database lab tersebut. Pada launcher, data-dir berisi subfolder dashboard dan setiap lab.
Untuk tautan materi, demo CSRF, atau halaman penyerang CORS, gunakan launcher supaya dashboard ikut
aktif. SSRF mandiri otomatis menyalakan service internal. Semua lab secara default dijalankan;
bila memakai `--lab`, dashboard menandai lab lainnya “Belum dijalankan”.

## Struktur dan data

```text
run.py                  Launcher dashboard + lab
labcore/                Factory, SQLite, protokol, fixture, katalog, kurikulum
templates/              Dashboard, materi, kuis, lab, demo browser
static/                 CSS dan JavaScript kontrol UI
labs/01_sql_injection/  app.py, vulnerable.py, secure.py, README.md, instance/
labs/...                Total 40 folder dengan SQLite masing-masing
instance/               dashboard.sqlite3 dan .session-key
tests/                  Tes perilaku, kuis, jaringan, browser, startup
```

`vulnerable.py` berarti mode rentan untuk serangan, atau pendekatan awal yang disederhanakan
untuk fondasi/deteksi. UI membedakan label tersebut. Kode dibaca langsung dari file, dengan nomor baris.
`secure.py` berisi perbaikan, validasi, atau analisis lengkap sesuai fokus lab.

**Reset data lab ini** memulihkan fixture dan state hanya pada lab itu. Database lab lain, nilai kuis,
catatan, dan checklist dashboard tidak dihapus. Riwayat eksperimen mencatat ringkasan/waktu UTC,
tanpa input atau password. Sesi aplikasi lab berubah setelah restart/reset; muat ulang form bila perlu.
Sesi dashboard menggunakan kunci persisten agar nilai kuis tetap dapat diakses setelah restart.

Akun dummy: `admin / LabAdmin!2026`, `alice / LabUser!2026`, `bob / LabUser!2026`.
Plaintext dan MD5 pada fixture adalah bahan belajar; SQL login yang diperbaiki menggunakan hash scrypt.

## Pengujian

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 tests\launcher_check.py
```

Unittest memakai database temporer, mencakup kasus serangan dan input sah, mutasi yang ditolak,
perhitungan subnet, checksum PCAP, metrik deteksi, concurrency, replay, kuis, persistensi, dan isolasi peserta.
Smoke test launcher memakai **offset 2000** (7100–7140, 7199) serta data temporer, memeriksa semua
service, konflik port, dan aplikasi mandiri. Ia menolak mulai bila port uji sudah ditempati.

Tes browser memerlukan Playwright dan Chrome lokal:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -X utf8 tests\browser_check.py --port-offset 1000
.\.venv\Scripts\python.exe -X utf8 tests\browser_check.py --address 192.168.5.51 --port-offset 1000
```

Browser QA menyalakan server dan database temporer, menguji UI desktop/mobile, seluruh halaman,
filter gabungan, kuis, catatan, unduhan, XSS, CSRF, CORS, race condition, dan capstone.
Screenshot disimpan di `.runtime/`; server uji dihentikan otomatis.

## Referensi dan kelanjutan

Materi menautkan [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/), RFC protokol,
[Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/),
[NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final),
[NICE Framework](https://csrc.nist.gov/pubs/sp/800/181/r1/final), dan [SLSA](https://slsa.dev/spec/v1.1/).
Lanjutkan dengan konfigurasi perangkat/VM terisolasi, capture dan log baru, review kode, serta
laporan yang ditinjau mentor. Pola lintas bahasa di lab tidak meniru CVE PHP tertentu; evaluasi kasus
PHP membutuhkan CVE, versi runtime, ekstensi, dan konfigurasi terkait.

## Troubleshooting

- **Masih terlihat 14 lab:** hentikan proses lama dengan Ctrl+C, jalankan ulang launcher, lalu refresh.
- **Port sudah dipakai:** hentikan proses yang relevan atau gunakan `--port-offset`. Startup batal
  bila salah satu port konflik; tidak meninggalkan sebagian service baru berjalan.
- **403 saat akses IP:** restart dengan `--host 0.0.0.0`, gunakan IP privat server (bukan alamat bind).
  Header Host DNS umum dan IP publik tidak diterima oleh batas aplikasi lab.
- **403 token:** muat ulang halaman setelah restart/reset.
- **Kuis tampak kosong:** gunakan browser/profile dan host/IP yang sama seperti sebelumnya.
- **CORS tidak terbaca pada mode rentan:** buka sesi Alice dahulu di port 5133, gunakan host sama,
  lalu ulangi di halaman dashboard. Periksa bahwa kedua service aktif.
- **CSRF tidak menunjukkan transfer:** buka Bank dahulu dengan browser/profile yang sama,
  lalu izinkan tab hasil dari tombol demo.
- **SSRF belum aktif:** gunakan launcher dengan lab 08 atau app 08 mandiri.
- **429 brute force:** tunggu window 60 detik atau reset lab 09.
