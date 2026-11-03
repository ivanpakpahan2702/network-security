# 21. TLS & validasi sertifikat

Menengah | Network | Port 5121

Periksa hostname, issuer, dan periode berlaku sebuah sertifikat dummy.

## Jalankan

Dari root: `.\.venv\Scripts\python.exe run.py --lab 21_tls_validation`

Atau mandiri: `.\.venv\Scripts\python.exe labs/21_tls_validation/app.py`

Materi: http://127.0.0.1:5100/learn/05_network_controls (dashboard harus berjalan)

## Mekanisme

Koneksi terenkripsi belum menjamin lawan bicara yang benar. Verifikasi identitas dan rantai kepercayaan merupakan bagian penting TLS.

## Latihan

1. Uji sertifikat wrong-host dengan tujuan bank.lab.test.
2. Coba expired dan untrusted.
3. Pilih valid untuk melihat pemeriksaan berhasil.

## Hasil dan mitigasi

Mode yang mematikan verifikasi menerima semua fixture; validator metadata menolak mismatch.

Gunakan TLS library dengan hostname verification dan trust store yang benar. Periksa chain, EKU, expiry, dan kebijakan revocation sesuai sistem.

## Batas praktik

Simulasi metadata sertifikat dengan tanggal evaluasi fixture tetap; tidak melakukan handshake TLS atau verifikasi signature X.509 nyata.

Kode: `vulnerable.py` berisi mode awal/rentan; `secure.py` berisi validasi/pertahanan. Database terpisah dibuat di `instance/lab.sqlite3`.

Referensi: https://www.rfc-editor.org/rfc/rfc9525.html

## Pilihan database

SQLite adalah default. Tambahkan `--db mysql` untuk memakai MySQL/MariaDB dan isi `database.local.toml` sesuai [panduan MySQL](../../MYSQL.md). Mode MySQL memakai schema terpisah untuk lab ini; berkas SQLite lama tetap tersedia.
