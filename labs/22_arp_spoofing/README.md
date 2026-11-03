# 22. ARP spoofing & binding

Menengah | Network | Port 5122

Coba mengganti MAC gateway dalam tabel ARP virtual.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 22_arp_spoofing`

Atau mandiri: `.\.venv\Scripts\python.exe labs/22_arp_spoofing/app.py`

Materi: http://127.0.0.1:5100/learn/05_network_controls (dashboard harus berjalan)

## Mekanisme

ARP memetakan IPv4 ke MAC dalam broadcast domain. Respons tidak terverifikasi dapat mengarahkan frame ke perangkat yang salah.

## Latihan

1. Lihat mapping gateway sebelum dan setelah respons palsu.
2. Bandingkan dengan binding IP/MAC/port yang dipercaya.
3. Gunakan respons gateway normal dari uplink-1.

## Hasil dan mitigasi

Mode rentan menimpa mapping gateway; mode diperbaiki menolak binding yang tidak cocok.

Gunakan Dynamic ARP Inspection dengan binding yang benar, segmentasi, dan proteksi aplikasi seperti TLS. Binding statis hanya sesuai untuk aset tertentu.

## Batas praktik

Simulasi ARP cache di SQLite; tidak mengirim paket ARP atau mengganggu jaringan LAN.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc826.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
