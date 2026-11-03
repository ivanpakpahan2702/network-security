# 29. SIEM: korelasi lintas log

Lanjutan | Blue Team | Port 5129

Hubungkan gagal login, login sukses, perubahan role, dan ekspor data dalam satu timeline.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 29_siem_correlation`

Atau mandiri: `.\.venv\Scripts\python.exe labs/29_siem_correlation/app.py`

Materi: http://127.0.0.1:5100/learn/10_detection_engineering (dashboard harus berjalan)

## Mekanisme

Event terpisah sering ambigu. Identitas, timestamp UTC, urutan, dan jendela waktu membantu membangun hipotesis insiden yang dapat dibuktikan.

## Latihan

1. Analisis alice dan urutkan empat fase serangan pada fixture.
2. Bandingkan dengan aktivitas bob.
3. Perkecil window menjadi 1 menit dan lihat bukti yang tidak lagi berkorelasi.

## Hasil dan mitigasi

Korelasi menyatukan bukti beberapa sumber; pencarian kata error saja tidak menangkap rantai ini.

Normalisasi waktu dan field, catat sumber bukti, dan konfirmasi hasil dengan pemilik aset. Korelasi temporal bukan bukti kausalitas tunggal.

## Batas praktik

Korelasi SQL/Python nyata atas log dummy; tidak terhubung ke SIEM perusahaan.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
