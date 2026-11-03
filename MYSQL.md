# Pilihan SQLite atau MySQL/MariaDB

**HeidiSQL adalah client pengelola database.** MySQL/MariaDB adalah server database, sedangkan
SQLite menyimpan database dalam berkas. Anda dapat memakai HeidiSQL untuk membuka MySQL lab ini.

## 1. Siapkan server dan akun lab

Gunakan MySQL yang sudah Anda instal, atau service MySQL/MariaDB pada XAMPP. Jalankan servicenya
melalui pengelola service yang biasa digunakan. Aplikasi tidak menyalakan, mengganti password,
atau mengubah database lain pada server tersebut.

Buka HeidiSQL atau client SQL dengan akun administrator. Contoh pembuatan akun lokal khusus lab:

```sql
CREATE USER 'security_lab'@'127.0.0.1' IDENTIFIED BY 'GANTI_PASSWORD_LAB_ANDA';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX
ON `security\_lab\_%`.* TO 'security_lab'@'127.0.0.1';
```

Gunakan hostname akun yang sesuai dengan sumber koneksi server. Beberapa instalasi memetakan
koneksi lokal sebagai `localhost`; jika demikian buat/grant akun `'security_lab'@'localhost'`.
Saat aplikasi dan MySQL berada pada mesin/container berbeda, gunakan sumber koneksi yang sesuai.
Pola grant di atas hanya mencakup nama database dengan awalan literal `security_lab_`.
User runtime tidak memerlukan hak administrator, FILE, DROP, atau akses ke database aplikasi lain.
Jika prefix diubah, sesuaikan pola grant. Jangan menjalankan contoh CREATE USER bila akun tersebut
sudah ada; gunakan akun lab yang tersedia dan sesuaikan konfigurasi koneksinya.

## 2. Isi koneksi

Salin konfigurasi contoh:

```powershell
Copy-Item database.example.toml database.local.toml
```

Isi `database.local.toml` dengan konfigurasi server Anda:

```toml
[database]
backend = "mysql"

[mysql]
host = "127.0.0.1"
port = 3306
user = "security_lab"
password = "GANTI_PASSWORD_LAB_ANDA"
prefix = "security_lab"
```

Prefix berisi 1–20 karakter huruf kecil/angka/underscore dan diawali huruf. Password juga dapat
dibaca dari environment `SECURITY_LAB_MYSQL_PASSWORD`; nilai environment mengalahkan nilai berkas.
Berkas lokal diabaikan Git. Jangan menaruh kredensial di screenshot atau laporan praktik.

## 3. Pilih backend dan jalankan

Klik `start-lab.bat`: **1 = SQLite**, **2 = MySQL/MariaDB**. Pilihan menu mengalahkan backend dalam TOML.
Atau jalankan langsung:

```powershell
.\start-lab.bat --db mysql
.\start-lab.bat --db sqlite
# Shortcut MySQL
.\start-mysql.bat
# Konfigurasi lain
.\start-lab.bat --db mysql --db-config .runtime\kelas-b.toml
```

Launcher memasang driver opsional jika belum tersedia. Untuk menjalankan Python langsung:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-mysql.txt
.\.venv\Scripts\python.exe run.py --db mysql
.\.venv\Scripts\python.exe run.py --db mysql --lab 01_sql_injection 34_race_condition
.\.venv\Scripts\python.exe labs\01_sql_injection\app.py --db mysql
```

`run.py` tanpa `--db` mengikuti backend pada `database.local.toml`, atau SQLite jika berkas tidak ada.
Factory Python menerima `database_settings=DatabaseSettings(...)`; tanpa parameter tersebut factory
tetap memakai SQLite agar pemakaian programatik dan tes tidak diam-diam berganti backend.

Jika server tidak tersedia atau izin kurang, startup melaporkan error. Tidak ada fallback diam-diam
ke SQLite. Hentikan proses lama dahulu; kemudian buka dashboard seperti biasa pada port 5100.
Halaman menampilkan **Database aktif: MySQL** atau **Database aktif: SQLite**.

## 4. Lihat tabel melalui HeidiSQL

Tambahkan sesi HeidiSQL dengan jenis koneksi **MariaDB or MySQL (TCP/IP)** dan isikan host, user,
password, serta port yang sama dengan konfigurasi. Setelah lab pertama kali berjalan, refresh daftar
database. Dengan prefix default, Anda akan melihat:

| Database | Isi |
| --- | --- |
| `security_lab_dashboard` | Checklist, nilai kuis, dan catatan belajar |
| `security_lab_01_sql_injection` | Akun dummy dan percobaan SQL injection |
| `security_lab_03_stored_xss` | Komentar untuk demo stored XSS |
| `security_lab_34_race_condition` | Wallet dummy untuk dua transaksi bersamaan |
| `security_lab_35_idempotency` | Pembayaran dan idempotency key |
| `security_lab_<ID-lab-lain>` | Data terpisah milik lab tersebut |

Semua 40 lab dapat memakai MySQL. Jika hanya menjalankan sebagian lab, hanya schema yang dibutuhkan
yang dibuat. Tabel memakai InnoDB dan utf8mb4 dengan perbandingan teks case-sensitive sesuai fixture.
Kolom `accounts.password_demo` dan MD5 adalah data dummy yang sengaja dipakai untuk pelajaran.

## Perilaku dan perbedaan

- Beralih SQLite ↔ MySQL tidak memindahkan data atau progres secara otomatis. Data backend lama
  tetap tersedia saat Anda kembali ke backend itu dengan konfigurasi semula.
- Setiap proses server memilih satu backend saat startup. Form eksperimen tidak dapat mengganti
  host, user, password, prefix, atau database server.
- `--data-dir` mengatur fixture lokal/kunci sesi; untuk dataset MySQL terpisah, gunakan prefix lain.
  `--port-offset` hanya menggeser port HTTP, bukan port atau nama database.
- Reset hanya memulihkan tabel/fixture lab yang dipilih; tidak menjalankan DROP DATABASE atau
  menghapus progres dashboard.
- Query rentan lab 01 tetap benar-benar digabung sebagai SQL. Pada mode diperbaiki, adapter
  mengubah placeholder `?` menjadi `%s` milik PyMySQL lalu mengirim nilai sebagai parameter.
  Query tanpa parameter tidak ditulis ulang. MULTI_STATEMENTS dan LOCAL INFILE tidak diaktifkan.
- Kontrol transaksi menggunakan `BEGIN IMMEDIATE` pada SQLite; MySQL memakai transaksi InnoDB,
  conditional UPDATE, dan row lock untuk operasi check-then-insert/rate limit.
- MySQL dan SQLite memiliki dialek SQL berbeda. Payload default dirancang bekerja pada keduanya;
  fungsi SQL khusus satu engine belum tentu tersedia pada engine lain.

## Pengujian

Implementasi diverifikasi dengan SQLite, MySQL 8.4.13, dan MariaDB 10.3.39.
Suite SQLite mencakup 63 tes; 58 skenario perilaku database diverifikasi pada masing-masing
server MySQL/MariaDB. UI MySQL juga diuji dengan 16 pemeriksaan Chrome melalui IP LAN,
termasuk kuis, CSRF/CORS, upload, race condition, dan capstone.
Pembuatan schema pertama untuk semua 40 lab dapat membutuhkan waktu; launcher menampilkan
progres setiap 10 lab. Schema dan data yang sudah ada dipakai kembali pada restart berikutnya.

Tes SQLite tetap dapat dijalankan tanpa driver/server MySQL:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests
```

Untuk suite MySQL, gunakan **server uji** dan berkas koneksi eksplisit. Suite membuat schema
`qa_<acak>_<lab>` dan menghapus hanya schema yang dibuatnya. Akun pengujian memerlukan CREATE,
DROP, SELECT, INSERT, UPDATE, DELETE, dan INDEX pada pola `qa\_%`.*.

```powershell
.\.venv\Scripts\python.exe -X utf8 tests\mysql_check.py --db-config .runtime\mysql-test.toml
.\.venv\Scripts\python.exe -X utf8 tests\browser_check.py --port-offset 1000 --db-config .runtime\mysql-test.toml
.\.venv\Scripts\python.exe -X utf8 tests\launcher_check.py --db-config .runtime\mysql-test.toml
```

Suite memeriksa perilaku yang sama pada seluruh lab, kuis, reset, persistensi, dan batas LAN.
Koneksi/izin yang salah menghasilkan kegagalan tes, bukan tes yang dilewati.

Referensi implementasi: [PyMySQL Connection](https://pymysql.readthedocs.io/en/latest/modules/connections.html),
[MySQL locking reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-locking-reads.html),
[MySQL INSERT](https://dev.mysql.com/doc/refman/8.4/en/insert.html).
