# 35. Replay & idempotency

Lanjutan | Web | Port 5135

Kirim ulang pembayaran yang sama dan bedakan retry dari transaksi baru.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 35_idempotency`

Atau mandiri: `.\.venv\Scripts\python.exe labs/35_idempotency/app.py`

Materi: http://127.0.0.1:5100/learn/09_advanced_appsec (dashboard harus berjalan)

## Mekanisme

Retry jaringan dapat membuat operasi diterapkan berulang. Idempotency key perlu disimpan atomik bersama hasil dan terikat pada parameter request.

## Latihan

1. Kirim dua request dengan key dan nominal sama.
2. Jalankan lagi; mode diperbaiki mengembalikan hasil tersimpan.
3. Ubah nominal dengan key yang sama: versi diperbaiki menolak konflik.

## Hasil dan mitigasi

Mode rentan membukukan pembayaran berulang; mode diperbaiki menyimpan satu pembayaran per key.

Terapkan unique key yang mencakup identitas/operasi, simpan fingerprint parameter dan respons, lalu commit dalam satu transaksi. Tetapkan kebijakan retensi.

## Batas praktik

Pencatatan pembayaran dan constraint SQLite nyata; semua nominal dummy dan tidak terhubung penyedia pembayaran.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
