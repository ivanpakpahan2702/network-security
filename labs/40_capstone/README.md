# 40. Capstone: investigasi & rencana perbaikan

Lanjutan | Blue Team | Port 5140

Analisis kasus terpadu dan susun laporan berbasis bukti dari login hingga akses data.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 40_capstone`

Atau mandiri: `.\.venv\Scripts\python.exe labs/40_capstone/app.py`

Materi: http://127.0.0.1:5100/learn/12_architecture_capstone (dashboard harus berjalan)

## Mekanisme

Kompetensi keamanan menghubungkan bukti teknis dengan dampak, containment, mitigasi, dan validasi. Menebak nama serangan saja tidak cukup.

## Latihan

1. Unduh evidence.json dan susun timeline tanpa melihat contoh lengkap dahulu.
2. Isi laporan: aset, akun, dugaan entry, bukti, kontrol, dan urutan tindakan.
3. Gunakan analisis lengkap untuk mendapat skor serta feedback setiap kriteria; revisi laporan berdasarkan bukti.

## Hasil dan mitigasi

Penilaian lengkap memberi skor untuk enam kriteria dan menunjukkan bukti/rencana yang masih kurang.

Pisahkan observasi dari hipotesis, simpan hash bukti, dokumentasikan batas kesimpulan, dan uji ulang kontrol setelah recovery.

## Batas praktik

Kasus sintetis dan rubric pembelajaran, bukan sertifikasi profesional atau bukti kejadian nyata.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://csrc.nist.gov/pubs/sp/800/61/r3/final

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
