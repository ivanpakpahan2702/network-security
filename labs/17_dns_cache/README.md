# 17. DNS cache & respons palsu

Menengah | Network | Port 5117

Lihat bagaimana respons DNS yang tidak cocok dapat meracuni cache resolver.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 17_dns_cache`

Atau mandiri: `.\.venv\Scripts\python.exe labs/17_dns_cache/app.py`

Materi: http://127.0.0.1:5100/learn/05_network_controls (dashboard harus berjalan)

## Mekanisme

Resolver perlu mencocokkan transaksi dan sumber respons. Data yang diterima tanpa pemeriksaan dapat mengganti pemetaan nama ke IP.

## Latihan

1. Masukkan respons palsu dan periksa cache sebelum/sesudah.
2. Ulangi di mode diperbaiki.
3. Gunakan respons normal dengan ID 4201 dari resolver .53.

## Hasil dan mitigasi

Cache rentan diganti respons palsu; validasi transaksi menolaknya.

Cocokkan ID, pertanyaan, sumber, dan port; gunakan randomisasi dan DNSSEC validation yang benar jika tersedia. Pencocokan transaksi saja tidak menjamin asal data DNS.

## Batas praktik

Simulasi cache SQLite, bukan DNS resolver jaringan; tidak mengklaim mengimplementasikan tanda tangan DNSSEC.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc5452.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
