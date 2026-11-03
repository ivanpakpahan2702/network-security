# 30. Incident response & evidence

Lanjutan | Blue Team | Port 5130

Pilih urutan tindakan pada insiden aktif dan lihat dampaknya pada bukti serta pemulihan.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 30_incident_response`

Atau mandiri: `.\.venv\Scripts\python.exe labs/30_incident_response/app.py`

Materi: http://127.0.0.1:5100/learn/11_incident_response (dashboard harus berjalan)

## Mekanisme

Tindakan tergesa seperti menghapus sistem dapat merusak bukti. Respons menggabungkan containment, preservasi, eradikasi, pemulihan, dan validasi.

## Latihan

1. Kasus: web-01 sedang mengekspor data dummy ke tujuan tak disetujui.
2. Bandingkan wipe,recover dengan urutan respons yang menjaga bukti.
3. Periksa hash bukti dan fase yang belum selesai.

## Hasil dan mitigasi

Validator menolak pemulihan tanpa preservasi dan containment dalam skenario ini.

Gunakan playbook sesuai konteks, dokumentasikan keputusan dan chain of custody. Prioritas isolasi/preservasi dapat berbeda tergantung risiko dan bukti volatil.

## Batas praktik

State machine respons insiden; seluruh tindakan hanya mengubah status fixture SQLite, bukan host atau file OS.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://csrc.nist.gov/pubs/sp/800/61/r3/final

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
