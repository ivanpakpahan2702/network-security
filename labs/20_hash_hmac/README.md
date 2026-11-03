# 20. Encoding, hash & HMAC

Dasar | Crypto | Port 5120

Bandingkan Base64 yang bisa dibaca kembali dengan HMAC yang mendeteksi perubahan pesan.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 20_hash_hmac`

Atau mandiri: `.\.venv\Scripts\python.exe labs/20_hash_hmac/app.py`

Materi: http://127.0.0.1:5100/learn/04_crypto_password (dashboard harus berjalan)

## Mekanisme

Encoding mengubah representasi, hash membuat digest, sedangkan HMAC mengikat integritas pesan pada secret bersama. Ketiganya berbeda dari enkripsi.

## Latihan

1. Ubah nominal pesan tanpa menghitung ulang MAC dari pengirim.
2. Lihat bahwa Base64 tetap dapat didekode tetapi HMAC tidak cocok.
3. Samakan kedua pesan; verifikasi harus berhasil.

## Hasil dan mitigasi

Perubahan pesan lolos pemeriksaan encoding saja, tetapi gagal verifikasi HMAC.

Gunakan HMAC untuk integritas dengan kunci bersama, AEAD untuk kerahasiaan plus integritas, dan KDF khusus untuk password. Kunci demo bukan contoh penyimpanan kunci produksi.

## Batas praktik

Base64, SHA-256, dan HMAC-SHA256 nyata pada pesan dummy; tidak menyediakan fitur enkripsi buatan sendiri.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc2104.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
