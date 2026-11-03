# 27. Analisis file PCAP

Menengah | Blue Team | Port 5127

Baca paket Ethernet/IPv4/TCP dari PCAP sungguhan lalu kelompokkan pola koneksi.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 27_pcap_analysis`

Atau mandiri: `.\.venv\Scripts\python.exe labs/27_pcap_analysis/app.py`

Materi: http://127.0.0.1:5100/learn/08_packet_logs (dashboard harus berjalan)

## Mekanisme

Satu SYN belum cukup untuk menyimpulkan scan. Korelasi port tujuan dan keberhasilan handshake memberi konteks tambahan.

## Latihan

1. Analisis capture scan dan identifikasi sumber serta port yang dituju.
2. Bandingkan normal dan incomplete; handshake gagal belum tentu serangan.
3. Unduh PCAP dan buka di Wireshark; filter tcp.flags.syn == 1.

## Hasil dan mitigasi

Analisis lengkap menemukan banyak port pada scan; capture normal menunjukkan handshake lengkap.

Gabungkan metadata paket, baseline, log host, dan konteks aset. Capture dapat mengandung data sensitif, dan trafik TLS tidak otomatis bisa dibaca isinya.

## Batas praktik

File PCAP biner nyata, dibuat dari paket sintetis dengan checksum. Tidak melakukan sniffing atau scanning jaringan.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.wireshark.org/docs/wsug_html_chunked/ChapterWork.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
