# 25. VLAN tagging & access port

Menengah | Network | Port 5125

Uji frame bertag VLAN admin yang datang dari port tamu.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 25_vlan_tagging`

Atau mandiri: `.\.venv\Scripts\python.exe labs/25_vlan_tagging/app.py`

Materi: http://127.0.0.1:5100/learn/05_network_controls (dashboard harus berjalan)

## Mekanisme

Jika port akses mempercayai tag VLAN dari klien, identitas segmen dapat dipalsukan. VLAN asal seharusnya berasal dari konfigurasi switch.

## Latihan

1. Kirim tag 10 dari access-7 yang seharusnya VLAN tamu 20.
2. Amati dampaknya terhadap akses database.
3. Uji frame untagged menuju web sebagai penggunaan sah.

## Hasil dan mitigasi

Tag klien dipercaya pada mode rentan; mode diperbaiki menolak tagged frame pada access port.

Tetapkan port mode secara eksplisit, batasi VLAN pada trunk, dan terapkan inter-VLAN ACL. VLAN bukan enkripsi.

## Batas praktik

Model switch virtual, bukan eksploit double-tagging pada perangkat nyata.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://cheatsheetseries.owasp.org/cheatsheets/Network_Segmentation_Cheat_Sheet.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
