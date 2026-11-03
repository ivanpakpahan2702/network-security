# 24. Routing & longest prefix match

Menengah | Network | Port 5124

Pilih next hop dari beberapa route yang saling tumpang tindih.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 24_routing`

Atau mandiri: `.\.venv\Scripts\python.exe labs/24_routing/app.py`

Materi: http://127.0.0.1:5100/learn/05_network_controls (dashboard harus berjalan)

## Mekanisme

Router menggunakan prefix paling spesifik di antara route yang cocok. Mengambil kecocokan pertama dapat salah memilih default route.

## Latihan

1. Bandingkan pemilihan route untuk 10.20.1.10.
2. Ubah menjadi 10.20.2.10, lalu alamat internet fixture.
3. Baca tabel prefix dan jelaskan next hop yang dipilih.

## Hasil dan mitigasi

Algoritma lengkap memilih /24 sebelum /16 dan /0.

Verifikasi route terpilih, return path, dan ACL. Longest prefix tidak menjamin next hop tepercaya; routing control plane tetap perlu dilindungi.

## Batas praktik

Evaluasi tabel route SQLite dengan ipaddress; tidak mengubah route komputer.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc1812.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
