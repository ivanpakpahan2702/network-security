# 38. Threat modeling & trust boundary

Lanjutan | Architecture | Port 5138

Petakan aset, aliran data, jalur serangan, dan kontrol yang memutus jalur tersebut.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 38_threat_model`

Atau mandiri: `.\.venv\Scripts\python.exe labs/38_threat_model/app.py`

Materi: http://127.0.0.1:5100/learn/12_architecture_capstone (dashboard harus berjalan)

## Mekanisme

Sistem yang dipercaya karena berada di jaringan internal masih dapat menerima input dari batas kepercayaan lain. Kontrol perlu ditempatkan pada jalur yang tepat.

## Latihan

1. Mulai dengan TLS saja dan identifikasi jalur yang masih terbuka.
2. Tambahkan object_authz dan segmentation; amati jalur yang terputus.
3. Pisahkan kontrol pencegahan, deteksi, dan pemulihan pada laporan.

## Hasil dan mitigasi

TLS tidak menutup seluruh jalur. Hasil menunjukkan residual risk berdasarkan kontrol pada model.

Tinjau data flow dan trust boundary bersama pemilik sistem, validasi asumsi, dan prioritaskan risiko. Skor pembelajaran likelihood × impact bukan skor CVSS resmi.

## Batas praktik

Evaluasi graph dan kontrol offline; tidak melakukan eksploitasi atau penilaian otomatis atas sistem nyata.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
