# 31. JWT signature & claims

Lanjutan | Web | Port 5131

Bandingkan membaca claims JWT dengan benar-benar memverifikasi token.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 31_jwt_verification`

Atau mandiri: `.\.venv\Scripts\python.exe labs/31_jwt_verification/app.py`

Materi: http://127.0.0.1:5100/learn/09_advanced_appsec (dashboard harus berjalan)

## Mekanisme

Base64url decoding tidak membuktikan token diterbitkan server. Signature, algoritma, issuer, audience, dan expiry harus diperiksa sebelum menggunakan claims.

## Latihan

1. Kirim token alg=none dengan role admin.
2. Mode diperbaiki menolak token tersebut.
3. Gunakan token normal bertanda tangan dan periksa role alice.

## Hasil dan mitigasi

Mode rentan mempercayai admin dari token palsu; mode diperbaiki hanya menerima HS256 dan claims yang sesuai.

Gunakan library JWT terawat dengan algorithm allowlist dan validasi claims. Kelola key rotation dan jangan menyimpan data rahasia di payload JWT.

## Batas praktik

HMAC-SHA256 dan verifikasi JWT nyata, dengan secret khusus dummy yang terlihat di kode; bukan penyedia autentikasi produksi.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc8725.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
