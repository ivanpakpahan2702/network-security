# 33. CORS & credentialed requests

Lanjutan | Web | Port 5133

Buktikan kapan halaman dari origin lain dapat membaca respons API menggunakan cookie korban.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 33_cors_policy`

Atau mandiri: `.\.venv\Scripts\python.exe labs/33_cors_policy/app.py`

Materi: http://127.0.0.1:5100/learn/09_advanced_appsec (dashboard harus berjalan)

## Mekanisme

Merefleksikan Origin dan mengizinkan credentials dapat membuka data kepada origin yang tidak dipercaya. CORS mengatur pembacaan oleh browser, bukan otorisasi API.

## Latihan

1. Buka akun korban untuk membuat cookie sesi.
2. Buka pembaca lintas origin dari dashboard dan tekan Ambil data.
3. Bandingkan mode rentan dengan allowlist origin; browser akan menolak pembacaan pada mode diperbaiki.

## Hasil dan mitigasi

Respons ber-cookie terbaca dari dashboard hanya pada endpoint rentan.

Gunakan allowlist origin eksak, Vary: Origin, dan credentials hanya saat dibutuhkan. Pertahankan autentikasi serta proteksi CSRF terpisah.

## Batas praktik

CORS dan cookie browser nyata di antara port dashboard dan lab; target fetch hanya API dummy pada host lab.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
