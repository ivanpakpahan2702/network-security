# Jalur belajar dan rubrik praktik

Versi interaktif: `/learn` pada dashboard. Nilai kuis ≥75% menandai lulus pemahaman; selesaikan tugas praktik juga.

## 01. Cara berpikir keamanan & dasar sistem

Dasar · Estimasi 45 menit

Prasyarat: Tidak ada

Tujuan:

- Membedakan aset, threat, vulnerability, impact, dan risk.
- Membaca izin file dan memahami identitas service.
- Menyusun catatan eksperimen yang dapat diulang.

Lab: 19

**Tugas:** Buat inventaris tiga aset lab, identitas proses yang mengaksesnya, dan risiko jika hak akses terlalu luas. Uji owner/group/other di lab permission.

Rubrik:

- Setiap aset memiliki pemilik dan dampak yang jelas.
- Catatan membedakan bukti dari dugaan.
- Perbaikan diuji dengan operasi sah dan operasi terlarang.

Referensi:

- [NIST NICE Framework](https://csrc.nist.gov/pubs/sp/800/181/r1/final)
- [GNU file permissions](https://www.gnu.org/software/coreutils/manual/html_node/Mode-Structure.html)

## 02. TCP/IP, subnet, port & alur paket

Dasar · Estimasi 45 menit

Prasyarat: 01_security_foundations

Tujuan:

- Menghitung subnet dari prefix CIDR.
- Membedakan MAC, IP, port, switch, router, dan gateway.
- Menjelaskan handshake serta perbedaan TCP dan UDP.

Lab: 15, 16

**Tugas:** Bagi jaringan 192.168.10.0/24 menjadi dua /25. Tulis rentang host, lalu jelaskan jalur paket dari .10 menuju .200. Rekonstruksi satu handshake dari urutan segmen.

Rubrik:

- Network dan broadcast dihitung dengan benar.
- IP tujuan dibedakan dari MAC next hop.
- Handshake tidak disamakan dengan enkripsi/autentikasi.

Referensi:

- [RFC 4632 CIDR](https://www.rfc-editor.org/rfc/rfc4632.html)
- [RFC 9293 TCP](https://www.rfc-editor.org/rfc/rfc9293.html)

## 03. HTTP, browser, cookie & sesi

Dasar · Estimasi 45 menit

Prasyarat: 01_security_foundations, 02_tcpip_subnet

Tujuan:

- Membedah request/response HTTP.
- Membedakan authentication, authorization, cookie, dan session.
- Memahami origin, site, serta batas perlindungan HTTPS.

Lab: 18

**Tugas:** Amati satu form lab melalui DevTools Network. Tulis method, origin, cookie yang terlibat, dan bagian request yang perlu direduksi dari log.

Rubrik:

- Origin dihitung dengan scheme/host/port.
- Sesi dibedakan dari hak akses objek.
- Catatan log tidak menyertakan kredensial mentah.

Referensi:

- [RFC 9110 HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Flask security](https://flask.palletsprojects.com/en/stable/web-security/)

## 04. Kriptografi dasar & keamanan password

Dasar · Estimasi 45 menit

Prasyarat: 03_http_browser

Tujuan:

- Membedakan encoding, hashing, MAC, signature, dan encryption.
- Menjelaskan salt serta biaya KDF password.
- Menghindari kesimpulan salah dari hasil cracking dummy.

Lab: 10, 20

**Tugas:** Bandingkan dua akun dengan password sama pada MD5 dan scrypt. Catat waktu uji, perbedaan digest, dan perubahan satu byte pada pesan HMAC.

Rubrik:

- Salt tidak disamakan dengan encryption key.
- Kesimpulan tidak menyebut scrypt mustahil ditebak.
- Perubahan pesan terdeteksi tanpa mengandalkan encoding.

Referensi:

- [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [RFC 2104 HMAC](https://www.rfc-editor.org/rfc/rfc2104.html)

## 05. Keamanan infrastruktur jaringan

Menengah · Estimasi 60 menit

Prasyarat: 02_tcpip_subnet, 04_crypto_password

Tujuan:

- Menjelaskan trust boundary pada layer 2 hingga aplikasi.
- Membedakan routing, translasi, filtering, dan enkripsi.
- Menguji aliran sah setelah menerapkan pembatasan.

Lab: 14, 17, 21, 22, 23, 24, 25, 26

**Tugas:** Gambar guest, web, database, dan admin sebagai empat zona. Buat matriks minimal enam aliran, pilih kontrol di titik yang tepat, lalu buktikan tiga allow dan tiga deny dalam lab.

Rubrik:

- Source/destination/protocol/port ditulis eksplisit.
- NAT dibedakan dari firewall dan authentication.
- Pengujian mencakup aliran sah, bukan hanya penolakan.

Referensi:

- [OWASP network segmentation](https://cheatsheetseries.owasp.org/cheatsheets/Network_Segmentation_Cheat_Sheet.html)
- [RFC 5452 DNS resilience](https://www.rfc-editor.org/rfc/rfc5452.html)
- [RFC 9525 TLS identity](https://www.rfc-editor.org/rfc/rfc9525.html)

## 06. Keamanan aplikasi web & secure coding

Menengah · Estimasi 60 menit

Prasyarat: 03_http_browser, 04_crypto_password

Tujuan:

- Membedakan injection, XSS, CSRF, dan broken access control.
- Menentukan kontrol pada titik interpretasi data.
- Melakukan regression test terhadap payload dan input normal.

Lab: 01, 02, 03, 04, 05, 06, 07, 11, 12

**Tugas:** Pilih satu lab injection dan satu lab authorization. Susun laporan singkat berisi source→sink, bukti dampak, perbaikan kode, serta hasil normal/serangan setelah perbaikan.

Rubrik:

- Source dan sink ditunjukkan dengan file/baris kode.
- Dampak ditunjukkan lewat data dummy yang terakses/berubah.
- Kontrol yang dipilih sesuai konteks sink.

Referensi:

- [SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [XSS prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

## 07. Identitas, sesi & keamanan API

Menengah · Estimasi 60 menit

Prasyarat: 03_http_browser, 04_crypto_password

Tujuan:

- Membedakan authentication, authorization, dan accounting.
- Merancang pembatasan percobaan login.
- Mencegah perubahan properti sensitif melalui API.

Lab: 09, 32

**Tugas:** Uji perubahan bio yang sah lalu kirim role=admin. Catat nilai database sebelum/sesudah. Rancang matriks izin untuk pengguna, pemilik objek, dan admin.

Rubrik:

- Update sah tetap berhasil.
- Field sensitif ditolak sebelum mutasi.
- Matriks membedakan identitas dan kepemilikan.

Referensi:

- [Mass assignment](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## 08. Membaca paket & log

Menengah · Estimasi 60 menit

Prasyarat: 02_tcpip_subnet, 05_network_controls

Tujuan:

- Mengenali handshake dan SYN tanpa balasan.
- Membaca PCAP dengan filter yang tepat.
- Menyusun timeline dan mencatat batas bukti.

Lab: 27

**Tugas:** Unduh ketiga PCAP, buka di Wireshark, dan tulis tabel jumlah SYN, pasangan koneksi, serta dugaan aktivitas. Sertakan satu penjelasan alternatif untuk capture tidak lengkap.

Rubrik:

- Handshake dijelaskan dengan urutan flags.
- Scan dibedakan dari SYN normal.
- Batas observasi dan hash berkas dicatat.

Referensi:

- [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/ChapterWork.html)
- [TCP](https://www.rfc-editor.org/rfc/rfc9293.html)

## 09. AppSec lanjutan: trust & concurrency

Lanjutan · Estimasi 90 menit

Prasyarat: 06_web_defense, 07_identity_api

Tujuan:

- Memvalidasi token dan kebijakan browser.
- Membedakan race condition dari replay.
- Menjelaskan parser HTTP yang tidak sepakat.

Lab: 08, 13, 31, 33, 34, 35, 36

**Tugas:** Reproduksi saldo negatif lalu perbaikan atomik. Uji retry pembayaran dengan key sama, kemudian ubah nominal. Buat tabel hasil dan jelaskan mengapa kedua kontrol diperlukan.

Rubrik:

- Bukti transaksi bersamaan dan saldo tercatat.
- Replay tidak membuat efek samping baru.
- Batas CORS, JWT, dan parser dijelaskan tanpa menyamakan kontrol.

Referensi:

- [JWT best practices](https://www.rfc-editor.org/rfc/rfc8725.html)
- [HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112.html)
- [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)

## 10. Detection engineering & SIEM

Lanjutan · Estimasi 90 menit

Prasyarat: 08_packet_logs, 07_identity_api

Tujuan:

- Menghitung precision dan recall.
- Menguji window dan urutan event.
- Membedakan sinyal DNS mencurigakan dari bukti eksfiltrasi.

Lab: 28, 29, 37

**Tugas:** Bandingkan threshold IDS 3, 4, dan 6; catat TP/FP/FN. Lalu ubah window SIEM dan jelaskan event yang keluar dari rangkaian. Pilih konfigurasi dengan alasan operasional.

Rubrik:

- Metrik dihitung dengan benar.
- False positive dan false negative dibahas.
- Satu perbaikan rule disertai uji regresi.

Referensi:

- [Suricata thresholding](https://docs.suricata.io/en/latest/rules/thresholding.html)
- [Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

## 11. Incident response & bukti

Lanjutan · Estimasi 90 menit

Prasyarat: 10_detection_engineering

Tujuan:

- Membedakan triage, containment, eradication, dan recovery.
- Menjaga integritas serta riwayat penanganan bukti.
- Menentukan validasi sebelum layanan dipulihkan.

Lab: 30

**Tugas:** Buat timeline dari evidence.json, jalankan urutan respons lengkap, lalu tulis rencana recovery dengan tiga pemeriksaan terukur dan satu ketidakpastian investigasi.

Rubrik:

- Evidence ID dan hash dicatat.
- Fakta dibedakan dari hipotesis.
- Pemulihan mencakup validasi kontrol dan fungsi.

Referensi:

- [NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)

## 12. Arsitektur, supply chain & capstone

Lanjutan · Estimasi 90 menit

Prasyarat: 09_advanced_appsec, 11_incident_response

Tujuan:

- Memetakan aset, aliran data, dan trust boundary.
- Menjelaskan sumber kepercayaan artefak.
- Menyusun laporan berbukti dan prioritas perbaikan.

Lab: 38, 39, 40

**Tugas:** Selesaikan capstone tanpa mengisi contoh lengkap dahulu. Ekspor laporan belajar dan lampirkan laporan investigasi berisi timeline, evidence ID, prioritas kontrol, pemilik tindakan, serta hasil uji ulang.

Rubrik:

- Klaim merujuk bukti yang tersedia.
- Kontrol sesuai jalur serangan dan memiliki prioritas.
- Batas bukti dan rencana validasi dijelaskan.

Referensi:

- [Threat modeling](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [SLSA](https://slsa.dev/spec/v1.1/)
- [NICE Framework](https://csrc.nist.gov/pubs/sp/800/181/r1/final)
