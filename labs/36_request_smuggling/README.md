# 36. HTTP framing & request smuggling

Lanjutan | Network | Port 5136

Bandingkan batas body yang dihitung parser Content-Length dengan parser chunked.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 36_request_smuggling`

Atau mandiri: `.\.venv\Scripts\python.exe labs/36_request_smuggling/app.py`

Materi: http://127.0.0.1:5100/learn/09_advanced_appsec (dashboard harus berjalan)

## Mekanisme

Dua hop HTTP yang berbeda pendapat tentang panjang pesan dapat menafsirkan byte sisa sebagai request berikutnya.

## Latihan

1. Baca offset akhir body dari kedua parser.
2. Periksa byte yang tersisa setelah terminator chunked.
3. Versi diperbaiki menolak kombinasi TE+CL dan header panjang yang ambigu.

## Hasil dan mitigasi

Payload ambigu menghasilkan batas berbeda; validator menolaknya sebelum forwarding.

Gunakan parser yang patuh standar dan konsisten antarlapis. Tolak framing ambigu, tutup koneksi pada error, serta audit normalisasi proxy/backend.

## Batas praktik

Parser byte offline. Request tidak dikirim ke proxy, web server lain, atau jaringan.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc9112.html#name-request-smuggling

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
