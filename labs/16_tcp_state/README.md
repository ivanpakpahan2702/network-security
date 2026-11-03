# 16. TCP handshake & state

Dasar | Network | Port 5116

Ikuti perubahan state koneksi dari SYN sampai data aplikasi.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 16_tcp_state`

Atau mandiri: `.\.venv\Scripts\python.exe labs/16_tcp_state/app.py`

Materi: http://127.0.0.1:5100/learn/02_tcpip_subnet (dashboard harus berjalan)

## Mekanisme

TCP menerima segmen berdasarkan state koneksi. Melihat ACK saja tidak membuktikan bahwa handshake yang sah sudah terjadi.

## Latihan

1. Jalankan ACK,DATA tanpa handshake.
2. Bandingkan dengan SYN,SYN-ACK,ACK,DATA,FIN.
3. Hapus atau tukar satu langkah dan temukan titik penolakannya.

## Hasil dan mitigasi

Model lengkap menolak data tanpa handshake; urutan normal mencapai ESTABLISHED lalu penutupan yang disederhanakan.

Pahami state dan arah paket ketika membaca PCAP. Handshake bukan autentikasi pengguna dan tidak memberi enkripsi.

## Batas praktik

State machine dua arah yang disederhanakan, tanpa paket jaringan. Penutupan FIN direpresentasikan satu langkah; retransmission/window tidak dimodelkan.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc9293.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
