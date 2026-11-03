# 26. NAT & stateful firewall

Menengah | Network | Port 5126

Bedakan paket balasan koneksi yang ada dari trafik masuk yang tidak diminta.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 26_stateful_firewall`

Atau mandiri: `.\.venv\Scripts\python.exe labs/26_stateful_firewall/app.py`

Materi: http://127.0.0.1:5100/learn/05_network_controls (dashboard harus berjalan)

## Mekanisme

NAT memetakan alamat/port; stateful filtering memutuskan trafik berdasarkan state koneksi. Keduanya bukan konsep yang sama.

## Latihan

1. Lihat koneksi keluar 10.0.0.10:49152 → 198.51.100.20:443.
2. Kirim paket dari sumber yang berbeda ke port NAT yang sama.
3. Bandingkan dengan balasan sumber/port yang sesuai state.

## Hasil dan mitigasi

Pemeriksaan mapping NAT saja menerima trafik salah; pemeriksaan state tuple menolaknya.

Gunakan default-deny inbound, state tracking, timeout, dan kebijakan egress. Enkripsi/authentication aplikasi tetap diperlukan.

## Batas praktik

Simulasi connection tracking TCP yang disederhanakan di SQLite; tidak membuat firewall OS.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc5382.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
