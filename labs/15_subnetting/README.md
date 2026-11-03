# 15. IPv4 & subnetting

Dasar | Network | Port 5115

Hitung network, broadcast, rentang host, dan apakah dua alamat berada dalam subnet yang sama.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 15_subnetting`

Atau mandiri: `.\.venv\Scripts\python.exe labs/15_subnetting/app.py`

Materi: http://127.0.0.1:5100/learn/02_tcpip_subnet (dashboard harus berjalan)

## Mekanisme

Prefix CIDR menentukan bit jaringan. Kesamaan tiga oktet pertama tidak menjamin dua host berada pada subnet yang sama.

## Latihan

1. Bandingkan asumsi /24 dengan perhitungan prefix /25.
2. Ubah peer menjadi .20 lalu .200 dan lihat kebutuhan gateway.
3. Coba /31 dan /32; perhatikan pengecualian rentang host.

## Hasil dan mitigasi

Host .200 berada di luar 192.168.10.0/25; host .20 berada di dalamnya.

Hitung CIDR sebelum menyusun DHCP pool, route, atau ACL. Alamat yang masih satu subnet belum tentu bisa berkomunikasi jika firewall menolak.

## Batas praktik

Perhitungan ipaddress nyata. Tidak mengubah IP atau routing komputer.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc4632.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
