# Hash password lemah

Aplikasi Flask untuk satu jenis serangan. Panduan, payload, hasil, batas simulasi,
dan kedua file sumber tersedia di http://127.0.0.1:5110.

Dari root proyek:

```powershell
.\.venv\Scripts\python.exe labs\10_password_hashing\app.py
```

Atau jalankan dengan dashboard (diperlukan untuk halaman penyerang CSRF):

```powershell
.\.venv\Scripts\python.exe run.py --lab 10_password_hashing
```

- `app.py`: entry point aplikasi mandiri.
- `vulnerable.py`: implementasi rentan yang benar-benar dipakai saat pengujian.
- `secure.py`: perbaikan untuk celah yang sama.
- `instance/lab.sqlite3`: dibuat otomatis; terpisah dari lab lain.
- UI dan infrastruktur dipakai bersama dari `labcore/`, `templates/`, dan `static/`.

Reset menggunakan tombol di halaman lab. Hanya data dummy aplikasi ini yang dipulihkan.


## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
