# 39. Supply chain & integritas artefak

Lanjutan | System | Port 5139

Buktikan mengapa checksum dari sumber yang sama dengan file belum membuktikan keaslian.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 39_artifact_integrity`

Atau mandiri: `.\.venv\Scripts\python.exe labs/39_artifact_integrity/app.py`

Materi: http://127.0.0.1:5100/learn/12_architecture_capstone (dashboard harus berjalan)

## Mekanisme

Penyerang yang mengganti artefak dapat mengganti checksum di sampingnya. Nilai pembanding harus berasal dari sumber yang dipercaya.

## Latihan

1. Pilih tampered dan checksum pemasok yang juga sudah diganti.
2. Bandingkan hasil dengan digest yang dipin server dari rilis tepercaya.
3. Pilih original untuk membuktikan artefak sah tetap diterima.

## Hasil dan mitigasi

Checksum yang dikendalikan pihak pengirim meloloskan tampered; digest tepercaya menolaknya.

Verifikasi signature/provenance dari identitas tepercaya, pin dependency, pelihara SBOM dan proses pembaruan. Hash hanya menjamin kesamaan byte terhadap nilai pembanding.

## Batas praktik

SHA-256 nyata pada artefak teks dummy; tidak mengunduh atau mengeksekusi paket perangkat lunak.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://slsa.dev/spec/v1.1/threats-overview

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
