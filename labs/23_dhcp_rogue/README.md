# 23. Rogue DHCP & DHCP snooping

Menengah | Network | Port 5123

Bandingkan penerimaan offer dari port klien dengan port DHCP yang dipercaya.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 23_dhcp_rogue`

Atau mandiri: `.\.venv\Scripts\python.exe labs/23_dhcp_rogue/app.py`

Materi: http://127.0.0.1:5100/learn/05_network_controls (dashboard harus berjalan)

## Mekanisme

DHCP offer dapat memberi gateway dan DNS. Perangkat yang menerima offer dari sembarang asal dapat mendapat konfigurasi jaringan yang salah.

## Latihan

1. Kirim offer dari access-7.
2. Amati lease dummy yang disimpan.
3. Ulangi lewat uplink-1 dengan gateway/DNS yang benar.

## Hasil dan mitigasi

Offer pada port tak dipercaya ditolak oleh model DHCP snooping.

Tetapkan trusted port secara ketat dan audit binding DHCP. Port uplink yang salah ditandai trusted dapat melemahkan kontrol.

## Batas praktik

Emulasi offer dan snooping di SQLite; tidak membuka socket UDP atau menyebarkan DHCP di LAN.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc2131.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
