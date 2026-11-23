"use strict";

const lessonGroups = [
  ["dasar", "Dasar server"],
  ["trafik", "Menangani trafik"],
  ["data", "Data dan operasi"],
  ["praktik", "Praktik infrastruktur"],
];

// Node coordinates are zero-based column and row positions in the diagram.
function node(id, name, role, column, row, description) {
  return { id, name, role, column, row, description };
}

function step(title, description, from, to, detail, { kind = "request", ms = 0, states = {} } = {}) {
  return { title, description, from, to, detail, kind, ms, states };
}

const browser = (column = 0, row = 0) => node(
  "browser", "Browser", "Klien", column, row,
  "Mencari alamat server, membuka koneksi, mengirim request HTTP, dan menampilkan data dari response."
);

const app = (column = 2, row = 0) => node(
  "app", "Aplikasi", "Logika bisnis", column, row,
  "Memilih handler untuk method dan path, menjalankan aturan bisnis, lalu menyusun status, header, dan body respons."
);
const database = (column = 2, row = 1) => node(
  "db", "Database", "Penyimpanan", column, row,
  "Menyimpan data persisten dan mengembalikan hasil query atau konfirmasi transaksi ke aplikasi."
);
const dns = (column = 0, row = 1) => node(
  "dns", "Resolver DNS", "Pencarian alamat", column, row,
  "Mencari jawaban DNS untuk klien dan menyimpan record sampai TTL habis."
);
const proxy = (column = 1, row = 0) => node(
  "proxy", "Reverse proxy", "Pintu masuk HTTP", column, row,
  "Menerima trafik dari klien dan meneruskan request ke layanan yang sesuai. Proxy dapat mengakhiri TLS di sisi publik."
);
const catalogRequest = "GET /api/produk/42 HTTP/1.1\nHost: toko.example\nAccept: application/json";
const catalogResponse = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"id":42,"nama":"Kopi Gayo"}';

const lessons = [
  {
    id: "request-lifecycle",
    group: "dasar",
    title: "Dari request ke response",
    nav: "Siklus request HTTP",
    intro: "Ikuti satu permintaan web dari pencarian alamat hingga respons muncul di browser. Perhatikan bagaimana DNS, reverse proxy, aplikasi, dan database saling terhubung.",
    nodes: [browser(), proxy(), app(), dns(), database()],
    scenarios: [
      {
        id: "sukses", name: "Produk ditemukan · 200 OK",
        steps: [
          step("Browser mencari alamat", "URL berisi nama host toko.example. Browser memerlukan alamat IP sebelum membuka koneksi ke server.", "browser", "dns", "DNS query\nNama: toko.example\nTipe: A", { ms: 5 }),
          step("DNS mengembalikan alamat", "Resolver mengirim record A. Browser sekarang tahu alamat proxy yang melayani nama domain itu.", "dns", "browser", "toko.example. 300 IN A 203.0.113.10", { kind: "response", ms: 7, states: { dns: "TTL 300 dtk" } }),
          step("Koneksi HTTPS dibuka", "Browser membuka TCP ke port 443 lalu melakukan TLS handshake. Contoh ini memakai HTTP/1.1 dan koneksi baru.", "browser", "proxy", "TCP → 203.0.113.10:443\nTLS handshake → koneksi siap", { ms: 24, states: { proxy: "TLS siap" } }),
          step("Request HTTP dikirim", "Browser mengirim method GET, path produk, dan header. Reverse proxy menerima request melalui koneksi yang sudah terenkripsi.", "browser", "proxy", catalogRequest, { ms: 12 }),
          step("Proxy meneruskan request", "Proxy membaca host dan path, lalu meneruskan request ke layanan katalog. Aplikasi memilih handler untuk GET /api/produk/42.", "proxy", "app", "Host toko.example + /api/produk/*\nUpstream: katalog:8000", { ms: 4 }),
          step("Aplikasi meminta data", "Handler membaca produk dengan ID 42 dari database. Parameter ID dikirim terpisah dari teks query.", "app", "db", "SELECT id, nama FROM produk WHERE id = ?\nParameter: [42]", { ms: 3 }),
          step("Database mengembalikan baris", "Aplikasi menerima satu baris dan mengubahnya menjadi representasi JSON.", "db", "app", '{ "id": 42, "nama": "Kopi Gayo" }', { kind: "response", ms: 8 }),
          step("Aplikasi menyiapkan response", "Status 200 menandakan permintaan berhasil. Content-Type memberi tahu klien bahwa isi respons berupa JSON.", "app", "proxy", catalogResponse, { kind: "response", ms: 4 }),
          step("Browser menampilkan produk", "Proxy mengirim respons kembali ke browser. Kode antarmuka membaca JSON dan memperbarui tampilan produk.", "proxy", "browser", catalogResponse, { kind: "response", ms: 11, states: { browser: "200 OK" } }),
        ],
      },
      {
        id: "tidak-ada", name: "Produk tidak ditemukan · 404",
        steps: [
          step("Browser memakai koneksi yang sama", "Browser sudah terhubung ke toko.example. Ia mengirim GET untuk ID produk lain melalui koneksi yang masih terbuka.", "browser", "proxy", "GET /api/produk/999 HTTP/1.1\nHost: toko.example", { ms: 12 }),
          step("Proxy memilih layanan katalog", "Request cocok dengan jalur katalog. Proxy meneruskannya ke aplikasi.", "proxy", "app", "Upstream: katalog:8000", { ms: 4 }),
          step("Aplikasi mencari produk", "Handler meminta database membaca produk dengan ID 999.", "app", "db", "SELECT id, nama FROM produk WHERE id = ?\nParameter: [999]", { ms: 3 }),
          step("Query menghasilkan nol baris", "Koneksi dan query berhasil. Tidak ada produk untuk ID yang diminta.", "db", "app", "0 baris ditemukan", { kind: "response", ms: 7 }),
          step("Aplikasi mengembalikan 404", "Handler memberi status 404 untuk menyatakan bahwa resource produk tersebut tidak ditemukan.", "app", "proxy", 'HTTP/1.1 404 Not Found\nContent-Type: application/json\n\n{"error":"Produk tidak ditemukan"}', { kind: "error", ms: 4 }),
          step("Browser menampilkan pesan", "Antarmuka membaca kode 404 dan memberi pengguna informasi bahwa produk itu tidak tersedia.", "proxy", "browser", "HTTP/1.1 404 Not Found", { kind: "error", ms: 11, states: { browser: "404 Not Found" } }),
        ],
      },
    ],
    terms: [
      ["Request", "Pesan dari klien yang mencantumkan method, target, header, dan pada beberapa permintaan, body."],
      ["Response", "Pesan balasan yang memuat status, header, dan biasanya body."],
      ["Upstream", "Layanan tujuan yang menerima request dari proxy."],
    ],
    source: ["RFC 9110 · HTTP Semantics", "https://www.rfc-editor.org/rfc/rfc9110.html"],
    quiz: {
      question: "Siapa yang membuat keputusan 404 pada skenario produk tidak ditemukan?",
      options: ["Resolver DNS", "Aplikasi katalog", "Browser"],
      answer: 1,
      explanation: "Aplikasi katalog menerima hasil query kosong dan memilih status 404 untuk resource produk.",
    },
  },
  {
    id: "dns-tls",
    group: "dasar",
    title: "DNS dan koneksi HTTPS",
    nav: "DNS & HTTPS",
    intro: "Pelajari cara resolver menemukan alamat IP, lalu lihat bagaimana browser memeriksa identitas server sebelum mengirim request HTTP.",
    nodes: [
      browser(), dns(1, 0), node("root", "Root & TLD", "Rujukan DNS", 2, 1, "Root merujuk resolver ke nameserver TLD. TLD merujuknya ke nameserver yang menangani zona domain."),
      node("auth", "DNS otoritatif", "Sumber record", 2, 0, "Menyediakan jawaban resmi untuk nama dalam zona yang dikelolanya."),
      node("edge", "Server HTTPS", "TLS · port 443", 0, 1, "Menyajikan sertifikat dan berpartisipasi dalam negosiasi TLS. Pada contoh ini server juga menjawab HTTP."),
    ],
    scenarios: [
      {
        id: "cache-kosong", name: "DNS cache kosong + TLS valid",
        steps: [
          step("Klien bertanya ke resolver", "Browser mendelegasikan pencarian alamat toko.example ke resolver rekursif yang tersedia.", "browser", "dns", "QNAME toko.example.\nQTYPE A", { ms: 2 }),
          step("Resolver menelusuri delegasi", "Karena contoh ini dimulai tanpa cache, resolver menelusuri rujukan root dan TLD. Diagram menggabungkan keduanya dalam satu node.", "dns", "root", "Root: rujukan ke TLD\nTLD: rujukan ke DNS otoritatif", { ms: 12 }),
          step("Resolver meminta record A", "Resolver menanyakan alamat IPv4 ke nameserver otoritatif untuk zona tujuan.", "dns", "auth", "A toko.example. ?", { ms: 8 }),
          step("Jawaban disimpan sampai TTL", "Nameserver mengirim alamat dan TTL. Resolver menyimpan record untuk pencarian berikutnya.", "auth", "dns", "toko.example. 300 IN A 203.0.113.10", { kind: "response", ms: 6, states: { dns: "TTL 300 dtk" } }),
          step("Browser menerima alamat", "Browser sekarang bisa membuat koneksi TCP ke port 443 di alamat hasil resolusi.", "dns", "browser", "A 203.0.113.10", { kind: "response", ms: 2 }),
          step("Browser memulai TLS", "Setelah TCP terhubung, browser mengirim ClientHello dengan pilihan versi TLS, parameter pertukaran kunci, dan nama server.", "browser", "edge", "TCP tersambung\nTLS ClientHello\nSNI: toko.example", { ms: 18 }),
          step("Browser memeriksa sertifikat", "Browser memeriksa nama, masa berlaku, dan rantai kepercayaan sertifikat. Kedua sisi menyelesaikan handshake dan siap bertukar data HTTP terenkripsi.", "edge", "browser", "TLS 1.3 · nama cocok\nRantai sertifikat tepercaya\nHandshake selesai", { kind: "response", ms: 15, states: { edge: "TLS siap" } }),
          step("Browser mengirim GET", "Request HTTP berjalan di atas koneksi TLS yang baru disiapkan.", "browser", "edge", "GET / HTTP/1.1\nHost: toko.example", { ms: 10 }),
          step("Server mengembalikan halaman", "HTTP 200 dan body HTML kembali melalui koneksi yang sama.", "edge", "browser", "HTTP/1.1 200 OK\nContent-Type: text/html", { kind: "response", ms: 12 }),
        ],
      },
      {
        id: "sertifikat-salah", name: "DNS cache hit + sertifikat salah",
        steps: [
          step("Resolver memeriksa cache", "Record masih dalam masa TTL, jadi resolver dapat segera menjawab.", "browser", "dns", "A toko.example. ?\nCache: HIT", { ms: 2, states: { dns: "TTL 184 dtk" } }),
          step("Resolver memberi alamat", "Record A memberi alamat IP. Browser masih harus memeriksa bahwa server di alamat tersebut berhak memakai nama domain.", "dns", "browser", "toko.example. 184 IN A 203.0.113.10", { kind: "response", ms: 2 }),
          step("Browser memulai handshake", "Nama toko.example dikirim agar server dapat memilih sertifikat yang sesuai.", "browser", "edge", "ClientHello\nSNI: toko.example", { ms: 18 }),
          step("Nama sertifikat berbeda", "Server menyajikan sertifikat untuk nama lain. Browser menghentikan handshake sebelum mengirim request HTTP.", "edge", "browser", "Nama diminta: toko.example\nNama pada sertifikat: aset.example\nTLS berhenti: nama tidak cocok", { kind: "error", ms: 15, states: { browser: "Nama tidak cocok" } }),
        ],
      },
    ],
    terms: [
      ["TTL", "Lama record DNS boleh digunakan dari cache."],
      ["Record A / AAAA", "Pemetaan nama domain ke alamat IPv4 atau IPv6."],
      ["SNI", "Nama server yang dapat disertakan klien dalam ClientHello agar server memilih konfigurasi TLS yang sesuai."],
    ],
    source: ["IETF · TLS 1.3", "https://datatracker.ietf.org/doc/html/rfc8446"],
    quiz: {
      question: "Apa yang terjadi jika nama pada sertifikat TLS berbeda dari nama domain yang dibuka?",
      options: ["Browser mengganti alamat DNS secara otomatis", "Browser beralih ke HTTP biasa", "Browser menghentikan handshake dan menampilkan kesalahan"],
      answer: 2, explanation: "Validasi nama gagal, sehingga browser tidak mengirim request HTTP pada koneksi itu.",
    },
  },
  {
    id: "reverse-proxy",
    group: "dasar",
    title: "Reverse proxy dan tunnel",
    nav: "Proxy & Cloudflare Tunnel",
    intro: "Telusuri bagaimana hostname publik mencapai layanan di localhost melalui Cloudflare Tunnel, termasuk cara membedakan gangguan konektor dan gangguan origin.",
    nodes: [
      browser(),
      node("edge", "Edge Cloudflare", "Hostname publik", 1, 0, "Menerima koneksi HTTPS dari pengunjung dan mencocokkan hostname dengan rute yang dipublikasikan."),
      node("tunnel", "cloudflared", "Konektor tunnel", 2, 0, "Membuka koneksi keluar ke Cloudflare dan meneruskan request yang diterima ke alamat origin."),
      node("origin", "Portal belajar", "Origin · :5100", 2, 1, "Layanan HTTP pada 127.0.0.1:5100. Origin menyajikan HTML, CSS, dan JavaScript portal untuk hostname publik."),
    ],
    scenarios: [
      {
        id: "aktif", name: "Tunnel aktif + origin siap",
        steps: [
          step("Konektor tersambung ke edge", "cloudflared lebih dulu membuka koneksi keluar ke Cloudflare. Koneksi itu dipakai untuk membawa trafik pengunjung ke mesin origin.", "tunnel", "edge", "Koneksi keluar cloudflared → Cloudflare\nStatus konektor: tersambung", { ms: 20, states: { tunnel: "Tersambung" } }),
          step("Pengunjung membuka domain", "Browser mengirim HTTPS ke edge untuk hostname ivanpakpahan.my.id. Edge membaca hostname untuk mencari rute yang cocok.", "browser", "edge", "GET /\nHost: ivanpakpahan.my.id", { ms: 17 }),
          step("Edge memakai rute tunnel", "Rute publik mengarahkan request ke konektor yang tersedia lewat koneksi yang sudah dibuka.", "edge", "tunnel", "Hostname: ivanpakpahan.my.id\nRute: published application", { ms: 8 }),
          step("Konektor meneruskan ke loopback", "Di mesin yang sama, cloudflared meneruskan HTTP ke port 5100 bersama hostname publik. HTTPS bagi pengunjung berakhir di edge, dan tunnel mengamankan bagian edge ke konektor.", "tunnel", "origin", "Service URL: http://127.0.0.1:5100\nGET /\nHost: ivanpakpahan.my.id", { ms: 1 }),
          step("Origin mengembalikan HTML", "Portal menerima GET / dan mengembalikan dokumen HTML beserta tipe kontennya.", "origin", "tunnel", "HTTP/1.1 200 OK\nContent-Type: text/html", { kind: "response", ms: 4 }),
          step("Response kembali ke edge", "Konektor mengirim response melalui tunnel.", "tunnel", "edge", "Tunnel membawa status, header, dan body", { kind: "response", ms: 8 }),
          step("Browser menerima halaman", "Edge mengirim respons HTTPS. Browser membaca HTML lalu meminta aset CSS dan JavaScript.", "edge", "browser", "HTTP 200 · halaman portal", { kind: "response", ms: 15, states: { browser: "200 OK" } }),
        ],
      },
      {
        id: "origin-mati", name: "Konektor aktif, origin mati · 502",
        steps: [
          step("Edge menerima GET", "Hostname publik dan koneksi browser ke edge berfungsi.", "browser", "edge", "GET /\nHost: ivanpakpahan.my.id", { ms: 17 }),
          step("Request mencapai konektor", "Cloudflare masih memiliki koneksi tunnel yang aktif dan meneruskan request seperti biasa.", "edge", "tunnel", "Status konektor: tersambung", { ms: 8, states: { tunnel: "Tersambung" } }),
          step("Port origin menolak koneksi", "Konektor mencoba port 5100. Pada skenario ini origin sedang berhenti.", "tunnel", "origin", "connect 127.0.0.1:5100\nConnection refused", { kind: "error", ms: 2, states: { origin: "Offline" } }),
          step("Gangguan dilaporkan ke edge", "Konektor mengembalikan kegagalan karena origin tidak dapat dijangkau.", "tunnel", "edge", "Origin error: connection refused", { kind: "error", ms: 8 }),
          step("Browser menerima 502", "Periksa proses origin dan Service URL. Jika edge kehilangan semua konektor, Cloudflare dapat menampilkan error 1033 sebelum request mencapai mesin origin.", "edge", "browser", "HTTP 502 Bad Gateway", { kind: "error", ms: 15, states: { browser: "502 Bad Gateway" } }),
        ],
      },
    ],
    terms: [
      ["Edge", "Titik masuk publik terdekat di jaringan penyedia proxy."],
      ["Origin", "Layanan yang menghasilkan konten yang diteruskan ke pengunjung."],
      ["Loopback", "Alamat 127.0.0.1 menunjuk ke mesin tempat proses yang mengaksesnya berjalan."],
    ],
    source: ["Cloudflare · Published applications", "https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/routing-to-tunnel/"],
    quiz: {
      question: "Jika tunnel tersambung tetapi port origin menolak koneksi, bagian mana yang diperiksa lebih dulu?",
      options: ["Proses origin dan Service URL", "TTL record DNS browser", "Ukuran body HTML"],
      answer: 0, explanation: "Request sudah mencapai konektor. Periksa apakah proses origin berjalan dan alamat serta portnya cocok dengan Service URL.",
    },
  },
  {
    id: "load-balancer", group: "trafik", title: "Load balancing dan failover", nav: "Load balancer",
    intro: "Bandingkan pembagian request secara bergiliran, pilihan berdasarkan koneksi aktif, dan perubahan rute saat backend tidak sehat.",
    nodes: [
      browser(0, 1),
      node("lb", "Load balancer", "Pembagi trafik", 1, 1, "Memilih backend yang sehat dengan algoritme yang dikonfigurasi, lalu meneruskan request."),
      node("a", "Server A", "Backend aplikasi", 2, 0, "Satu replika aplikasi yang dapat menerima request saat sehat."),
      node("b", "Server B", "Backend aplikasi", 2, 1, "Replika aplikasi yang menerima request tanpa bergantung pada replika A."),
      node("c", "Server C", "Backend aplikasi", 2, 2, "Replika tambahan dalam pool load balancer."),
    ],
    scenarios: [
      {
        id: "round-robin", name: "Round robin · 3 backend sehat",
        steps: [
          step("Tiga request masuk", "Tiga permintaan independen tiba. Karena backend setara, load balancer memutar urutan A, B, C.", "browser", "lb", "R1, R2, R3 → GET /api/produk\nAlgoritme: round robin", { ms: 12, states: { a: "Sehat · 0 request", b: "Sehat · 0 request", c: "Sehat · 0 request" } }),
          step("R1 dikirim ke A", "A berada pada giliran pertama.", "lb", "a", "R1 → Server A", { ms: 2, states: { a: "Sehat · 1 request" } }),
          step("R2 dikirim ke B", "B berada pada giliran kedua.", "lb", "b", "R2 → Server B", { ms: 2, states: { b: "Sehat · 1 request" } }),
          step("R3 dikirim ke C", "C berada pada giliran ketiga. Jika semua tetap sehat, giliran berikutnya kembali ke A.", "lb", "c", "R3 → Server C\nGiliran selanjutnya: A", { ms: 2, states: { c: "Sehat · 1 request" } }),
          step("Contoh balasan backend tiba", "Server B menyelesaikan R2. Urutan respons bisa berbeda dari urutan penugasan karena waktu kerja tiap server berbeda.", "b", "lb", "R2 ← HTTP 200", { kind: "response", ms: 18 }),
          step("Klien menerima respons R2", "Load balancer mengembalikan response ke koneksi klien untuk request tersebut. R1 dan R3 memiliki respons masing-masing.", "lb", "browser", "R2 ← HTTP 200\nDistribusi: A=1, B=1, C=1", { kind: "response", ms: 10 }),
        ],
      },
      {
        id: "least-connections", name: "Least connections · beban tidak rata",
        steps: [
          step("Request datang saat pool sibuk", "A memiliki 4 koneksi aktif, B memiliki 1, dan C memiliki 3. Contoh menganggap bobot backend sama.", "browser", "lb", "GET /api/produk\nA=4, B=1, C=3 koneksi aktif", { ms: 12, states: { a: "4 koneksi", b: "1 koneksi", c: "3 koneksi" } }),
          step("Load balancer memilih B", "Algoritme least connections memilih backend sehat dengan paling sedikit koneksi aktif. Koneksi baru membuat hitungan B naik menjadi 2.", "lb", "b", "min(4, 1, 3) = 1 → Server B", { ms: 2, states: { b: "2 koneksi" } }),
          step("B menyelesaikan request", "Dalam contoh ini koneksi upstream ditutup setelah response, sehingga hitungan B turun lagi.", "b", "lb", "HTTP 200\nB kembali ke 1 koneksi aktif", { kind: "response", ms: 21, states: { b: "1 koneksi" } }),
          step("Klien menerima response", "Klien memperoleh hasil tanpa perlu mengetahui server mana yang menanganinya.", "lb", "browser", "HTTP 200 OK", { kind: "response", ms: 10 }),
        ],
      },
      {
        id: "failover", name: "Health check gagal · lewati A",
        steps: [
          step("Health check A gagal", "Setelah ambang kegagalan pemeriksaan kesehatan tercapai, A dikeluarkan dari daftar backend untuk request baru.", "lb", "a", "GET /health → timeout\nA: dikeluarkan dari pool", { kind: "error", ms: 300, states: { a: "Tidak sehat", b: "Sehat", c: "Sehat" } }),
          step("Request baru masuk", "Browser tetap memakai alamat load balancer yang sama.", "browser", "lb", "GET /api/produk\nBackend siap: B, C", { ms: 12 }),
          step("Request dialihkan ke B", "Load balancer hanya memilih backend yang sehat. A akan kembali layak dipilih setelah memenuhi syarat kesehatan.", "lb", "b", "Upstream: Server B", { ms: 2 }),
          step("B mengembalikan 200", "Server B memproses request dan mengirim respons.", "b", "lb", "HTTP 200 OK", { kind: "response", ms: 21 }),
          step("Klien tetap menerima hasil", "Kapasitas pool berkurang, tetapi request ini tetap berhasil berkat backend lain.", "lb", "browser", "HTTP 200 OK\nPool sehat: 2 dari 3", { kind: "response", ms: 10 }),
        ],
      },
    ],
    terms: [
      ["Round robin", "Memilih backend bergiliran."],
      ["Least connections", "Memilih backend sehat dengan koneksi aktif paling sedikit untuk bobot yang sama."],
      ["Health check", "Pemeriksaan yang menentukan apakah backend layak menerima trafik baru."],
    ],
    source: ["NGINX · HTTP load balancing", "https://nginx.org/en/docs/http/load_balancing.html"],
    quiz: {
      question: "Dengan 4, 1, dan 3 koneksi aktif pada A, B, dan C, backend sehat mana yang dipilih least connections?",
      options: ["Server A", "Server C", "Server B"],
      answer: 2, explanation: "Server B memiliki koneksi aktif paling sedikit, tepatnya satu sebelum request baru masuk.",
    },
  },
  {
    id: "cache", group: "trafik", title: "Cache, CDN dan TTL", nav: "Cache & CDN",
    intro: "Bandingkan jalur cache miss, cache hit, dan validasi ulang saat salinan di CDN sudah kedaluwarsa.",
    nodes: [
      browser(), node("cdn", "Cache CDN", "Cache bersama", 1, 0, "Menyimpan respons publik yang dapat dipakai ulang sesuai kebijakan cache."),
      node("origin", "Server origin", "Pemilik konten", 2, 0, "Menyediakan aset dan header Cache-Control atau ETag yang menentukan cara cache memperlakukan respons."),
    ],
    scenarios: [
      {
        id: "hit-miss", name: "Request pertama MISS, kedua HIT",
        steps: [
          step("Browser meminta aset", "Klien meminta gambar publik. Cache bersama memakai kunci untuk menemukan salinan yang cocok.", "browser", "cdn", "GET /assets/kemasan.webp", { ms: 9 }),
          step("CDN mengalami MISS", "Salinan belum ada. CDN harus mengambil aset dari origin.", "cdn", "origin", "GET /assets/kemasan.webp\nCache: MISS", { ms: 28, states: { cdn: "MISS" } }),
          step("Origin memberi respons yang dapat disimpan", "Header public dan max-age memberi izin penyimpanan dan masa segar 60 detik. CDN menyimpan salinan untuk request berikutnya.", "origin", "cdn", 'HTTP 200 OK\nCache-Control: public, max-age=60\nETag: "kemasan-v1"', { kind: "response", ms: 26, states: { cdn: "Segar · 60 dtk" } }),
          step("Respons pertama tiba", "Browser menerima file melalui CDN setelah pengambilan dari origin.", "cdn", "browser", "HTTP 200 OK\nAge: 0", { kind: "response", ms: 11 }),
          step("Klien berikutnya meminta aset sama", "Klien lain meminta URL yang sama 12 detik kemudian. Salinan di CDN masih segar.", "browser", "cdn", "GET /assets/kemasan.webp\nWaktu simulasi: +12 detik", { ms: 9 }),
          step("CDN langsung menjawab", "Cache hit menghilangkan perjalanan CDN ke origin. Age menunjukkan umur respons dalam detik.", "cdn", "browser", "HTTP 200 OK\nAge: 12\nCache: HIT", { kind: "response", ms: 11, states: { cdn: "HIT · usia 12 dtk" } }),
        ],
      },
      {
        id: "ttl-habis", name: "TTL habis · ETag menghasilkan 304",
        steps: [
          step("Salinan CDN kedaluwarsa", "Usia aset melewati max-age 60 detik. CDN perlu mengetahui apakah file masih sama sebelum memakai salinannya.", "browser", "cdn", "GET /assets/kemasan.webp\nUsia salinan: 65 detik", { ms: 9, states: { cdn: "Kedaluwarsa" } }),
          step("CDN bertanya dengan ETag", "If-None-Match mengirim identitas versi yang dimiliki CDN.", "cdn", "origin", 'GET /assets/kemasan.webp\nIf-None-Match: "kemasan-v1"', { ms: 28 }),
          step("Origin mengembalikan 304", "Versi file masih cocok, sehingga origin tidak perlu mengirim body aset lagi.", "origin", "cdn", 'HTTP 304 Not Modified\nETag: "kemasan-v1"\nCache-Control: public, max-age=60', { kind: "response", ms: 21, states: { cdn: "Validasi berhasil" } }),
          step("CDN mengirim body dari salinannya", "Permintaan browser pada skenario ini tidak bersyarat, sehingga CDN mengirim 200 beserta body yang baru divalidasi.", "cdn", "browser", "HTTP 200 OK\nBody: salinan CDN", { kind: "response", ms: 11 }),
        ],
      },
    ],
    terms: [
      ["Cache hit", "Salinan yang cocok dan masih dapat digunakan ditemukan."],
      ["Cache miss", "Cache perlu mengambil respons dari origin karena salinan belum tersedia."],
      ["ETag", "Validator versi representasi yang bisa dipakai untuk revalidasi."],
    ],
    source: ["RFC 9111 · HTTP Caching", "https://www.rfc-editor.org/rfc/rfc9111.html"],
    quiz: {
      question: "Mengapa origin dapat mengembalikan 304 saat menerima If-None-Match?",
      options: ["Karena origin selalu memblokir CDN", "Karena versi aset masih sama dengan ETag yang dikirim", "Karena salinan CDN belum pernah dibuat"],
      answer: 1, explanation: "ETag masih cocok. CDN dapat memakai body yang sudah disimpan setelah memperbarui hasil validasinya.",
    },
  },
  {
    id: "database", group: "data", title: "Database dan replikasi", nav: "Database & replikasi",
    intro: "Ikuti transaksi dari API ke database primary. Coba membaca dari replica saat perubahan masih dalam perjalanan untuk memahami replication lag.",
    nodes: [
      browser(), app(1, 0),
      node("primary", "Primary DB", "Baca dan tulis", 2, 0, "Menerima transaksi tulis dan menghasilkan catatan perubahan untuk replica."),
      node("replica", "Replica DB", "Baca saja", 2, 1, "Menerapkan perubahan dari primary. Bacaan dapat tertinggal saat replikasi berjalan secara asinkron."),
    ],
    scenarios: [
      {
        id: "tulis", name: "Tulis ke primary dan replikasi",
        steps: [
          step("Klien meminta perubahan stok", "API menerima produk dan jumlah yang harus disimpan.", "browser", "app", "PATCH /api/produk/42\n{\"stok\": 12}", { ms: 10 }),
          step("Aplikasi memulai transaksi", "Pool koneksi meminjamkan koneksi untuk update pada primary.", "app", "primary", "BEGIN\nUPDATE produk SET stok = ? WHERE id = ?\nParameter: [12, 42]\nCOMMIT", { ms: 5 }),
          step("Primary mengonfirmasi commit", "Transaksi sudah dicatat di primary. Pada replikasi asinkron, konfirmasi bisa datang sebelum replica menerapkan perubahan.", "primary", "app", "COMMIT OK\nPrimary: stok 12", { kind: "response", ms: 9, states: { primary: "Stok 12", replica: "Stok 8" } }),
          step("API mengonfirmasi ke klien", "Aplikasi mengembalikan nilai baru berdasarkan hasil transaksi.", "app", "browser", "HTTP 200 OK\n{\"stok\": 12}", { kind: "response", ms: 8 }),
          step("Replica menerapkan perubahan", "Catatan perubahan dialirkan ke replica. Setelah diterapkan, hasil baca replica menyamai primary pada contoh ini.", "primary", "replica", "WAL replay selesai\nReplica: stok 12", { ms: 85, states: { replica: "Stok 12" } }),
        ],
      },
      {
        id: "lag", name: "Baca replica saat tertinggal",
        steps: [
          step("Klien membaca sesaat setelah update", "Primary sudah menyimpan stok 12, tetapi replica masih menunjukkan versi sebelumnya.", "browser", "app", "GET /api/produk/42", { ms: 10, states: { primary: "Stok 12", replica: "Stok 8" } }),
          step("API memilih replica", "Pembacaan biasa diarahkan ke replica untuk mengurangi beban primary.", "app", "replica", "SELECT stok FROM produk WHERE id = ?\nParameter: [42]", { ms: 5 }),
          step("Replica memberi nilai lama", "Query berhasil dengan stok 8 karena perubahan terbaru belum diterapkan.", "replica", "app", "{\"stok\": 8}\nStatus replica: tertinggal", { kind: "response", ms: 7 }),
          step("Klien melihat nilai sebelumnya", "Untuk kebutuhan read-your-writes, aplikasi dapat mengarahkan pembacaan segera setelah update ke primary.", "app", "browser", "HTTP 200 OK\n{\"stok\": 8}", { kind: "response", ms: 8, states: { browser: "Stok 8" } }),
          step("Replica akhirnya menyusul", "Setelah replay selesai, query berikutnya dapat membaca stok 12 pada replica.", "primary", "replica", "WAL diterapkan\nReplica: stok 12", { ms: 85, states: { replica: "Stok 12" } }),
        ],
      },
    ],
    terms: [
      ["Commit", "Mengakhiri transaksi dengan menyimpan perubahan yang berhasil."],
      ["WAL", "Write-ahead log yang mencatat perubahan dan dapat dikirim ke replica."],
      ["Replication lag", "Jeda antara perubahan pada primary dan saat perubahan bisa dibaca pada replica."],
    ],
    source: ["PostgreSQL · Streaming replication", "https://www.postgresql.org/docs/17/warm-standby.html"],
    quiz: {
      question: "Dari mana aplikasi dapat membaca untuk melihat perubahan yang baru saja di-commit ketika replica masih tertinggal?",
      options: ["Primary", "Replica yang tertinggal", "Resolver DNS"],
      answer: 0, explanation: "Primary sudah mengonfirmasi commit. Replica mungkin belum menerapkan perubahan itu.",
    },
  },
  {
    id: "queue", group: "data", title: "Queue dan background worker", nav: "Queue & worker",
    intro: "Pisahkan permintaan HTTP dari pekerjaan yang butuh waktu. Ikuti job mulai dari antrian sampai selesai, termasuk pengiriman ulang saat worker berhenti.",
    nodes: [
      browser(), app(1, 0),
      node("queue", "Broker", "Antrian job", 2, 0, "Menerima job dari producer, mengirimnya ke worker, dan mencatat konfirmasi pemrosesan."),
      node("worker", "Worker", "Proses latar", 2, 1, "Mengambil job, menyimpan hasil, lalu mengirim konfirmasi bahwa pekerjaan selesai."),
      database(1, 1),
    ],
    scenarios: [
      {
        id: "job-selesai", name: "202 diterima, worker menyelesaikan job",
        steps: [
          step("Klien meminta laporan", "API menerima permintaan membuat laporan yang memerlukan waktu lebih lama daripada request HTTP biasa.", "browser", "app", "POST /api/laporan", { ms: 12 }),
          step("API mengirim job", "API mengirim pesan job ke broker dengan ID yang dapat dipakai untuk melacak hasil.", "app", "queue", "jobId=lap-42\ntipe=buat-laporan", { ms: 4, states: { queue: "1 siap" } }),
          step("Broker mengonfirmasi penerimaan", "Publisher confirm menandakan broker sudah menerima pesan sesuai konfigurasinya. Worker masih harus mengerjakannya.", "queue", "app", "Publisher confirm: lap-42", { kind: "response", ms: 5 }),
          step("API mengembalikan 202", "202 Accepted berarti pekerjaan diterima untuk diproses. Location menunjuk ke endpoint status pekerjaan.", "app", "browser", "HTTP 202 Accepted\nLocation: /api/laporan/lap-42", { kind: "response", ms: 10, states: { browser: "202 Accepted" } }),
          step("Worker menerima job", "Broker menyerahkan pesan ke worker. Pesan menunggu konfirmasi pemrosesan.", "queue", "worker", "Delivery: lap-42\nStatus: menunggu ACK", { ms: 7, states: { queue: "1 menunggu ACK", worker: "Mengerjakan" } }),
          step("Worker menyimpan hasil", "Laporan dan status selesai disimpan agar dapat diambil oleh endpoint status.", "worker", "db", "lap-42 → status=selesai\nSimpan hasil laporan", { ms: 165, states: { db: "Laporan tersedia" } }),
          step("Worker mengirim ACK", "Setelah pekerjaan disimpan, worker mengonfirmasi pesan ke broker.", "worker", "queue", "ACK lap-42", { kind: "response", ms: 3, states: { queue: "Antrian kosong", worker: "Selesai" } }),
        ],
      },
      {
        id: "redelivery", name: "Worker berhenti sebelum ACK",
        steps: [
          step("Broker memberikan job", "Worker menerima lap-42 dan mulai memproses tanpa mengirim ACK lebih dulu.", "queue", "worker", "Delivery #1\nJob: lap-42", { ms: 7, states: { queue: "1 menunggu ACK" } }),
          step("Koneksi worker terputus", "Worker sempat menyimpan laporan, lalu berhenti sebelum broker menerima ACK. Broker memasukkan kembali pesan yang belum dikonfirmasi.", "worker", "queue", "Putus sebelum ACK\nJob dikembalikan ke antrian", { kind: "error", ms: 15, states: { queue: "1 siap", worker: "Terputus" } }),
          step("Broker mengirim ulang job", "Worker yang tersedia menerima ID job yang sama. Pada sistem dengan redelivery, satu pesan bisa diproses lebih dari sekali.", "queue", "worker", "Delivery #2 · redelivered\nJob: lap-42", { ms: 7, states: { queue: "1 menunggu ACK", worker: "Berjalan" } }),
          step("Worker memeriksa hasil yang sudah ada", "Worker memakai ID job untuk mengenali pekerjaan yang sudah selesai dan menghindari penyimpanan duplikat.", "worker", "db", "Cek lap-42\nHasil sudah tersimpan", { ms: 12, states: { db: "1 hasil tersimpan" } }),
          step("Pemrosesan dikonfirmasi", "Setelah memastikan hasil tersedia, worker mengirim ACK dan broker dapat menghapus pesan dari antrian.", "worker", "queue", "ACK lap-42", { kind: "response", ms: 3, states: { queue: "Antrian kosong" } }),
        ],
      },
    ],
    terms: [
      ["Producer", "Proses yang mengirim pesan ke broker."],
      ["ACK", "Konfirmasi bahwa worker sudah menangani pesan."],
      ["Idempoten", "Pemrosesan ulang menghasilkan keadaan akhir yang sama, tanpa menggandakan efek yang sudah terjadi."],
    ],
    source: ["RabbitMQ · Acknowledgements and confirms", "https://www.rabbitmq.com/docs/confirms"],
    quiz: {
      question: "Kapan worker sebaiknya mengirim ACK pada skenario pembuatan laporan?",
      options: ["Sebelum menerima job", "Sesudah hasil berhasil disimpan", "Segera setelah API mengembalikan 202"],
      answer: 1, explanation: "ACK setelah menyimpan hasil memungkinkan broker mengirim ulang pesan jika worker berhenti lebih awal.",
    },
  },
  {
    id: "observability", group: "data", title: "Log, metrik dan tracing", nav: "Observabilitas",
    intro: "Bandingkan request sehat dengan request yang melambat. Gunakan trace ID, durasi per komponen, dan kode status untuk menemukan letak gangguan.",
    nodes: [
      browser(), proxy(), app(), database(),
      node("telemetry", "Telemetri", "Log · metrik · trace", 1, 1, "Menerima data instrumentasi dari layanan. Log menyimpan kejadian, metrik merangkum pengukuran, dan trace menunjukkan alur request."),
    ],
    scenarios: [
      {
        id: "normal", name: "Korelasi request sehat",
        steps: [
          step("Proxy menerima request", "Trace ID dibuat atau diteruskan sesuai kebijakan instrumentasi. ID membuat aktivitas request ini bisa dikorelasikan lintas layanan.", "browser", "proxy", "GET /api/produk/42", { ms: 11 }),
          step("Konteks trace dikirim ke aplikasi", "Proxy meneruskan konteks agar span aplikasi menjadi bagian dari trace yang sama.", "proxy", "app", "Trace ID: 0af7651916cd43dd8448eb211c80319c\nSpan: app.request", { ms: 4 }),
          step("Aplikasi mencatat span query", "Span query mencatat durasi operasi database sebagai satu bagian dari request.", "app", "db", "Span: db.query\nOperasi: SELECT produk", { ms: 6 }),
          step("Aplikasi meneruskan response", "Query selesai dengan sukses. API membalas dan aplikasi mencatat status.", "app", "proxy", "HTTP 200\nLog: request selesai", { kind: "response", ms: 4 }),
          step("Proxy mengirim 200", "Klien menerima respons dan proxy mencatat durasi serta status akhir.", "proxy", "browser", "HTTP 200 OK", { kind: "response", ms: 11, states: { browser: "200 OK" } }),
          step("Data dikumpulkan", "Exporter mengirim telemetri. Gunakan trace untuk request ini, log untuk detail kejadian, dan metrik untuk gambaran banyak request.", "app", "telemetry", "Trace: app.request → db.query (6 ms)\nLog: status=200\nMetrik: tambah 1 request sukses", { states: { telemetry: "Trace tercatat" } }),
        ],
      },
      {
        id: "timeout", name: "Query melampaui timeout proxy",
        steps: [
          step("Proxy menerima GET", "Jalur awal sama seperti pada request sehat. Proxy menunggu respons upstream dengan batas waktu 1 detik.", "browser", "proxy", "GET /api/produk/42\nBatas upstream: 1000 ms", { ms: 11 }),
          step("Proxy meneruskan request", "Aplikasi memperoleh trace context dan mulai menangani request.", "proxy", "app", "Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736\nSpan: app.request", { ms: 4 }),
          step("Operasi database masih berlangsung", "Span database berlangsung sekitar 1,2 detik pada contoh ini. Database adalah komponen dengan waktu terbanyak pada trace tersebut.", "app", "db", "Span db.query: 1200 ms\nBatas proxy terlampaui saat query berjalan", { kind: "error", ms: 1200, states: { db: "Query lambat" } }),
          step("Proxy mengirim 504", "Begitu batas waktunya habis, proxy mengembalikan Gateway Timeout ke klien. Proxy melakukan ini sebelum query contoh selesai.", "proxy", "browser", "HTTP 504 Gateway Timeout\nDeadline upstream: 1000 ms", { kind: "error", ms: 11, states: { browser: "504 Timeout" } }),
          step("Trace dan log menunjukkan letak penundaan", "Saat korelasi, log proxy menunjukkan batas upstream, sementara trace aplikasi menunjukkan waktu di query. Ini menunjukkan komponen yang perlu ditelusuri lebih lanjut.", "app", "telemetry", "Log proxy: upstream timeout\nSpan app.request → db.query: 1200 ms\nMetrik proxy: tambah 1 respons 504", { states: { telemetry: "Timeout tercatat" } }),
        ],
      },
    ],
    terms: [
      ["Log", "Catatan suatu kejadian dengan waktu dan konteks."],
      ["Metrik", "Pengukuran yang dapat dibandingkan dari waktu ke waktu, seperti jumlah error dan distribusi latensi."],
      ["Trace dan span", "Trace menggambarkan satu alur request. Span mewakili satu operasi dan durasinya."],
    ],
    source: ["OpenTelemetry · Signals", "https://opentelemetry.io/docs/concepts/signals/"],
    quiz: {
      question: "Sinyal apa yang menunjukkan durasi tiap operasi dalam satu request lintas komponen?",
      options: ["Satu baris access log", "Metrik total request", "Trace yang berisi span"],
      answer: 2, explanation: "Span yang dihubungkan dalam satu trace menunjukkan urutan, hubungan, dan durasi operasi request.",
    },
  },
  {
    id: "docker", group: "praktik", title: "Docker dan container", nav: "Docker & container",
    intro: "Ikuti image saat dijalankan sebagai container. Amati pemetaan port dari host dan apa yang terjadi pada data ketika container diganti.",
    nodes: [
      browser(), node("host", "Host Docker", "Port host · :8080", 1, 0, "Menjalankan Docker Engine dan meneruskan paket dari port host yang dipublikasikan."),
      node("container", "Container web", "Port internal · :80", 2, 0, "Menjalankan proses web dari image. Container memiliki lapisan tulis sendiri dan dapat dipasang volume."),
      node("image", "Image", "Paket aplikasi", 1, 1, "Berisi lapisan yang mendefinisikan filesystem awal, dependensi, dan konfigurasi bawaan proses."),
      node("volume", "Volume", "Data persisten", 2, 1, "Penyimpanan Docker yang dapat tetap ada ketika container dihapus dan dapat dipasang kembali."),
    ],
    scenarios: [
      {
        id: "pemetaan-port", name: "Jalankan web dan petakan port",
        steps: [
          step("Docker menyiapkan image", "Docker mengambil image bila belum tersedia secara lokal. Image menyediakan berkas dan konfigurasi awal server web.", "image", "host", "docker pull nginx:stable", { ms: 80, states: { image: "Tersedia" } }),
          step("Engine membuat container", "Docker menjalankan proses web dan memetakan port loopback host 8080 ke port 80 container.", "host", "container", "docker run --name web -d -p 127.0.0.1:8080:80 nginx:stable", { ms: 120, states: { container: "Berjalan", host: "8080 → 80" } }),
          step("Browser mengakses port host", "Browser pada mesin host membuka 127.0.0.1:8080 dan mengirim GET.", "browser", "host", "GET http://127.0.0.1:8080/", { ms: 3 }),
          step("Request mencapai proses web", "Pemetaan mengantar koneksi ke port 80 container, tempat proses web menerima HTTP.", "host", "container", "Host :8080 → web :80", { ms: 2 }),
          step("Container mengirim respons", "Proses web merespons. Balasan melewati pemetaan jaringan yang sama dalam arah sebaliknya.", "container", "host", "HTTP/1.1 200 OK", { kind: "response", ms: 6 }),
          step("Browser menampilkan halaman", "Browser menerima HTML melalui port host yang ia gunakan.", "host", "browser", "HTTP 200 · halaman web", { kind: "response", ms: 2 }),
        ],
      },
      {
        id: "volume", name: "Ganti container dengan volume",
        steps: [
          step("Host memasang named volume", "Dalam skenario ini aplikasi menyimpan laporan di /data, yang dipasang dari volume laporan-data.", "host", "container", "services:\n  web:\n    volumes:\n      - laporan-data:/data\nvolumes:\n  laporan-data:", { states: { container: "Container lama" } }),
          step("Aplikasi menyimpan laporan", "Berkas yang ditulis ke /data berada di volume dan memiliki siklus hidup terpisah dari container.", "container", "volume", "Tulis /data/report.json\nVolume: laporan-data", { ms: 8, states: { volume: "report.json" } }),
          step("Host membuat container pengganti", "Versi aplikasi baru berjalan dari image baru. Docker memasang kembali volume dengan nama yang sama.", "host", "container", "Image versi baru\nMount: laporan-data:/data", { ms: 120, states: { container: "Container baru" } }),
          step("Container baru membaca file", "Aplikasi membuka /data/report.json dan menerima data lama dari volume.", "volume", "container", "Baca /data/report.json\nHasil: laporan masih tersedia", { kind: "response", ms: 7 }),
        ],
      },
    ],
    terms: [
      ["Image", "Paket berlapis yang menjadi sumber pembuatan container."],
      ["Container", "Proses aplikasi dengan filesystem dan lingkungan eksekusi sendiri."],
      ["Publish port dan volume", "Pemetaan port membawa koneksi masuk. Volume menyimpan data dengan siklus hidup tersendiri."],
    ],
    source: ["Docker Docs · Containers, konfigurasi, dan penyimpanan", "https://docs.docker.com/learn/paths/get-started-with-docker-containers/"],
    quiz: {
      question: "Ke port mana browser pada host terhubung ketika pemetaan port adalah 127.0.0.1:8080:80?",
      options: ["8080", "80", "443"],
      answer: 0, explanation: "Browser memakai port host 8080. Docker meneruskan koneksi ke port 80 di container.",
    },
  },
  {
    id: "proxmox",
    group: "praktik",
    title: "Proxmox VE dan server virtual",
    nav: "Proxmox VE",
    intro: "Jalankan Debian di dalam VM, sambungkan VM ke jaringan dengan bridge, lalu layani halaman HTML dari Nginx di dalam VM.",
    nodes: [
      browser(),
      node("host", "Host Proxmox", "Panel · :8006", 0, 1, "Menjalankan hypervisor dan menyediakan panel untuk mengelola VM pada jaringan administrasi."),
      node("bridge", "Bridge vmbr0", "Jaringan virtual", 1, 0, "Menghubungkan kartu jaringan virtual VM ke jaringan fisik melalui antarmuka host yang dikaitkan dengan bridge."),
      node("guest", "VM Debian", "Sistem tamu", 2, 0, "Mesin virtual yang punya sistem operasi, alamat IP, dan disk virtual sendiri."),
      node("nginx", "Nginx", "Web server · :80", 2, 1, "Proses di dalam VM yang membaca index.html dari document root dan menyajikannya lewat HTTP."),
    ],
    scenarios: [
      {
        id: "vm-web", name: "VM Debian dan web server siap",
        steps: [
          step("Admin membuka panel Proxmox", "Panel diakses lewat jaringan lokal. Di sini admin membuat VM, memasang ISO Debian, dan memilih bridge untuk antarmuka VM.", "browser", "host", "https://192.168.1.10:8006\nVM 101 · Debian · vmbr0", { states: { host: "Panel aktif" } }),
          step("Host menyalakan VM", "Proxmox menyediakan CPU, RAM, disk, dan kartu jaringan virtual. Debian boot dan memperoleh alamat LAN sendiri.", "host", "guest", "VM 101 boot\nIP tamu: 192.168.1.60", { states: { guest: "192.168.1.60" } }),
          step("Debian menjalankan Nginx", "Nginx mendengarkan port 80 di VM dan memiliki akses baca ke berkas situs.", "guest", "nginx", "systemctl is-active nginx\nactive", { states: { nginx: "Mendengarkan :80" } }),
          step("Klien meminta halaman dari IP VM", "Browser mengirim GET ke alamat VM. Jaringan dalam contoh ini mengantar koneksi ke bridge yang terhubung dengan kartu virtual VM.", "browser", "bridge", "GET http://192.168.1.60/", { ms: 3 }),
          step("Bridge mengantarkan trafik ke VM", "Trafik mencapai antarmuka virtual VM. Alamat IP tujuan tetap merupakan alamat VM.", "bridge", "guest", "Tujuan: 192.168.1.60:80\nNIC virtual: VirtIO", { ms: 1 }),
          step("Nginx membaca index.html", "Debian menyerahkan koneksi TCP ke Nginx. Nginx membaca halaman dari document root dan menyiapkan respons.", "guest", "nginx", "GET / → /var/www/html/index.html", { ms: 2 }),
          step("Response keluar dari VM", "Respons dari Nginx melewati jaringan VM dan bridge menuju perangkat klien.", "guest", "bridge", "HTTP/1.1 200 OK\nContent-Type: text/html", { kind: "response", ms: 2 }),
          step("Browser menampilkan halaman", "Klien selesai memuat HTML. Port 8006 dipakai saat administrasi dan port 80 VM dipakai saat membuka website.", "bridge", "browser", "HTTP 200 · Ruang Web", { kind: "response", ms: 3 }),
        ],
      },
      {
        id: "nginx-berhenti", name: "VM hidup, web server berhenti",
        steps: [
          step("Klien mencoba port web VM", "Browser mengakses alamat LAN VM. Mesin virtual bisa merespons jaringan, tetapi tiap layanan tetap perlu proses yang mendengarkan port.", "browser", "bridge", "Tujuan: 192.168.1.60:80", { ms: 3, states: { guest: "VM aktif" } }),
          step("Koneksi mencapai VM", "Bridge berfungsi dan paket sampai ke VM. Dalam skenario ini port 80 belum didengarkan.", "bridge", "guest", "TCP ke 192.168.1.60:80", { ms: 1 }),
          step("Port 80 menolak koneksi", "Periksa status Nginx dari konsol VM. VM yang aktif dapat memiliki service yang berhenti.", "guest", "bridge", "Connection refused\nsystemctl is-active nginx → inactive", { kind: "error", ms: 1, states: { nginx: "Berhenti" } }),
          step("Browser gagal membuka halaman", "Setelah Nginx berjalan, uji HTTP dari konsol VM sebelum menguji lagi dari perangkat lain.", "bridge", "browser", "Uji dari VM: curl -I http://127.0.0.1/", { kind: "error", ms: 3 }),
        ],
      },
    ],
    terms: [
      ["Hypervisor", "Sistem yang mengelola mesin virtual dan alokasi sumber daya host."],
      ["Bridge", "Penghubung jaringan virtual VM ke jaringan lain pada host."],
      ["Guest", "Sistem operasi yang berjalan di dalam VM, misalnya Debian."],
    ],
    source: ["Proxmox VE · Administration Guide", "https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf"],
    quiz: {
      question: "Untuk membuka Nginx di VM beralamat 192.168.1.60, URL mana yang dipakai?",
      options: ["https://192.168.1.10:8006", "http://192.168.1.60/", "http://127.0.0.1/ dari laptop lain"],
      answer: 1,
      explanation: "Klien mengakses IP VM pada port HTTP 80. Panel Proxmox memakai IP host dan port 8006.",
    },
  },
  {
    id: "hosting",
    group: "praktik",
    title: "Dari file HTML ke website publik",
    nav: "Hosting HTML ke internet",
    intro: "Ikuti perjalanan dari berkas di komputer sampai halaman terbuka lewat HTTPS dari jaringan lain. Bandingkan hosting statis dengan tunnel ke web server sendiri.",
    nodes: [
      node("files", "Folder site", "index.html + CSS", 0, 0, "Berisi berkas yang sengaja disiapkan untuk publikasi. Browser lokal bisa membacanya melalui file://."),
      node("edge", "Edge HTTPS", "Domain publik", 1, 0, "Menerima trafik untuk hostname publik, menyajikan deployment statis, atau meneruskan request ke konektor tunnel."),
      node("origin", "Nginx lokal", "Origin · :8080", 2, 0, "Menyajikan berkas dari mesin sendiri bila memakai tunnel. Pada hosting statis, unggahan yang disimpan platform menjadi sumber berkas."),
      browser(1, 1),
      dns(2, 1),
    ],
    scenarios: [
      {
        id: "pages", name: "Unggah ke hosting statis",
        steps: [
          step("Berkas disiapkan di laptop", "index.html dan CSS tersedia di folder site. Membuka file:// membaca penyimpanan pada perangkat yang membuka berkas.", "files", "browser", "file:///…/site/index.html\nAsset: ./style.css"),
          step("Folder diunggah ke penyedia hosting", "Hosting menyimpan salinan berkas. URL deployment menyediakan halaman dari folder yang memiliki index.html di bagian teratas.", "files", "edge", "Upload folder site\nDeployment: <proyek>.pages.dev", { states: { edge: "Deployment siap" } }),
          step("Pengunjung mencari alamat domain", "Pengunjung dari jaringan lain mengetik nama publik. Resolver mengembalikan alamat edge yang melayani nama itu.", "browser", "dns", "DNS → <proyek>.pages.dev", { ms: 10 }),
          step("Browser menerima alamat", "Browser dapat membuka koneksi HTTPS ke edge penyedia hosting.", "dns", "browser", "DNS: alamat edge", { kind: "response", ms: 8 }),
          step("Browser mengirim request HTTPS", "URL publik menentukan host. Path / membuka index.html dan path /style.css meminta stylesheet.", "browser", "edge", "GET /\nHost: <proyek>.pages.dev", { ms: 22 }),
          step("Edge menyajikan deployment", "Hosting mengembalikan HTML dan melayani CSS saat diminta. Komputer yang mengunggah file boleh dimatikan setelah deployment selesai.", "edge", "browser", "HTTP 200 · index.html\nGET /style.css → HTTP 200", { kind: "response", ms: 14 }),
        ],
      },
      {
        id: "tunnel", name: "Sajikan HTML dari komputer sendiri",
        steps: [
          step("Nginx memuat folder situs", "Web server menyajikan HTML dan CSS melalui HTTP. Uji origin di mesin yang menjalankan Nginx sebelum menerbitkan rute.", "files", "origin", "http://127.0.0.1:8080/ → index.html", { states: { origin: "Port 8080 siap" } }),
          step("Konektor menyiapkan tunnel", "cloudflared membuka koneksi keluar ke edge. Rute menetapkan hostname publik dan URL origin untuk contoh ini.", "origin", "edge", "web.contoh.example → tunnel\nOrigin: http://127.0.0.1:8080", { states: { edge: "Rute aktif" } }),
          step("Browser mencari alamat publik", "Pengunjung memakai alamat domain. Resolver mencari alamat edge yang melayani hostname itu.", "browser", "dns", "QNAME web.contoh.example", { ms: 10 }),
          step("DNS memberi alamat edge", "Browser menghubungi endpoint publik melalui HTTPS.", "dns", "browser", "Alamat edge tersedia", { kind: "response", ms: 8 }),
          step("Request tiba dari jaringan lain", "Pengunjung mengirim GET ke hostname publik. Sertifikat HTTPS diperiksa oleh browser.", "browser", "edge", "GET https://web.contoh.example/", { ms: 22 }),
          step("Tunnel membawa request ke origin", "Edge memilih rute tunnel. Konektor meneruskan request ke Nginx pada port 8080 di mesin tempat konektor berjalan.", "edge", "origin", "GET / → http://127.0.0.1:8080", { ms: 8 }),
          step("Origin mengembalikan HTML", "Nginx membaca berkas dan response HTTP kembali melalui konektor serta edge.", "origin", "edge", "HTTP/1.1 200 OK\nContent-Type: text/html", { kind: "response", ms: 4 }),
          step("Pengunjung menerima halaman", "Halaman berhasil dimuat lewat HTTPS. Origin dan konektor harus terus berjalan agar pengunjung berikutnya dapat mengaksesnya.", "edge", "browser", "HTTP 200 · website publik", { kind: "response", ms: 15 }),
        ],
      },
    ],
    terms: [
      ["Document root", "Folder yang dibaca web server saat melayani path URL situs."],
      ["Hosting statis", "Layanan yang menyajikan salinan HTML, CSS, JavaScript, dan aset yang diunggah."],
      ["Domain publik", "Nama yang diakses pengunjung, diarahkan melalui DNS dan dihubungkan ke layanan yang menyajikan situs."],
    ],
    source: ["Cloudflare Pages · Direct Upload", "https://developers.cloudflare.com/pages/get-started/direct-upload/"],
    quiz: {
      question: "Pilihan mana yang tetap melayani HTML publik saat komputer pengunggah dimatikan?",
      options: ["file:// ke folder di komputer", "Tunnel ke Nginx di komputer itu", "Hosting statis yang menyajikan salinan hasil upload"],
      answer: 2,
      explanation: "Hosting statis melayani berkas yang sudah diunggah dari infrastrukturnya sendiri.",
    },
  },
];

// Docker and hosting use the same example so an uploaded page matches the local one.
const demoSite = [
  ["site/index.html", `<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ruang Web</title>
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <h1>Halo dari Ruang Web</h1>
  <p>Halaman ini disajikan dari index.html.</p>
</body>
</html>`],
  ["site/style.css", `body {
  max-width: 42rem;
  margin: 4rem auto;
  padding: 0 1.25rem;
  font: 1.15rem/1.65 system-ui, sans-serif;
  color: #182842;
  background: #edf4ff;
}`],
];
const createDemoFolder = ["PowerShell · folder proyek", `New-Item -ItemType Directory -Path .\\ruang-web\\site
Set-Location .\\ruang-web`];
const demoAddress = "http://127.0.0.1:8080/";

const practiceGuides = {
  docker: {
    title: "Tutorial Docker dari nol",
    outcome: "Hasil akhir berupa halaman HTML yang disajikan oleh Nginx di dalam container, dengan port host yang bisa diuji dari Windows.",
    requirements: "Windows dengan virtualisasi dan WSL 2 untuk latihan ini, Docker Desktop dengan Linux containers, serta port localhost 8080 yang tersedia.",
    chapters: [
      {
        title: "Build dan jalankan image",
        steps: [
          {
            title: "Siapkan Docker Desktop",
            body: "Ikuti panduan instalasi resmi untuk menyiapkan WSL 2 dan Docker Desktop. Buka Docker Desktop, tunggu engine berjalan, lalu buka PowerShell. Docker version menampilkan sisi Client dan Server. Container hello-world menguji akses engine dan registry.",
            code: [["PowerShell · cek instalasi", "wsl --status\ndocker version\ndocker run --rm hello-world"]],
          },
          {
            title: "Buat folder latihan dan halaman",
            body: "Bekerja dari folder induk pilihan Anda. Buat subfolder latihan, lalu simpan kedua contoh dengan nama yang ditampilkan. Folder site berisi berkas yang nanti disalin atau dipasang pada document root Nginx.",
            code: [createDemoFolder, ...demoSite],
          },
          {
            title: "Tulis Dockerfile dan buat image",
            body: "Simpan Dockerfile di samping folder site, lalu jalankan build dari ruang-web. Nginx menyediakan web server. COPY menempatkan isi folder site pada document root image.",
            code: [
              ["Dockerfile", "FROM nginx:stable-alpine\nCOPY site/ /usr/share/nginx/html/"],
              ["PowerShell · build image", "docker build -t ruang-html:1.0 .\ndocker image ls ruang-html"],
            ],
          },
          {
            title: "Jalankan container dan uji HTML",
            body: "Pemetaan port mengantar 127.0.0.1:8080 di Windows ke port 80 di container. Buka " + demoAddress + " di browser. HTTP 200 dan teks Halo dari Ruang Web menunjukkan bahwa image berisi halaman Anda. Jika port bentrok, ubah port host dan URL uji secara konsisten.",
            code: [[
              "PowerShell · run dan verifikasi",
              "docker run --name ruang-html --rm -d -p 127.0.0.1:8080:80 ruang-html:1.0\ndocker ps --filter name=ruang-html\ncurl.exe -fsS http://127.0.0.1:8080/\ncurl.exe -I http://127.0.0.1:8080/style.css\ndocker logs --tail 20 ruang-html",
            ]],
          },
        ],
      },
      {
        title: "Jalankan dengan Docker Compose",
        steps: [
          {
            title: "Deklarasikan layanan web",
            body: "Hentikan container dari langkah sebelumnya agar port 8080 tersedia. Buat compose.yaml di dalam ruang-web. Bind mount read-only membuat Nginx membaca folder site langsung dari komputer, jadi perubahan HTML bisa terlihat setelah browser dimuat ulang tanpa build ulang.",
            code: [
              ["PowerShell · hentikan container latihan", "docker stop ruang-html"],
              [
                "compose.yaml",
                'services:\n  web:\n    image: nginx:stable-alpine\n    ports:\n      - "127.0.0.1:8080:80"\n    volumes:\n      - "./site:/usr/share/nginx/html:ro"\n    restart: unless-stopped',
              ],
            ],
          },
          {
            title: "Cek konfigurasi dan hasil deploy",
            body: "Periksa konfigurasi, mulai layanan, lalu verifikasi kedua berkas lewat HTTP. Untuk latihan hosting melalui tunnel, biarkan layanan web berjalan. Ketika selesai, docker compose down menghentikan dan menghapus container serta jaringan proyek. Direktori site adalah berkas biasa di komputer Anda.",
            code: [
              [
                "PowerShell · jalankan Compose",
                "docker compose config\ndocker compose up -d\ndocker compose ps\ncurl.exe -I http://127.0.0.1:8080/\ncurl.exe -I http://127.0.0.1:8080/style.css\ndocker compose logs --tail 20 web",
              ],
              ["PowerShell · selesai berlatih", "docker compose down"],
            ],
          },
        ],
      },
    ],
    related: ["hosting"],
    sources: [
      ["Docker Desktop untuk Windows", "https://docs.docker.com/desktop/setup/install/windows-install/"],
      ["Pemetaan port Docker", "https://docs.docker.com/get-started/docker-concepts/running-containers/publishing-ports/"],
      ["Docker Compose up", "https://docs.docker.com/reference/cli/docker/compose/up/"],
    ],
  },
  proxmox: {
    title: "Tutorial Proxmox dari instalasi sampai web server",
    outcome: "Hasil akhir berupa VM Debian dengan Nginx yang menyajikan halaman HTML dan dapat dijangkau dari LAN.",
    requirements: "Mesin x86-64 dengan Intel VT-x atau AMD-V, disk khusus untuk instalasi, USB installer, LAN kabel, ISO Proxmox VE dan Debian, serta SCP atau OpenSSH Client pada komputer pengirim file.",
    chapters: [
      {
        title: "Siapkan host Proxmox VE",
        steps: [
          {
            title: "Instal hypervisor di mesin khusus",
            body: "Unduh ISO Proxmox VE resmi, tulis sebagai USB bootable, lalu boot mesin target dari USB. Pilih Install Proxmox VE, tentukan disk, zona waktu, kata sandi admin, email, dan antarmuka jaringan. Installer menghapus data pada disk yang dipilih. Periksa nama dan kapasitas disk sebelum menyetujui instalasi.",
          },
          {
            title: "Atur IP administrasi dan buka panel",
            body: "Gunakan IP yang belum dipakai pada LAN. Contoh host 192.168.1.10/24 dengan gateway 192.168.1.1 harus diganti menyesuaikan jaringan Anda. Setelah reboot, lepaskan USB dan buka URL panel dari perangkat di LAN. Masuk sebagai root dengan realm Linux PAM. Sertifikat bawaan dapat memunculkan peringatan pada akses pertama. Cocokkan IP dengan konsol host sebelum mempercayai sertifikat, atau pasang sertifikat tepercaya.",
            code: [["Browser · contoh panel LAN", "https://192.168.1.10:8006/"]],
          },
        ],
      },
      {
        title: "Buat dan instal VM Debian",
        steps: [
          {
            title: "Unggah ISO dan tentukan sumber daya VM",
            body: "Di panel, pilih storage yang mendukung ISO, biasanya local, lalu buka ISO Images dan unggah Debian. Pilih Create VM, beri nama web-debian, pilih ISO, dan gunakan contoh 2 vCPU, RAM 2 GB, serta disk virtual 16 GB. Pilih storage disk seperti local-lvm jika tersedia. Pilih NIC VirtIO dan bridge yang terhubung LAN, biasanya vmbr0.",
          },
          {
            title: "Boot Debian dan catat alamat tamu",
            body: "Buka Console VM dan mulai instalasi Debian. Kosongkan kata sandi root pada installer Debian agar pengguna pertama mendapat hak sudo. Buat pengguna webadmin dan pilih SSH server pada pemilihan perangkat lunak. Setelah instalasi, lepas ISO virtual dan reboot dari disk. Periksa IP IPv4 dan gateway dari dalam VM. Untuk rute tunnel jangka panjang, gunakan reservasi DHCP atau konfigurasi IP yang stabil pada jaringan Anda.",
            code: [["Shell Debian · alamat dan rute", "ip -4 -brief address\nip route"]],
          },
        ],
      },
      {
        title: "Sajikan halaman HTML dari VM",
        steps: [
          {
            title: "Pasang Nginx di Debian",
            body: "Perintah berikut dijalankan di konsol VM sebagai pengguna dengan hak sudo. Status active dan respons 200 di loopback menunjukkan bahwa web server berjalan di VM.",
            code: [[
              "Shell Debian · pasang dan cek Nginx",
              "sudo apt update\nsudo apt install -y nginx curl\nsudo systemctl enable --now nginx\nsystemctl is-active nginx\ncurl -I http://127.0.0.1/",
            ]],
          },
          {
            title: "Terbitkan berkas HTML dan uji dari LAN",
            body: "Siapkan index.html dan style.css di folder site seperti pada tutorial Hosting HTML. Dari PowerShell di folder ruang-web, kirim keduanya ke direktori pengguna VM melalui SCP. Ganti nama pengguna dan IP sesuai hasil instalasi. Dari konsol VM, salin berkas tersebut ke document root Nginx bawaan Debian dan uji HTTP dari dalam VM.",
            code: [
              [
                "PowerShell di folder ruang-web · salin ke VM",
                "scp .\\site\\index.html .\\site\\style.css webadmin@192.168.1.60:~/",
              ],
              [
                "Shell Debian di VM · siapkan document root",
                "sudo install -m 0644 ~/index.html ~/style.css /var/www/html/\ncurl -fsS http://127.0.0.1/\ncurl -I http://127.0.0.1/style.css",
              ],
            ],
          },
          {
            title: "Uji dari perangkat lain di LAN",
            body: "Ganti IP contoh dengan IP VM Anda dan buka URL di browser perangkat lain. Cari judul Halo dari Ruang Web. Jika uji lokal berjalan dan uji LAN gagal, periksa bridge, IP, aturan firewall, dan apakah port 80 bisa dijangkau dari perangkat itu.",
            code: [
              ["PowerShell di perangkat LAN", "Test-NetConnection 192.168.1.60 -Port 80\ncurl.exe -fsS http://192.168.1.60/"],
            ],
          },
          {
            title: "Hubungkan VM ke tutorial hosting",
            body: "Saat cloudflared berjalan di VM yang sama, URL origin Nginx adalah http://127.0.0.1:80. Jika konektor berjalan di mesin lain di LAN, gunakan IP VM seperti http://192.168.1.60 dan uji dari mesin konektor. Rute publik mengarah ke Nginx di VM. Panel administrasi port 8006 digunakan dari LAN.",
          },
        ],
      },
      {
        title: "Operasikan VM setelah instalasi",
        steps: [
          {
            title: "Periksa status VM dan service",
            body: "Di panel Proxmox, gunakan Summary untuk melihat CPU, RAM, disk, dan status VM. Nyalakan Start at boot pada VM bila web server harus hidup setelah host reboot. Dari konsol VM, periksa service Nginx secara terpisah karena status VM hanya menyatakan bahwa mesin virtual berjalan.",
          },
          {
            title: "Simpan backup sebelum perubahan besar",
            body: "Buat backup VM ke penyimpanan cadangan yang sudah dikonfigurasi dan uji pemulihannya ke VM latihan. Snapshot berguna untuk menandai kondisi sebelum perubahan bila storage mendukungnya. Backup di storage terpisah tetap penting untuk pemulihan saat disk utama bermasalah.",
          },
        ],
      },
    ],
    related: ["hosting"],
    sources: [
      ["Unduhan ISO Proxmox VE", "https://www.proxmox.com/en/downloads/proxmox-virtual-environment/iso"],
      ["Panduan administrasi Proxmox VE", "https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf"],
      ["Unduhan Debian", "https://www.debian.org/distrib/"],
      ["Panduan instalasi Debian", "https://www.debian.org/doc/manuals/debian-handbook/sect.installation-steps.en.html"],
    ],
  },
  hosting: {
    title: "Tutorial hosting HTML sampai bisa dibuka dari internet",
    outcome: "Siapkan folder HTML dan CSS, terbitkan melalui Cloudflare Pages atau Cloudflare Tunnel, lalu pastikan halaman dan aset bisa dibuka dari jaringan lain.",
    requirements: "Folder situs berisi berkas publik dan akun Cloudflare. Gunakan domain di Cloudflare jika ingin URL Tunnel sendiri. Pages menyediakan URL pages.dev untuk deployment.",
    chapters: [
      {
        title: "Siapkan dan uji halaman lokal",
        steps: [
          {
            title: "Simpan index.html dan aset",
            body: "Gunakan folder latihan baru atau lanjutkan folder site dari tutorial Docker. index.html harus berada di tingkat teratas folder yang akan disajikan. Gunakan alamat relatif seperti ./style.css agar aset ditemukan lewat URL publik. Samakan huruf besar dan kecil pada nama berkas.",
            code: [createDemoFolder, ...demoSite],
          },
          {
            title: "Uji halaman lewat HTTP",
            body: "Buka terminal dari ruang-web dan jalankan server pratinjau Python di bawah. Buka http://127.0.0.1:8080/ dari komputer sendiri. Jalankan curl di terminal kedua untuk memeriksa HTML dan CSS. Tekan Ctrl+C untuk menutup pratinjau sebelum memakai port itu untuk Nginx.",
            code: [
              ["PowerShell · pratinjau sementara", "py -3 -m http.server 8080 --bind 127.0.0.1 --directory site"],
              ["PowerShell · cek hasil pratinjau", "curl.exe -I http://127.0.0.1:8080/\ncurl.exe -I http://127.0.0.1:8080/style.css"],
            ],
          },
        ],
      },
      {
        title: "Pilihan A · Hosting statis dengan Cloudflare Pages",
        steps: [
          {
            title: "Unggah folder site",
            body: "Masuk ke Cloudflare, buka Workers & Pages, buat aplikasi Pages dengan Direct Upload, beri nama proyek, lalu unggah folder site. Bila memakai ZIP, letakkan index.html dan style.css di bagian teratas ZIP. Pilih Deploy site. Pages menyimpan dan menyajikan salinannya dari URL deployment berbentuk nama-proyek.pages.dev.",
          },
          {
            title: "Uji URL deployment dan sambungkan domain bila diperlukan",
            body: "Buka URL pages.dev yang diberikan dashboard. Untuk domain sendiri, tambahkan hostname dari menu Custom domains di proyek Pages dan ikuti pengaturan DNS yang ditampilkan. Gunakan hostname yang kosong jika domain utama sudah digunakan oleh layanan lain. Untuk apex domain pada Pages, gunakan zona dengan nameserver Cloudflare.",
          },
          {
            title: "Terbitkan perubahan baru",
            body: "Ubah halaman di komputer, uji lagi, lalu buat deployment baru dengan folder terbaru. Setelah deployment selesai, pengunjung tetap dapat membuka situs saat komputer pengunggah dimatikan.",
          },
        ],
      },
      {
        title: "Pilihan B · Cloudflare Tunnel ke web server sendiri",
        steps: [
          {
            title: "Jalankan origin yang menyajikan situs",
            body: "Gunakan Nginx dari tutorial Docker atau VM Debian dari tutorial Proxmox. Dari mesin yang menjalankan cloudflared, uji IP dan port origin sampai HTML dan CSS mendapat respons. Loopback 127.0.0.1 menunjuk ke mesin konektor itu sendiri.",
            code: [["PowerShell · uji origin Docker di mesin konektor", "curl.exe -I http://127.0.0.1:8080/\ncurl.exe -I http://127.0.0.1:8080/style.css"]],
          },
          {
            title: "Sambungkan konektor dan buat published application",
            body: "Pada Cloudflare, buka Networking lalu Tunnels. Pilih tunnel yang sudah tersambung, atau buat tunnel dan ikuti perintah instalasi cloudflared untuk sistem operasi Anda. Di Routes buat Published application. Gunakan subdomain khusus latihan, misalnya web pada domain sendiri, dan biarkan path kosong agar situs terbuka dari /. Masukkan Service URL http://127.0.0.1:8080 untuk contoh Docker pada mesin konektor. Gunakan IP VM dan port Nginx bila konektor berada di mesin lain. Simpan dan periksa rute DNS.",
            code: [[
              "Contoh rute · ganti hostname sesuai domain Anda",
              "Hostname: web.domain-anda\nPath: (kosong)\nService URL: http://127.0.0.1:8080",
            ]],
          },
          {
            title: "Periksa HTTPS dan ketersediaan origin",
            body: "Buka URL publik dengan HTTPS. Browser mengambil sertifikat dari layanan publik dan Cloudflare meneruskan trafik ke origin melalui tunnel. Origin dan cloudflared perlu tetap berjalan agar halaman bisa dibuka. Error 1033 menunjukkan konektor tunnel tidak tersedia. Respons 502 dari rute tunnel dapat berarti konektor tersambung tetapi gagal menghubungi origin. Uji Service URL dari mesin konektor dan cek log.",
          },
        ],
      },
      {
        title: "Buktikan halaman bisa dibuka dari luar jaringan",
        steps: [
          {
            title: "Uji dari data seluler atau perangkat di jaringan lain",
            body: "Matikan Wi-Fi pada ponsel dan buka URL HTTPS publik memakai data seluler, atau minta orang di jaringan lain membuka URL yang sama. Pastikan judul halaman terlihat dan CSS dimuat. Ganti URL contoh di bawah dengan URL proyek Anda sendiri.",
            code: [[
              "PowerShell · uji DNS, HTML dan CSS publik",
              "Resolve-DnsName web.domain-anda\ncurl.exe -IL https://web.domain-anda/\ncurl.exe -IL https://web.domain-anda/style.css",
            ]],
          },
          {
            title: "Cari penyebab jika situs hanya berjalan di komputer sendiri",
            body: "Saat domain gagal ditemukan, cek DNS dan pemilihan hostname. Jika HTML muncul tanpa gaya, buka Network pada DevTools dan cari status CSS atau gambar. Untuk 404 pada root Pages, periksa posisi index.html dalam folder unggahan. Untuk 502 tunnel, verifikasi port dan proses origin. Bagikan URL HTTPS setelah pengujian dari jaringan lain lulus.",
          },
        ],
      },
    ],
    related: ["docker", "proxmox"],
    sources: [
      ["Cloudflare Pages · Direct Upload", "https://developers.cloudflare.com/pages/get-started/direct-upload/"],
      ["Cloudflare Pages · Domain kustom", "https://developers.cloudflare.com/pages/configuration/custom-domains/"],
      ["Cloudflare Tunnel · Published applications", "https://developers.cloudflare.com/tunnel/get-started/"],
      ["Cloudflare Tunnel · Troubleshooting", "https://developers.cloudflare.com/tunnel/troubleshooting/"],
    ],
  },
};
