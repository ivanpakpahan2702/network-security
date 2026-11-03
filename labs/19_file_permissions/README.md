# 19. Linux permissions & least privilege

Dasar | System | Port 5119

Hitung hak baca/tulis/eksekusi dari owner, group, dan mode oktal.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 19_file_permissions`

Atau mandiri: `.\.venv\Scripts\python.exe labs/19_file_permissions/app.py`

Materi: http://127.0.0.1:5100/learn/01_security_foundations (dashboard harus berjalan)

## Mekanisme

Bit rwx dibagi menjadi owner/group/other. Mode 777 memberi hak kepada semua kelas, termasuk akun yang tidak terkait layanan.

## Latihan

1. Uji other melakukan write pada 777.
2. Bandingkan dengan profil file rahasia 640.
3. Uji owner read dan group write untuk memahami bit izin.

## Hasil dan mitigasi

Mode awal 777 mengizinkan penulisan oleh other; profil 640 menolaknya.

Terapkan least privilege pada file, user service, dan direktori. ACL, root, mount flags, dan SELinux/AppArmor perlu dianalisis terpisah.

## Batas praktik

Evaluator bit permission offline; tidak menjalankan chmod dan tidak mengubah file OS.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.gnu.org/software/coreutils/manual/html_node/Mode-Structure.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
