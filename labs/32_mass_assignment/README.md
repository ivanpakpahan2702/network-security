# 32. Mass assignment

Menengah | Web | Port 5132

Sisipkan role admin dalam JSON perubahan profil.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 32_mass_assignment`

Atau mandiri: `.\.venv\Scripts\python.exe labs/32_mass_assignment/app.py`

Materi: http://127.0.0.1:5100/learn/07_identity_api (dashboard harus berjalan)

## Mekanisme

Binding seluruh field input ke model memungkinkan atribut internal ikut diubah. Validasi tipe saja tidak cukup jika field tersebut tidak boleh diedit pengguna.

## Latihan

1. Kirim JSON yang mengandung role admin.
2. Lihat profil mode rentan berubah.
3. Versi diperbaiki hanya menerima display_name dan bio; ulangi dengan input normal.

## Hasil dan mitigasi

Mode rentan mengubah role alice; allowlist field menolak perubahan role.

Gunakan DTO/allowlist per operasi dan ambil identitas dari sesi server. Field yang ditampilkan di form tidak membatasi field yang dapat dikirim klien.

## Batas praktik

Update profil SQLite nyata pada akun dummy; identitas alice tetap ditentukan server.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
