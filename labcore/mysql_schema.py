"""Schema MySQL/MariaDB eksplisit; tabel transaksi memakai InnoDB."""
import re
SCHEMAS = {
    'base': '''
        CREATE TABLE IF NOT EXISTS accounts (
            id BIGINT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(256) UNIQUE NOT NULL,
            password_demo TEXT NOT NULL, md5 VARCHAR(32) NOT NULL, password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS comments (id BIGINT PRIMARY KEY AUTO_INCREMENT, mode VARCHAR(16) NOT NULL, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS invoices (id BIGINT PRIMARY KEY AUTO_INCREMENT, owner VARCHAR(256) NOT NULL, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wallets (mode VARCHAR(16) PRIMARY KEY, balance BIGINT NOT NULL);
        CREATE TABLE IF NOT EXISTS attempts (id BIGINT PRIMARY KEY AUTO_INCREMENT, mode VARCHAR(16), username VARCHAR(256), occurred DOUBLE, success INTEGER);
        CREATE TABLE IF NOT EXISTS uploads (id BIGINT PRIMARY KEY AUTO_INCREMENT, mode VARCHAR(16), name TEXT, body LONGBLOB, mime VARCHAR(256));
        CREATE TABLE IF NOT EXISTS events (id BIGINT PRIMARY KEY AUTO_INCREMENT, occurred TIMESTAMP DEFAULT CURRENT_TIMESTAMP, mode VARCHAR(16), title TEXT, status INTEGER);
        CREATE TABLE IF NOT EXISTS services (name VARCHAR(64) PRIMARY KEY, port INTEGER, banner TEXT);
        CREATE TABLE IF NOT EXISTS lab_locks (name VARCHAR(64) PRIMARY KEY);
    ''',
    'exercises': '''
        CREATE TABLE IF NOT EXISTS exercise_records (kind VARCHAR(64), name VARCHAR(128), payload TEXT NOT NULL, PRIMARY KEY(kind,name));
        CREATE TABLE IF NOT EXISTS exercise_state (mode VARCHAR(16), name VARCHAR(128), payload TEXT NOT NULL, PRIMARY KEY(mode,name));
        CREATE TABLE IF NOT EXISTS profiles (mode VARCHAR(16) PRIMARY KEY, display_name TEXT, bio TEXT, role VARCHAR(32) NOT NULL);
        CREATE TABLE IF NOT EXISTS race_wallets (id VARCHAR(32) PRIMARY KEY, balance BIGINT NOT NULL);
        CREATE TABLE IF NOT EXISTS payments (id BIGINT PRIMARY KEY AUTO_INCREMENT, mode VARCHAR(16) NOT NULL, request_id VARCHAR(64) NOT NULL, amount INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS idempotency (mode VARCHAR(16), request_id VARCHAR(64), amount INTEGER NOT NULL, payment_id BIGINT NOT NULL, PRIMARY KEY(mode,request_id));
    ''',
    'dashboard': '''
        CREATE TABLE IF NOT EXISTS progress (lab_id VARCHAR(64) PRIMARY KEY, completed INTEGER NOT NULL);
    ''',
    'learning': '''
        CREATE TABLE IF NOT EXISTS lesson_results (
            learner VARCHAR(64), module VARCHAR(64), best_score INTEGER, last_score INTEGER, attempts INTEGER,
            updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(learner,module));
        CREATE TABLE IF NOT EXISTS lesson_notes (
            learner VARCHAR(64), module VARCHAR(64), note TEXT, updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(learner,module));
    ''',
}


def create_schema(db, group, sqlite_script):
    if db.dialect == 'sqlite':
        db.executescript(sqlite_script)
    else:
        existing = {row[0] for row in db.execute('SHOW TABLES')}
        for statement in SCHEMAS[group].split(';'):
            if statement.strip():
                table = re.search(r'CREATE TABLE IF NOT EXISTS ([a-z_]+)', statement)[1]
                if table not in existing:
                    db.execute(statement.strip() + ' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin')
        if group == 'base':
            db.execute("INSERT INTO lab_locks (name) VALUES ('login'),('payments') ON DUPLICATE KEY UPDATE name=name")
            db.commit()
