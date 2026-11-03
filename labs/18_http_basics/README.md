# 18. Anatomi HTTP & data sensitif

Dasar | Web | Port 5118

Bedah method, path, header, body, dan data yang seharusnya tidak masuk log.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 18_http_basics`

Atau mandiri: `.\.venv\Scripts\python.exe labs/18_http_basics/app.py`

Materi: http://127.0.0.1:5100/learn/03_http_browser (dashboard harus berjalan)

## Mekanisme

Request HTTP membawa metadata dan payload. Logging seluruh request dapat menyalin cookie, Authorization, dan password ke tempat dengan hak akses berbeda.

## Latihan

1. Baca bagian request yang dipisahkan parser.
2. Bandingkan log mentah dengan log yang hanya menyimpan metadata terpilih.
3. Ganti GET/POST dan perhatikan body tidak selalu hadir.

## Hasil dan mitigasi

Analisis lengkap tetap menunjukkan struktur request tetapi menyamarkan kredensial pada contoh log.

Pilih field log yang diperlukan; redaksi Authorization, Cookie, query sensitif, dan body. HTTPS melindungi transport, bukan otomatis isi log server.

## Batas praktik

Parsing teks HTTP offline; request tidak dikirim ke host di dalam input.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc9110.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
