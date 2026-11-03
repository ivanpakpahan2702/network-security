# 34. Race condition & transaksi atomik

Lanjutan | Web | Port 5134

Jalankan dua penarikan saldo bersamaan untuk membuktikan check-then-act race.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 34_race_condition`

Atau mandiri: `.\.venv\Scripts\python.exe labs/34_race_condition/app.py`

Materi: http://127.0.0.1:5100/learn/09_advanced_appsec (dashboard harus berjalan)

## Mekanisme

Dua worker dapat membaca saldo yang sama sebelum salah satunya memperbarui. Validasi yang benar tetapi terpisah dari mutasi tidak menjamin konsistensi.

## Latihan

1. Dua worker mencoba menarik 80 dari saldo 100.
2. Amati saldo -60 pada versi rentan.
3. Versi atomik mengizinkan satu penarikan saja; uji 40 agar keduanya sah.

## Hasil dan mitigasi

SQLite transaksi atomik menjaga saldo tidak negatif.

Gunakan transaksi, conditional update, constraint, dan idempotency sesuai kebutuhan. Lock dalam satu proses saja tidak melindungi deployment multiworker.

## Batas praktik

Dua thread dan transaksi SQLite nyata, terbatas pada wallet dummy unik setiap percobaan. Tidak mengirim beban ke endpoint luar.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
