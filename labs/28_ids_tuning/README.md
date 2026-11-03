# 28. IDS: threshold & false positive

Lanjutan | Blue Team | Port 5128

Uji rule pada dataset berlabel dan ukur precision serta recall.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 28_ids_tuning`

Atau mandiri: `.\.venv\Scripts\python.exe labs/28_ids_tuning/app.py`

Materi: http://127.0.0.1:5100/learn/10_detection_engineering (dashboard harus berjalan)

## Mekanisme

Alert yang terlalu sensitif membanjiri analis; threshold terlalu tinggi dapat melewatkan serangan. Evaluasi butuh dataset yang mencakup trafik normal.

## Latihan

1. Bandingkan rule naif dengan agregasi SYN per sumber dalam jendela waktu.
2. Ubah threshold 3, 5, lalu 20.
3. Catat false positive dan false negative, bukan hanya banyaknya alert.

## Hasil dan mitigasi

Threshold mengubah trade-off deteksi. Hasil menyertakan TP/FP/FN dan precision/recall.

Tuning rule dengan baseline representatif, jendela waktu, allowlist terverifikasi, dan validasi ulang. Hasil satu dataset tidak membuktikan efektivitas produksi.

## Batas praktik

Replay dataset sintetis SQLite; tidak mengendalikan Suricata/Snort atau memantau jaringan nyata.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://docs.suricata.io/en/latest/rules/thresholding.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
