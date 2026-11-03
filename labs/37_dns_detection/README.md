# 37. Deteksi pola DNS tunneling

Lanjutan | Blue Team | Port 5137

Bandingkan rule panjang label dengan korelasi entropy, volume, dan domain tujuan.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 37_dns_detection`

Atau mandiri: `.\.venv\Scripts\python.exe labs/37_dns_detection/app.py`

Materi: http://127.0.0.1:5100/learn/10_detection_engineering (dashboard harus berjalan)

## Mekanisme

Label DNS yang panjang bisa berasal dari aktivitas sah. Beberapa indikator yang konsisten lebih berguna daripada satu ukuran saja.

## Latihan

1. Bandingkan domain CDN fixture dengan domain telemetry yang tidak disetujui.
2. Ubah threshold dan lihat query yang dipilih.
3. Jelaskan mengapa hasil perlu dikonfirmasi dari endpoint dan kebijakan organisasi.

## Hasil dan mitigasi

Rule gabungan menekan false positive CDN pada fixture; threshold yang terlalu tinggi dapat melewatkan pola.

Gunakan resolver terkelola, egress policy, baseline, korelasi endpoint, dan inspeksi log yang proporsional. Entropy tinggi bukan bukti exfiltration tunggal.

## Batas praktik

Analisis log DNS sintetis di SQLite, tanpa resolusi nama, pembuatan tunnel, atau pengiriman data.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
