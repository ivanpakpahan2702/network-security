"""Kurikulum berbahasa Indonesia. Jawaban kuis dinilai server, tidak disisipkan ke form."""
OWASP = "https://cheatsheetseries.owasp.org/cheatsheets/"
RFC = "https://www.rfc-editor.org/rfc/"
IR = "https://csrc.nist.gov/pubs/sp/800/61/r3/final"


def q(question, options, answer, explanation):
    return dict(question=question, options=options, answer=answer, explanation=explanation)


def section(title, paragraphs, example=""):
    return dict(title=title, paragraphs=paragraphs, example=example)


def module(slug, title, level, summary, prerequisites, labs, objectives, sections, questions, assignment, rubric, references):
    return dict(id=slug, title=title, level=level, summary=summary, prerequisites=prerequisites,
                lab_numbers=labs, objectives=objectives, sections=sections, questions=questions,
                assignment=assignment, rubric=rubric, references=references)


MODULES = [
    module("01_security_foundations", "Cara berpikir keamanan & dasar sistem", "Dasar",
        "Mulai dari aset, proses, izin, ancaman, dan cara membuktikan temuan.", [], [19],
        ["Membedakan aset, threat, vulnerability, impact, dan risk.", "Membaca izin file dan memahami identitas service.", "Menyusun catatan eksperimen yang dapat diulang."],
        [section("Keamanan adalah pengelolaan risiko", [
            "Confidentiality membatasi siapa yang dapat membaca data; integrity menjaga perubahan tetap sah; availability menjaga layanan tetap tersedia. Satu kontrol bisa membantu lebih dari satu tujuan, tetapi tidak menyelesaikan semuanya. Backup membantu pemulihan, sementara otorisasi mencegah pembacaan oleh pihak yang salah.",
            "Aset adalah sesuatu yang bernilai, seperti data peserta atau layanan login. Ancaman adalah potensi kejadian yang merugikan. Kerentanan adalah kelemahan yang dapat dimanfaatkan. Risiko menggabungkan kemungkinan dan dampak dalam konteks aset. Error 500 adalah gejala yang perlu dianalisis, bukan otomatis bukti eksploit."],
            "Aset: invoice\nKelemahan: tidak mengecek pemilik\nAncaman: akun lain membaca invoice\nDampak: kerahasiaan data hilang\nKontrol: owner check pada setiap request"),
         section("Proses, user, dan permission", [
            "Program berjalan sebagai proses dengan identitas dan hak tertentu. Hak aplikasi ke file/database harus mengikuti kebutuhan service. Menjalankan semua proses sebagai administrator memperbesar dampak jika aplikasi disalahgunakan.",
            "Pada model rwx Linux, angka read=4, write=2, execute=1 dijumlahkan untuk owner/group/other. Mode 640 berarti owner boleh read/write, group hanya read, dan other tidak mendapat izin. Hak direktori memiliki arti tersendiri: execute berkaitan dengan penelusuran path. Lab menghitung file rwx sederhana; ACL dan kontrol wajib OS merupakan lapisan tambahan."]),
         section("Metode kerja yang dapat direproduksi", [
            "Tentukan ruang lingkup dan akun uji sebelum bekerja. Catat keadaan awal, input normal, satu perubahan input, hasil aktual, dan hasil setelah mitigasi. Pisahkan observasi dari interpretasi: 'HTTP 200 berisi invoice bob' merupakan observasi; dugaan bypass otorisasi perlu dibandingkan dengan identitas sesi dan aturan bisnis.",
            "Gunakan data dummy dalam lab. Perintah diagnosis awal seperti ipconfig dan melihat DevTools Network membantu memahami lingkungan. Mulailah dari inventaris dan konfigurasi sebelum menjalankan alat otomatis; output alat selalu membutuhkan verifikasi."],
            "Catatan eksperimen:\n1. Target/versi/akun uji\n2. Kondisi awal dan kontrol normal\n3. Input perubahan\n4. Bukti respons\n5. Akar masalah dan dampak\n6. Perbaikan serta uji ulang")],
        [q("Kontrol yang paling langsung mencegah alice membaca invoice bob adalah…", ["Backup harian", "Pemeriksaan pemilik pada setiap akses objek", "Mengganti nama tombol"], 1, "Otorisasi harus menegakkan hak akses pada objek yang diminta; backup tidak mencegah pembacaan."),
         q("Mode file 640 memberi izin write kepada…", ["Owner", "Semua anggota group", "Other"], 0, "Digit owner 6 adalah read+write; digit group 4 hanya read; digit other 0 tidak memberi akses."),
         q("Sebuah HTTP 500 tanpa bukti tambahan paling tepat disebut…", ["Bukti pasti SQL injection", "Bukti pengambilalihan server", "Gejala error yang harus diperiksa"], 2, "Status error tidak menjelaskan penyebab maupun dampak keamanan dengan sendirinya."),
         q("Mengapa perlu input normal sebelum mencoba payload?", ["Untuk mengurangi jumlah tabel", "Untuk mendapatkan pembanding perilaku sah", "Agar payload selalu berhasil"], 1, "Pembanding membantu membedakan celah keamanan dari fitur yang memang tidak bekerja.")],
        "Buat inventaris tiga aset lab, identitas proses yang mengaksesnya, dan risiko jika hak akses terlalu luas. Uji owner/group/other di lab permission.",
        ["Setiap aset memiliki pemilik dan dampak yang jelas.", "Catatan membedakan bukti dari dugaan.", "Perbaikan diuji dengan operasi sah dan operasi terlarang."],
        [("NIST NICE Framework", "https://csrc.nist.gov/pubs/sp/800/181/r1/final"), ("GNU file permissions", "https://www.gnu.org/software/coreutils/manual/html_node/Mode-Structure.html")]),
    module("02_tcpip_subnet", "TCP/IP, subnet, port & alur paket", "Dasar",
        "Bangun model jaringan sebelum mempelajari serangannya.", ["01_security_foundations"], [15, 16],
        ["Menghitung subnet dari prefix CIDR.", "Membedakan MAC, IP, port, switch, router, dan gateway.", "Menjelaskan handshake serta perbedaan TCP dan UDP."],
        [section("Perjalanan data melalui lapisan", [
            "Aplikasi menghasilkan data, transport menambahkan informasi port, IP memberi alamat antarjaringan, lalu link layer membungkusnya dalam frame. Nama model OSI membantu diskusi, tetapi diagnosis perlu melihat paket dan konfigurasi nyata. Port mengidentifikasi endpoint transport dalam sebuah host; nomor port lazim tidak membuktikan aplikasi yang benar-benar berjalan.",
            "Switch menghubungkan perangkat dalam segmen layer 2 berdasarkan MAC. Router meneruskan paket antarjaringan berdasarkan IP dan tabel route. Jika tujuan berada di luar subnet, host biasanya mengirim frame kepada MAC gateway, sementara alamat IP tujuan tetap alamat tujuan akhir, kecuali ada translasi seperti NAT."],
            "Browser → TCP dst port 443 → IP server → frame ke MAC gateway\nIP tujuan tetap server; MAC tujuan pada hop pertama bisa gateway."),
         section("CIDR dan rentang alamat", [
            "Prefix /25 menyisakan tujuh bit host sehingga terdapat 128 alamat dalam satu blok. Untuk subnet IPv4 biasa, alamat network dan broadcast tidak dipakai sebagai host. Prefix /31 untuk link point-to-point dan /32 untuk satu alamat adalah pengecualian yang penting.",
            "192.168.10.10/25 berada dalam 192.168.10.0–127. Alamat 192.168.10.200 berada pada blok lain walaupun tiga oktet awalnya sama. Jangan menyamakan 'IP privat' dengan 'satu subnet' atau 'otomatis dipercaya'. Hak akses masih ditentukan oleh kebijakan jaringan dan aplikasi."]),
         section("Transport dan state", [
            "TCP membangun state, memberi sequence number, acknowledgement, retransmission, serta kontrol aliran. Three-way handshake yang lazim adalah SYN, SYN-ACK, ACK. UDP mengirim datagram tanpa handshake TCP; aplikasi di atasnya tetap bisa membangun mekanisme reliabilitas sendiri.",
            "Handshake tidak mengenkripsi data dan tidak membuktikan identitas pengguna. SYN tanpa balasan dapat disebabkan firewall, host mati, packet loss, atau aktivitas mencurigakan. Kesimpulan perlu konteks; satu paket tidak cukup untuk mendiagnosis seluruh kejadian."],
            "Klien → Server: SYN\nServer → Klien: SYN, ACK\nKlien → Server: ACK\nLalu aplikasi bertukar data")],
        [q("192.168.10.10/25 dan 192.168.10.200 berada…", ["Dalam subnet yang sama", "Di subnet berbeda", "Tidak dapat direpresentasikan IPv4"], 1, "Blok pertama /25 berakhir pada .127; .200 berada dalam blok .128/25."),
         q("Saat tujuan berada di luar subnet, MAC tujuan frame pertama biasanya adalah…", ["MAC gateway lokal", "Selalu MAC server jauh", "Alamat DNS"], 0, "ARP menyelesaikan MAC next hop lokal; paket IP tetap menargetkan server jauh."),
         q("Apa yang dijamin handshake TCP?", ["Pengguna pasti sah", "Isi data terenkripsi", "Terbentuknya state transport sesuai protokol"], 2, "Autentikasi pengguna dan enkripsi adalah tugas protokol/lapisan lain."),
         q("Port 443 yang terbuka membuktikan…", ["Server pasti aman", "Endpoint transport menerima koneksi; aplikasi masih perlu diidentifikasi", "Semua pengguna boleh mengakses data"], 1, "Reachability, identitas aplikasi, dan otorisasi adalah pertanyaan berbeda.")],
        "Bagi jaringan 192.168.10.0/24 menjadi dua /25. Tulis rentang host, lalu jelaskan jalur paket dari .10 menuju .200. Rekonstruksi satu handshake dari urutan segmen.",
        ["Network dan broadcast dihitung dengan benar.", "IP tujuan dibedakan dari MAC next hop.", "Handshake tidak disamakan dengan enkripsi/autentikasi."],
        [("RFC 4632 CIDR", RFC + "rfc4632.html"), ("RFC 9293 TCP", RFC + "rfc9293.html")]),
    module("03_http_browser", "HTTP, browser, cookie & sesi", "Dasar",
        "Pahami request yang dikirim browser dan state yang dipelihara aplikasi.", ["01_security_foundations", "02_tcpip_subnet"], [18],
        ["Membedah request/response HTTP.", "Membedakan authentication, authorization, cookie, dan session.", "Memahami origin, site, serta batas perlindungan HTTPS."],
        [section("Request dan response", [
            "Request terdiri dari method, target, versi protokol, header, dan body opsional. Response membawa status, header, dan body. GET biasanya mengambil representasi; POST digunakan untuk mengirim data atau operasi yang mengubah state. Method saja tidak memberi otorisasi dan tidak menggantikan validasi server.",
            "Content-Type menjelaskan format, sedangkan Content-Length/Transfer-Encoding membantu menentukan framing HTTP/1.1. JSON valid secara sintaks tetap bisa melanggar aturan bisnis. Di DevTools Network, bandingkan URL, method, status, header, dan payload untuk memahami apa yang benar-benar dikirim."],
            "POST /profile HTTP/1.1\nHost: portal.lab.test\nContent-Type: application/json\n\n{\"display_name\":\"Alice\"}"),
         section("Cookie, session, dan identitas", [
            "Cookie adalah data yang disimpan browser dan dikirim menurut aturan domain/path/SameSite/Secure. Aplikasi bisa memakai cookie untuk membawa ID sesi atau data sesi bertanda tangan. HttpOnly menghalangi pembacaan cookie melalui JavaScript, tetapi tidak menghentikan browser mengirim cookie pada request.",
            "Authentication menjawab siapa pengguna; authorization menentukan tindakan/objek yang boleh diakses. Server harus mengambil identitas dari mekanisme sesi yang terverifikasi, bukan mempercayai field user_id atau role dari form. Logout, rotasi sesi, timeout, dan pencabutan kredensial juga bagian dari lifecycle identitas."]),
         section("Origin, site, dan HTTPS", [
            "Origin adalah gabungan scheme, host, dan port. Dua halaman pada IP sama tetapi port 5100 dan 5104 berbeda origin. Site untuk SameSite memiliki aturan berbeda dan tidak ditentukan hanya oleh port. Karena itu cookie dapat ikut terkirim pada request lintas origin yang masih same-site seperti dalam lab ini.",
            "HTTPS memberi perlindungan transport dan verifikasi identitas server jika validasi sertifikat dilakukan benar. HTTPS tidak memperbaiki SQL injection, IDOR, maupun log yang membocorkan Authorization. Kebijakan browser seperti CORS juga tidak menggantikan autentikasi dan otorisasi server."])],
        [q("Dua URL dengan host sama tetapi port berbeda…", ["Selalu same-origin", "Berbeda origin", "Tidak bisa berbagi cookie dalam kondisi apa pun"], 1, "Port adalah bagian dari origin. Cakupan cookie tidak menggunakan port sebagai pembatas."),
         q("HttpOnly terutama mencegah…", ["Browser mengirim cookie", "Server membaca cookie", "JavaScript membaca cookie melalui document.cookie"], 2, "HttpOnly tidak otomatis mencegah CSRF karena browser masih dapat melampirkan cookie."),
         q("JSON berisi role=admin dari form harus…", ["Diperiksa izin field dan identitas pengguna oleh server", "Dipercaya karena JSON valid", "Dipercaya jika memakai HTTPS"], 0, "Format valid dan transport aman tidak memberi pengguna hak mengubah atribut internal."),
         q("Yang sebaiknya tidak disalin mentah ke log adalah…", ["Status response", "Authorization dan session cookie", "Nama route yang sudah dinormalisasi"], 1, "Kredensial dalam log memperluas tempat dan orang yang dapat mengaksesnya.")],
        "Amati satu form lab melalui DevTools Network. Tulis method, origin, cookie yang terlibat, dan bagian request yang perlu direduksi dari log.",
        ["Origin dihitung dengan scheme/host/port.", "Sesi dibedakan dari hak akses objek.", "Catatan log tidak menyertakan kredensial mentah."],
        [("RFC 9110 HTTP semantics", RFC + "rfc9110.html"), ("Flask security", "https://flask.palletsprojects.com/en/stable/web-security/")]),
    module("04_crypto_password", "Kriptografi dasar & keamanan password", "Dasar",
        "Pilih alat yang tepat untuk representasi, integritas, kerahasiaan, dan penyimpanan password.", ["03_http_browser"], [10, 20],
        ["Membedakan encoding, hashing, MAC, signature, dan encryption.", "Menjelaskan salt serta biaya KDF password.", "Menghindari kesimpulan salah dari hasil cracking dummy."],
        [section("Tujuan yang berbeda membutuhkan primitive berbeda", [
            "Base64 adalah encoding yang mudah dibalik tanpa secret. Hash seperti SHA-256 menghasilkan digest untuk membandingkan byte terhadap nilai acuan. HMAC menambahkan key bersama untuk autentikasi pesan. Digital signature memakai pasangan kunci sehingga verifier tidak harus memiliki secret penanda tangan.",
            "Enkripsi bertujuan menjaga kerahasiaan; skema modern yang sesuai seperti AEAD juga memverifikasi integritas. Jangan merancang algoritma sendiri atau menganggap 'sudah di-Base64' berarti terenkripsi. Keamanan juga bergantung pada penyimpanan key, nonce, distribusi trust, dan rotasi, bukan hanya nama algoritmanya."],
            "Encoding: dapat dibaca kembali tanpa secret\nHash: bandingkan digest dengan acuan tepercaya\nHMAC: integritas dengan shared secret\nEncryption: kerahasiaan; gunakan skema terautentikasi"),
         section("Password memerlukan fungsi yang sengaja mahal", [
            "Password sering memiliki entropy lebih rendah daripada key acak. MD5/SHA biasa dapat diuji sangat cepat sehingga tidak cocok sebagai penyimpan password. Password KDF seperti Argon2id atau scrypt menambahkan biaya komputasi/memori untuk setiap tebakan.",
            "Salt unik membuat password sama menghasilkan hash berbeda dan menghalangi pemanfaatan tabel precomputed yang sama untuk banyak akun. Salt biasanya disimpan bersama hash dan tidak harus rahasia. Parameter KDF perlu ditinjau sesuai perangkat, risiko, dan kemampuan layanan; terlalu berat juga dapat mengganggu availability."]),
         section("Membaca hasil uji dengan benar", [
            "Dalam lab, password yang benar sengaja ada dalam daftar kandidat. Scrypt tetap dapat menemukannya. Perbaikannya terlihat pada biaya setiap verifikasi dan perbedaan salt, bukan pada klaim bahwa password menjadi mustahil ditebak.",
            "Serangan offline memakai hash yang sudah didapat, sedangkan serangan online menguji endpoint login. Throttling dan MFA membantu pada jalur online tetapi tidak memperlambat pemeriksaan hash yang sudah dicuri. Keduanya perlu dipertimbangkan bersama dengan kekuatan password dan keamanan storage."])],
        [q("Base64 memberikan…", ["Representasi yang dapat dibalik tanpa key", "Kerahasiaan setara TLS", "Verifikasi identitas pengirim"], 0, "Base64 bukan enkripsi dan tidak menyediakan autentikasi pesan."),
         q("Salt unik terutama membantu…", ["Membuat password lemah tidak bisa ditebak", "Membedakan hash password sama dan membatasi precomputation", "Menyembunyikan username"], 1, "Salt tidak menggantikan password kuat atau biaya KDF."),
         q("Untuk memverifikasi integritas pesan dengan shared secret, gunakan…", ["Base64", "MD5 tanpa key", "HMAC"], 2, "HMAC mengikat pesan pada key bersama; verifier harus melindungi key tersebut."),
         q("Throttling endpoint login langsung membatasi…", ["Semua cracking offline", "Percobaan online ke endpoint tersebut", "Kemampuan membaca file backup hash"], 1, "Setelah hash dicuri, attacker dapat menguji kandidat tanpa menghubungi endpoint login.")],
        "Bandingkan dua akun dengan password sama pada MD5 dan scrypt. Catat waktu uji, perbedaan digest, dan perubahan satu byte pada pesan HMAC.",
        ["Salt tidak disamakan dengan encryption key.", "Kesimpulan tidak menyebut scrypt mustahil ditebak.", "Perubahan pesan terdeteksi tanpa mengandalkan encoding."],
        [("OWASP password storage", OWASP + "Password_Storage_Cheat_Sheet.html"), ("RFC 2104 HMAC", RFC + "rfc2104.html")]),
    module("05_network_controls", "Keamanan infrastruktur jaringan", "Menengah",
        "Hubungkan DNS, ARP, DHCP, routing, VLAN, NAT, TLS, dan kebijakan akses.", ["02_tcpip_subnet", "04_crypto_password"], [14, 17, 21, 22, 23, 24, 25, 26],
        ["Menjelaskan trust boundary pada layer 2 hingga aplikasi.", "Membedakan routing, translasi, filtering, dan enkripsi.", "Menguji aliran sah setelah menerapkan pembatasan."],
        [section("Layanan dasar juga memerlukan trust", [
            "ARP memetakan IP ke MAC dalam segmen lokal, DHCP menyediakan konfigurasi host, dan DNS memetakan nama ke record. Jika sumber data yang salah dipercaya, trafik dapat diarahkan ke tujuan yang salah walaupun aplikasi tidak memiliki bug input.",
            "DHCP snooping membedakan port trusted/untrusted untuk pesan server. Dynamic ARP Inspection memakai binding agar klaim IP/MAC tidak diterima sembarang. Untuk DNS, cocokkan respons dengan query yang outstanding; DNSSEC menambahkan autentikasi data melalui signature dan chain of trust, bukan enkripsi query. Demo DNS lab hanya memodelkan pemeriksaan transaksi, bukan implementasi DNSSEC."]),
         section("Routing dan segmentasi", [
            "Longest prefix match memilih route yang paling spesifik. Setelah route dipilih, ACL/firewall tetap dapat menolak aliran. Return path juga harus tersedia. Pada VLAN, identitas segmen seharusnya ditentukan oleh konfigurasi port dan trunk yang diizinkan, bukan sekadar tag dari perangkat pengguna.",
            "Default-deny berarti aliran ditolak kecuali ada kebutuhan yang ditetapkan. Dokumentasikan sumber, tujuan, protokol, port, dan alasan bisnis. Memindahkan semua server ke VLAN lain tanpa membatasi inter-VLAN routing belum menghasilkan segmentasi yang efektif."],
            "Guest VLAN20 → Web:443       ALLOW\nGuest VLAN20 → Database:5432 DENY\nWeb → Database:5432          ALLOW sesuai kebutuhan\nAdmin → Management:22        ALLOW dari jalur admin"),
         section("NAT, state, dan TLS", [
            "NAT menerjemahkan alamat atau port. Stateful firewall melacak koneksi dan mengevaluasi paket terhadap kebijakan/state. Terlihatnya port mapping tidak memberi semua sumber hak untuk mengirim paket melaluinya. Model lab memeriksa tuple sederhana; firewall nyata juga menangani timeout dan rincian protokol.",
            "TLS melindungi komunikasi ketika identitas server diverifikasi. Mematikan verifikasi sertifikat untuk mengatasi error dapat membuat aplikasi berkomunikasi aman secara enkripsi dengan pihak yang salah. Periksa hostname, validity, chain, trust store, dan kebijakan sertifikat yang sesuai."]),
         section("Validasi perubahan jaringan", [
            "Mulai dari matriks aliran sebelum/sesudah. Buktikan aliran berisiko diblokir dan aliran sah tetap bekerja. Gunakan log rule hit serta bukti request untuk membedakan masalah routing dari filtering atau authentication.",
            "Lab ARP/DHCP/VLAN/NAT memakai topologi virtual sehingga pengujian tidak mengubah switch atau router Anda. Tujuannya membangun kemampuan membaca keputusan kontrol; penerapan pada perangkat nyata harus mengikuti dokumentasi vendor, topologi, dan rencana pemulihan konfigurasi."])],
        [q("Default route /0 dan route /24 sama-sama cocok. Yang dipilih biasanya…", ["Yang tercantum pertama", "Route /24", "Keduanya selalu dibuang"], 1, "Longest prefix match memilih prefix yang paling spesifik."),
         q("Port klien menerima DHCP offer dari perangkat tamu. Kontrol yang relevan adalah…", ["DHCP snooping dengan trusted port yang tepat", "Base64 pada gateway", "Mengganti nomor port HTTP"], 0, "Snooping dapat menolak pesan server dari port yang tidak dipercaya."),
         q("Apa yang TIDAK otomatis diberikan oleh NAT?", ["Translasi alamat/port sesuai konfigurasi", "Pemetaan tuple", "Autentikasi pengguna aplikasi"], 2, "NAT bukan mekanisme identitas pengguna atau pengganti otorisasi."),
         q("Koneksi TLS dengan verify=False berarti…", ["Identitas server pasti valid", "Verifikasi identitas dapat dilewati walaupun trafik terenkripsi", "Celah aplikasi seperti IDOR ikut tertutup"], 1, "Enkripsi tanpa verifikasi identitas tidak menjamin endpoint yang dihubungi benar.")],
        "Gambar guest, web, database, dan admin sebagai empat zona. Buat matriks minimal enam aliran, pilih kontrol di titik yang tepat, lalu buktikan tiga allow dan tiga deny dalam lab.",
        ["Source/destination/protocol/port ditulis eksplisit.", "NAT dibedakan dari firewall dan authentication.", "Pengujian mencakup aliran sah, bukan hanya penolakan."],
        [("OWASP network segmentation", OWASP + "Network_Segmentation_Cheat_Sheet.html"), ("RFC 5452 DNS resilience", RFC + "rfc5452.html"), ("RFC 9525 TLS identity", RFC + "rfc9525.html")]),
    module("06_web_defense", "Keamanan aplikasi web & secure coding", "Menengah",
        "Telusuri aliran input hingga interpreter, browser, file, dan objek data.", ["03_http_browser", "04_crypto_password"], [1, 2, 3, 4, 5, 6, 7, 11, 12],
        ["Membedakan injection, XSS, CSRF, dan broken access control.", "Menentukan kontrol pada titik interpretasi data.", "Melakukan regression test terhadap payload dan input normal."],
        [section("Ikuti input ke sink", [
            "Source adalah tempat data masuk, seperti parameter URL, JSON, upload, atau database yang sebelumnya menerima input pengguna. Sink adalah tempat data mendapat arti, seperti SQL parser, HTML renderer, shell, atau filesystem path. Data yang sudah disimpan di database tetap dapat berbahaya saat digunakan kemudian.",
            "SQL parameter binding memisahkan struktur query dari nilai. Escaping output HTML menangani konteks browser; validasi path canonical membatasi file; allowlist tujuan membatasi redirect. Satu fungsi 'sanitize semua input' tidak dapat menggantikan kontrol yang sesuai untuk sink yang berbeda."]),
         section("XSS dan CSRF berbeda", [
            "Reflected XSS kembali melalui respons langsung; stored XSS disimpan lalu dieksekusi pada kunjungan berikutnya. Pertahanan utamanya encoding sesuai konteks output, atau sanitization terawat ketika HTML pengguna memang diizinkan. CSP merupakan lapisan tambahan, bukan pengganti perbaikan rendering.",
            "CSRF memanfaatkan request browser yang membawa kredensial korban, tanpa harus mengeksekusi script di origin bank. Token anti-CSRF yang terikat sesi dan pemeriksaan Origin membantu memastikan perubahan state berasal dari alur yang sah. SameSite adalah lapisan tambahan dengan aturan site yang perlu dipahami."]),
         section("Otorisasi dan file", [
            "Pada IDOR, mengganti invoice_id dapat membuka objek orang lain jika server tidak memeriksa owner. Menggunakan UUID dapat membuat penebakan lebih sulit tetapi tidak mengganti otorisasi. Query harus dibatasi dengan identitas yang berasal dari sesi server.",
            "Upload perlu pembatasan format/ukuran, nama internal yang terkendali, penyimpanan yang sesuai, dan cara penyajian aman. File HTML dapat menjalankan script di browser walaupun tidak dieksekusi sebagai kode server. Path traversal harus diuji pada path final setelah normalisasi, bukan hanya dengan menghapus substring '../'."],
            "SELECT id, body FROM invoices WHERE id = ? AND owner = ?\n# id dari request; owner dari sesi yang sudah diverifikasi"),
         section("Buktikan perbaikan", [
            "Uji payload yang diketahui, variasi encoding yang relevan, objek milik sendiri/orang lain, dan input normal. Jangan menganggap respons 403 selalu cukup: periksa apakah mutasi sudah terjadi sebelum penolakan atau data bocor pada pesan error.",
            "Catat lokasi kode, input pemicu, bukti dampak, perubahan perbaikan, dan hasil uji ulang. Command injection dalam kumpulan ini memakai emulator terbatas; prinsip utama tetap menghindari shell dan memisahkan argumen dari sintaks."])],
        [q("Pertahanan SQL injection yang utama untuk nilai input adalah…", ["Parameter binding", "Mengubah input menjadi huruf kecil", "Menghapus semua spasi"], 0, "Parameter binding menjaga nilai pengguna sebagai data, terpisah dari struktur SQL."),
         q("Menggunakan UUID sebagai invoice ID…", ["Menghilangkan kebutuhan owner check", "Dapat menyulitkan tebakan tetapi tetap membutuhkan otorisasi", "Mencegah semua XSS"], 1, "ID yang sulit ditebak bukan bukti hak mengakses objek."),
         q("Komentar sudah disimpan di database. Saat dirender ia…", ["Pasti aman", "Tidak bisa lagi mengandung script", "Tetap perlu output encoding sesuai konteks"], 2, "Penyimpanan tidak mengubah tingkat kepercayaan input; stored XSS terjadi saat output."),
         q("Perbaikan yang baik harus diuji terhadap…", ["Payload serangan saja", "Payload dan operasi sah", "Tampilan warna tombol saja"], 1, "Kontrol harus menutup celah sambil menjaga kebutuhan bisnis yang sah.")],
        "Pilih satu lab injection dan satu lab authorization. Susun laporan singkat berisi source→sink, bukti dampak, perbaikan kode, serta hasil normal/serangan setelah perbaikan.",
        ["Source dan sink ditunjukkan dengan file/baris kode.", "Dampak ditunjukkan lewat data dummy yang terakses/berubah.", "Kontrol yang dipilih sesuai konteks sink."],
        [("SQL injection prevention", OWASP + "SQL_Injection_Prevention_Cheat_Sheet.html"), ("XSS prevention", OWASP + "Cross_Site_Scripting_Prevention_Cheat_Sheet.html"), ("CSRF prevention", OWASP + "Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html")]),
    module("07_identity_api", "Identitas, sesi & keamanan API", "Menengah",
        "Pisahkan identitas, izin, dan kepemilikan field dalam API.",
        ["03_http_browser", "04_crypto_password"], [9, 32],
        ["Membedakan authentication, authorization, dan accounting.", "Merancang pembatasan percobaan login.", "Mencegah perubahan properti sensitif melalui API."],
        [section("Siklus identitas", [
            "Authentication membuktikan identitas; authorization memeriksa apakah identitas itu boleh melakukan aksi pada objek tertentu. Accounting mencatat apa yang terjadi. Login berhasil tidak otomatis mengizinkan membaca semua invoice atau mengganti role.",
            "Setelah login, rotasi session ID dan beri batas waktu sesi. Logout dan perubahan kredensial perlu mekanisme pencabutan sesi. MFA mengurangi dampak password yang bocor, tetapi tidak menggantikan otorisasi objek atau perlindungan sesi."]),
         section("Pembatasan percobaan", [
            "Rate limit per akun memperlambat tebakan terdistribusi; limit per sumber membantu menahan satu sumber yang menyerang banyak akun. Kombinasikan keduanya dengan pengamatan risiko, pesan error generik, dan pemulihan akun yang aman.",
            "Lockout permanen dapat dipakai untuk mengunci korban. Gunakan jeda atau window terbatas, dan ukur dampaknya pada pengguna sah. Bandingkan hasil brute-force lab dengan password security: pertahanan online berbeda dari KDF yang memperlambat tebakan offline."]),
         section("Kontrak API dan field milik server", [
            "API update profil boleh menerima display_name dan bio. Role, saldo, owner, serta status verifikasi ditentukan server. Menyalin seluruh JSON ke model database membuat penyerang ikut mengubah field yang tidak ditampilkan di form.",
            "Gunakan schema dengan allowlist field, tipe dan panjang nilai. Tetap periksa izin objek setelah validasi schema. Tambahkan batas ukuran request, pagination, dan kuota operasi mahal; JSON valid belum tentu murah atau berwenang."])],
        [q("Login berhasil membuktikan…", ["Hak atas semua objek", "Identitas sesuai mekanisme login", "Semua field JSON aman"], 1, "Hak per objek dan aksi masih harus diperiksa."),
         q("Field role pada update profil umum sebaiknya…", ["Dipercaya dari browser", "Dihapus hanya dari HTML", "Ditolak oleh schema server"], 2, "Penyerang dapat mengirim request tanpa memakai form."),
         q("Lockout permanen tanpa pemulihan berisiko…", ["Dipakai mengunci akun korban", "Menghilangkan SQL injection", "Meningkatkan entropi password"], 0, "Pertahanan login juga harus mempertimbangkan denial of service terhadap akun."),
         q("Rate limit online menggantikan KDF password?", ["Ya", "Tidak; ancaman offline berbeda", "Hanya bila memakai HTTPS"], 1, "Salinan hash dapat ditebak tanpa menghubungi endpoint login.")],
        "Uji perubahan bio yang sah lalu kirim role=admin. Catat nilai database sebelum/sesudah. Rancang matriks izin untuk pengguna, pemilik objek, dan admin.",
        ["Update sah tetap berhasil.", "Field sensitif ditolak sebelum mutasi.", "Matriks membedakan identitas dan kepemilikan."],
        [("Mass assignment", OWASP + "Mass_Assignment_Cheat_Sheet.html"), ("Authentication", OWASP + "Authentication_Cheat_Sheet.html")]),
    module("08_packet_logs", "Membaca paket & log", "Menengah",
        "Ubah paket dan catatan aplikasi menjadi bukti yang dapat diperiksa.",
        ["02_tcpip_subnet", "05_network_controls"], [27],
        ["Mengenali handshake dan SYN tanpa balasan.", "Membaca PCAP dengan filter yang tepat.", "Menyusun timeline dan mencatat batas bukti."],
        [section("Apa yang terlihat dalam capture", [
            "PCAP menyimpan paket, timestamp, dan panjang capture. Ethernet memuat alamat MAC; IPv4 memuat sumber/tujuan; TCP memuat port, sequence, acknowledgment, dan flags. Satu SYN adalah upaya pembukaan koneksi, bukan bukti login berhasil.",
            "Unduh tiga PCAP dari lab 27. normal.pcap berisi SYN, SYN-ACK, ACK; scan.pcap berisi SYN ke beberapa port; incomplete.pcap hanya satu SYN. Berkas sintetis ini memiliki struktur PCAP nyata dan dapat dibuka di Wireshark. Tidak ada capture jaringan pengguna."]),
         section("Filter dan korelasi", [
            "Capture filter menentukan paket yang disimpan; display filter menyaring tampilan paket yang sudah ada. Keduanya mempunyai sintaks berbeda. Di Wireshark gunakan tcp.flags.syn == 1 && tcp.flags.ack == 0 untuk menyorot SYN awal; gunakan tcp.port == 443 untuk kedua arah port HTTPS.",
            "Cocokkan pasangan alamat/port dan arah paket sebelum menyimpulkan handshake. Capture yang tidak lengkap, packet loss, NAT, atau posisi sensor dapat menyembunyikan balasan. Tidak terlihat dalam capture bukan berarti tidak pernah terjadi."],
            "Display filter: ip.addr == 192.0.2.10\nDisplay filter: tcp.flags.syn == 1 && tcp.flags.ack == 0"),
         section("Log yang bisa diinvestigasi", [
            "Log berguna memuat waktu dengan zona, identitas, sumber, aksi, objek, hasil, dan correlation ID. Jangan mencatat password, token sesi, atau isi pribadi tanpa kebutuhan. Sinkronisasi jam dan konversi ke UTC penting saat menggabungkan sumber.",
            "Pisahkan observasi (lima login gagal tercatat), inferensi (mungkin ada tebakan password), dan pertanyaan (apakah pemilik akun mengenali login sukses?). Simpan berkas asli, catat hash dan waktu akuisisi, lalu kerjakan salinan. Hash mendeteksi perubahan, bukan membuktikan kebenaran isi log."])],
        [q("SYN tanpa balasan membuktikan…", ["Server pasti mati", "Hanya SYN terlihat pada capture itu", "Login berhasil"], 1, "Kelengkapan capture dan posisi sensor membatasi kesimpulan."),
         q("Display filter menghapus paket dari berkas asli?", ["Ya", "Hanya UDP", "Tidak, ia menyaring tampilan"], 2, "Penyimpanan hasil terfilter adalah tindakan lain."),
         q("Korelasi paket dua arah memakai…", ["Pasangan IP/port dan arah", "Warna tampilan", "Nama file saja"], 0, "Balasan membalik alamat/port; flag serta sequence membantu validasi lebih lanjut."),
         q("Hash bukti berguna untuk…", ["Membuktikan semua isinya benar", "Mendeteksi perubahan berkas", "Mengganti timestamp"], 1, "Integritas byte berbeda dari autentisitas dan akurasi sumber.")],
        "Unduh ketiga PCAP, buka di Wireshark, dan tulis tabel jumlah SYN, pasangan koneksi, serta dugaan aktivitas. Sertakan satu penjelasan alternatif untuk capture tidak lengkap.",
        ["Handshake dijelaskan dengan urutan flags.", "Scan dibedakan dari SYN normal.", "Batas observasi dan hash berkas dicatat."],
        [("Wireshark User's Guide", "https://www.wireshark.org/docs/wsug_html_chunked/ChapterWork.html"), ("TCP", "https://www.rfc-editor.org/rfc/rfc9293.html")]),
    module("09_advanced_appsec", "AppSec lanjutan: trust & concurrency", "Lanjutan",
        "Pelajari kegagalan kepercayaan lintas komponen dan request bersamaan.",
        ["06_web_defense", "07_identity_api"], [8, 13, 31, 33, 34, 35, 36],
        ["Memvalidasi token dan kebijakan browser.", "Membedakan race condition dari replay.", "Menjelaskan parser HTTP yang tidak sepakat."],
        [section("Token dan asal request", [
            "JWT adalah format claim bertanda tangan atau terenkripsi; base64url bukan enkripsi. Verifikasi signature dengan algoritma yang ditetapkan server, lalu cek issuer, audience, expiry, dan claim yang diperlukan. Membaca payload tanpa verifikasi membuat claim role dapat dipalsukan.",
            "CORS mengatur apakah script origin lain boleh membaca respons. Origin terdiri dari scheme, host, dan port; dua port berbeda adalah dua origin. CORS bukan autentikasi atau pertahanan CSRF. Demo port 5133 menggunakan sesi nyata: origin dashboard dapat membaca data hanya ketika server memantulkan Origin dan mengizinkan credentials."]),
         section("Input yang menyeberangi batas interpreter", [
            "SSRF terjadi ketika input pengguna menentukan tujuan request server. Periksa kebutuhan destination, skema, hasil DNS, redirect, dan egress; allowlist domain saja dapat tidak cukup bila resolver atau redirect mengubah tujuan. Lab membatasi semua request pada layanan dummy lokal.",
            "SSTI menjadikan input sebagai sumber template. Memperbaikinya berarti mempertahankan template tetap dan memasukkan input sebagai data. Sandbox pada demo membatasi dampak eksperimen; ia bukan alasan membiarkan pengguna menulis template produksi tanpa desain khusus."]),
         section("Atomisitas dan idempotensi", [
            "Race condition muncul saat dua request membaca saldo yang sama lalu sama-sama mengurangi saldo. Pengecekan dan mutasi harus atomik: transaksi dengan locking yang sesuai atau UPDATE bersyarat balance >= amount. Lab menggunakan dua thread dan database nyata untuk menunjukkan saldo negatif versus satu transaksi ditolak.",
            "Replay dapat terjadi karena retry jaringan, bukan hanya serangan. Idempotency key mengikat identitas, operasi, parameter, dan hasil; key sama dengan parameter berbeda harus ditolak. Unique constraint serta transaksi mencegah dua request membuat hasil ganda. Idempotensi tidak menggantikan pengecekan saldo atomik."]),
         section("Framing HTTP", [
            "Proxy dan backend harus sepakat di mana sebuah request berakhir. Content-Length dan Transfer-Encoding yang ditafsirkan berbeda dapat menyisakan byte yang dianggap request berikutnya. Lab membandingkan offset parser pada teks terbatas secara offline; tidak memakai proxy rentan sungguhan.",
            "Tolak framing ambigu, header panjang ganda yang tidak konsisten, dan trailing bytes yang tidak diharapkan. Gunakan implementasi protokol terawat dan pengujian end-to-end pada proxy/backend. Hasil satu parser mini tidak membuktikan seluruh stack produksi aman."])],
        [q("JWT dapat dipercaya setelah…", ["Payload berhasil di-decode", "Signature dan claim wajib diverifikasi", "Header berisi HS256"], 1, "Algoritma dari token tidak boleh menentukan kebijakan verifier."),
         q("CORS menolak pembacaan respons berarti request pasti tidak dikirim?", ["Ya", "Hanya saat POST", "Tidak; CORS dan CSRF berbeda"], 2, "Banyak request dapat terkirim walau JavaScript tidak boleh membaca hasilnya."),
         q("Perbaikan saldo bersamaan yang tepat adalah…", ["Check dan update atomik", "Menambah delay browser", "Mengganti warna tombol"], 0, "Atomic conditional update mencegah kedua request mengonsumsi saldo yang sama."),
         q("Idempotency key sama, nominal berbeda sebaiknya…", ["Membuat pembayaran baru diam-diam", "Ditolak sebagai konflik", "Mengubah hasil sebelumnya"], 1, "Key terikat parameter operasi agar replay tidak mengubah maknanya.")],
        "Reproduksi saldo negatif lalu perbaikan atomik. Uji retry pembayaran dengan key sama, kemudian ubah nominal. Buat tabel hasil dan jelaskan mengapa kedua kontrol diperlukan.",
        ["Bukti transaksi bersamaan dan saldo tercatat.", "Replay tidak membuat efek samping baru.", "Batas CORS, JWT, dan parser dijelaskan tanpa menyamakan kontrol."],
        [("JWT best practices", "https://www.rfc-editor.org/rfc/rfc8725.html"), ("HTTP/1.1", "https://www.rfc-editor.org/rfc/rfc9112.html"), ("CORS", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS")]),
    module("10_detection_engineering", "Detection engineering & SIEM", "Lanjutan",
        "Bangun rule dari hipotesis, ukur kesalahan, dan korelasikan bukti.",
        ["08_packet_logs", "07_identity_api"], [28, 29, 37],
        ["Menghitung precision dan recall.", "Menguji window dan urutan event.", "Membedakan sinyal DNS mencurigakan dari bukti eksfiltrasi."],
        [section("Metrik rule", [
            "True positive adalah aktivitas berbahaya yang terdeteksi; false positive adalah aktivitas sah yang ditandai. False negative adalah aktivitas berbahaya yang terlewat. Precision = TP/(TP+FP); recall = TP/(TP+FN). Bila penyebut nol, metrik tidak terdefinisi, bukan otomatis sempurna.",
            "Ground truth pada dataset latihan dipakai setelah deteksi untuk evaluasi, bukan sebagai input rule. Threshold rendah dapat meningkatkan recall sekaligus membebani analis. Threshold tinggi dapat melewatkan serangan lambat. Uji data normal dan serangan serta pisahkan data tuning dari evaluasi."]),
         section("Agregasi dan korelasi", [
            "Port scan lebih masuk akal dideteksi dengan banyak port unik dari satu sumber dalam window, bukan sekadar menghitung seluruh SYN sejak sensor hidup. Tetapkan pengelompokan, ukuran window, duplikasi event, dan keterlambatan log secara eksplisit.",
            "SIEM menghubungkan beberapa sumber: kegagalan login berulang, login sukses, perubahan role, kemudian ekspor data. Kesamaan akun/IP, urutan waktu, dan jarak antarperistiwa memperkuat hipotesis. Log yang terlambat atau jam meleset dapat mengubah hasil korelasi."]),
         section("Pola DNS dan triage", [
            "Label DNS panjang, berentropi tinggi, banyak subdomain unik, dan domain tidak disetujui dapat menjadi sinyal tunneling. CDN serta telemetri sah juga dapat menghasilkan pola serupa. Gabungkan konteks aset, proses pembuat query, volume, dan baseline sebelum menyimpulkan eksfiltrasi.",
            "Lab DNS menggunakan log sintetis dan tidak mengirim query. Hasil rule harus menyertakan event sumber dan alasan, sehingga analis dapat memverifikasi. Dokumentasikan pemilik rule, kebutuhan data, severity, pengecualian, dan test case setiap kali rule diubah."])],
        [q("TP=3 dan FP=1 menghasilkan precision…", ["25%", "75%", "100%"], 1, "3/(3+1)=0,75."),
         q("Ground truth dimasukkan sebagai syarat rule akan…", ["Membuat evaluasi bocor dan tidak realistis", "Selalu meningkatkan generalisasi", "Mengganti kebutuhan log"], 0, "Label evaluasi tidak tersedia seperti itu saat deteksi produksi."),
         q("Label DNS panjang selalu berarti tunneling?", ["Ya", "Hanya pada TCP", "Tidak, perlu konteks dan baseline"], 2, "Layanan sah dapat mempunyai label panjang dan berentropi tinggi."),
         q("Korelasi urutan event membutuhkan…", ["Hanya jumlah total", "Identitas, waktu, dan urutan yang konsisten", "Nama file yang sama"], 1, "Window dan pengelompokan menentukan apakah event termasuk rangkaian yang sama.")],
        "Bandingkan threshold IDS 3, 4, dan 6; catat TP/FP/FN. Lalu ubah window SIEM dan jelaskan event yang keluar dari rangkaian. Pilih konfigurasi dengan alasan operasional.",
        ["Metrik dihitung dengan benar.", "False positive dan false negative dibahas.", "Satu perbaikan rule disertai uji regresi."],
        [("Suricata thresholding", "https://docs.suricata.io/en/latest/rules/thresholding.html"), ("Logging", OWASP + "Logging_Cheat_Sheet.html")]),
    module("11_incident_response", "Incident response & bukti", "Lanjutan",
        "Susun respons yang menjaga bukti dan memulihkan layanan secara terukur.",
        ["10_detection_engineering"], [30],
        ["Membedakan triage, containment, eradication, dan recovery.", "Menjaga integritas serta riwayat penanganan bukti.", "Menentukan validasi sebelum layanan dipulihkan."],
        [section("Persiapan dan keputusan", [
            "Incident response adalah kemampuan organisasi, bukan hanya menjalankan alat. Tetapkan penanggung jawab, jalur eskalasi, inventaris aset, akses log, backup, dan kriteria insiden sebelum kejadian. NIST SP 800-61r3 menghubungkan respons insiden dengan pengelolaan risiko dan fungsi CSF 2.0.",
            "Triage menguji apakah alert benar, apa cakupannya, dan layanan mana terdampak. Containment membatasi dampak lanjutan; eradication menangani penyebab serta persistence; recovery mengembalikan layanan dengan validasi. Kegiatan dapat berulang ketika bukti baru muncul."]),
         section("Bukti dan urutan tindakan", [
            "Catat siapa mengambil bukti, kapan, dari mana, metode, hash, lokasi penyimpanan, serta setiap perpindahan. Gunakan salinan untuk analisis. Menyalakan ulang atau menghapus mesin dapat menghilangkan bukti volatile; membiarkan koneksi aktif juga dapat memperbesar dampak.",
            "Urutan lab isolate, preserve, rotate, recover, validate adalah latihan untuk skenario yang diberikan, bukan aturan universal. Pada insiden nyata, pengambilan memori, kebutuhan keselamatan, dan keputusan containment bergantung konteks serta kewenangan. Lab hanya mengubah status virtual dan tidak menyentuh host."]),
         section("Pemulihan dan pembelajaran", [
            "Rotasi kredensial perlu dilakukan setelah cakupan kompromi dipahami dan dari lingkungan tepercaya. Recovery mencakup perbaikan celah, pemulihan dari sumber bersih, verifikasi konfigurasi, dan pengujian layanan. Memulihkan backup tanpa menutup akar masalah dapat mengulang insiden.",
            "Validasi harus memastikan fungsi bisnis berjalan, akses tidak sah ditolak, indikator terkait tidak muncul lagi, dan logging efektif. Laporan memisahkan fakta, inferensi, ketidakpastian, dampak, serta tindakan dengan pemilik/tenggat. Komunikasikan hanya informasi yang dibutuhkan pihak terkait."])],
        [q("Menghapus disk sebelum preservasi dapat…", ["Menghilangkan bukti", "Membuktikan akar masalah", "Mengganti kebutuhan triage"], 0, "Tindakan destruktif mengurangi kesempatan memahami kejadian."),
         q("Hash bukti harus disertai…", ["Warna label", "Asal, waktu, metode, dan riwayat penanganan", "Password pengguna"], 1, "Chain of custody memerlukan konteks dan pencatatan penanganan."),
         q("Recovery dianggap selesai setelah…", ["Server bisa ping saja", "Backup berhasil disalin saja", "Fungsi dan kontrol keamanan tervalidasi"], 2, "Ketersediaan dan penutupan celah harus diuji."),
         q("Urutan tindakan lab berlaku identik untuk semua insiden?", ["Ya", "Tidak, keputusan bergantung konteks", "Hanya untuk Linux"], 1, "Tradeoff bukti, dampak, dan keselamatan memerlukan penilaian kasus.")],
        "Buat timeline dari evidence.json, jalankan urutan respons lengkap, lalu tulis rencana recovery dengan tiga pemeriksaan terukur dan satu ketidakpastian investigasi.",
        ["Evidence ID dan hash dicatat.", "Fakta dibedakan dari hipotesis.", "Pemulihan mencakup validasi kontrol dan fungsi."],
        [("NIST SP 800-61r3", "https://csrc.nist.gov/pubs/sp/800/61/r3/final")]),
    module("12_architecture_capstone", "Arsitektur, supply chain & capstone", "Lanjutan",
        "Gabungkan analisis aplikasi, jaringan, dan respons menjadi laporan akhir.",
        ["09_advanced_appsec", "11_incident_response"], [38, 39, 40],
        ["Memetakan aset, aliran data, dan trust boundary.", "Menjelaskan sumber kepercayaan artefak.", "Menyusun laporan berbukti dan prioritas perbaikan."],
        [section("Threat modeling", [
            "Gambar pengguna, proses, penyimpanan, layanan luar, dan arah aliran data. Tandai batas kepercayaan ketika data atau identitas berpindah komponen. Untuk setiap aliran, tanyakan siapa yang dapat memalsukan identitas, mengubah data, membocorkan informasi, mengganggu layanan, atau menaikkan hak.",
            "Hubungkan ancaman dengan kontrol yang spesifik. TLS melindungi saluran, authorization membatasi objek, segmentasi membatasi jalur, logging membantu deteksi, backup membantu pemulihan. Skor likelihood × impact dalam lab adalah alat prioritas sederhana, bukan skor CVSS atau probabilitas terukur."]),
         section("Kepercayaan pada rantai pasok", [
            "Checksum yang datang bersama unduhan dari sumber yang sama dapat diganti bersama artefaknya. Hash harus dibandingkan dengan nilai yang didapat dari jalur tepercaya; tanda tangan menambah autentikasi jika kunci dan proses verifikasinya dipercaya. Lab membandingkan digest pengguna dengan digest yang dipin di server.",
            "Inventaris dependensi dan SBOM membantu mengetahui komponen yang dipakai, tetapi tidak menjamin bebas celah. Lockfile, verifikasi asal build, pembatasan hak CI, tinjauan perubahan, dan pembaruan yang diuji mengurangi risiko berbeda. SLSA membahas provenance serta jaminan rantai pasok build."]),
         section("Kasus akhir", [
            "Baca bukti E01–E05 sebelum mengisi laporan lab 40. Ada informasi inventaris, kegagalan dan keberhasilan login, akses invoice milik orang lain, serta ekspor ke tujuan yang tidak disetujui. Jelaskan hubungan antarperistiwa dan mana kesimpulan yang masih membutuhkan bukti tambahan.",
            "Laporan yang dapat ditindaklanjuti memuat ringkasan, aset dan identitas, evidence ID, akar masalah, dampak, containment, perbaikan, dan uji ulang. Rubrik otomatis hanya memeriksa struktur serta beberapa unsur kasus; kualitas argumentasi tetap perlu tinjauan manusia."]),
         section("Melanjutkan pembelajaran", [
            "Ulangi latihan dengan input yang berbeda dan jelaskan hasil tanpa melihat solusi. Setelah itu berlatih di mesin virtual terisolasi: administrasi Linux, konfigurasi switch/firewall, analisis capture lebih besar, review kode, dan penyusunan detection rule pada data baru.",
            "Lulus kuis bukan bukti siap menangani semua insiden. Gunakan portofolio laporan, pengujian ulang, dan umpan balik mentor untuk mengukur kemampuan. NICE Framework dapat membantu memetakan pengetahuan serta keterampilan ke peran kerja yang ingin diperdalam."])],
        [q("TLS saja mencegah IDOR?", ["Ya", "Tidak, perlu authorization objek", "Hanya di jaringan LAN"], 1, "Enkripsi saluran tidak menentukan siapa berhak membaca objek."),
         q("Checksum dari penyerang bersama file berbahaya…", ["Bukan sumber integritas tepercaya", "Membuktikan file resmi", "Menggantikan verifikasi asal"], 0, "Penyerang dapat menghitung checksum baru untuk byte yang diganti."),
         q("SBOM menjamin tidak ada kerentanan?", ["Ya", "Jika berformat JSON", "Tidak, ia membantu inventaris komponen"], 2, "Inventaris perlu digabung dengan penilaian dan pengelolaan risiko."),
         q("Laporan terbaik menghubungkan…", ["Nama alat saja", "Bukti, dampak, kontrol, dan uji ulang", "Jumlah screenshot saja"], 1, "Klaim perlu bukti dan perbaikan perlu validasi.")],
        "Selesaikan capstone tanpa mengisi contoh lengkap dahulu. Ekspor laporan belajar dan lampirkan laporan investigasi berisi timeline, evidence ID, prioritas kontrol, pemilik tindakan, serta hasil uji ulang.",
        ["Klaim merujuk bukti yang tersedia.", "Kontrol sesuai jalur serangan dan memiliki prioritas.", "Batas bukti dan rencana validasi dijelaskan."],
        [("Threat modeling", OWASP + "Threat_Modeling_Cheat_Sheet.html"), ("SLSA", "https://slsa.dev/spec/v1.1/"), ("NICE Framework", "https://csrc.nist.gov/pubs/sp/800/181/r1/final")]),
]

LEVELS = ("Dasar", "Menengah", "Lanjutan")
for index, item in enumerate(MODULES, 1):
    item["number"] = index
    item["duration"] = {"Dasar": 45, "Menengah": 60, "Lanjutan": 90}[item["level"]]
MODULE_BY_ID = {item["id"]: item for item in MODULES}
LAB_MODULES = {}
for item in MODULES:
    for number in item["lab_numbers"]:
        LAB_MODULES.setdefault(number, []).append(item["id"])
