import hashlib
import sqlite3
import threading
from functools import lru_cache

from werkzeug.security import generate_password_hash
from labcore.dbconfig import MySQLTarget
from labcore.mysql_schema import create_schema

_seed_lock = threading.Lock()
SCRYPT = "scrypt:32768:8:3"


class ClosingConnection(sqlite3.Connection):
    """Context manager SQLite standar commit/rollback tetapi juga menutup file."""
    dialect = 'sqlite'
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


@lru_cache(maxsize=1)
def seed_hashes():
    return [generate_password_hash(password, method=SCRYPT) for password in
            ("LabAdmin!2026", "LabUser!2026", "LabUser!2026")]


def connect(path):
    if isinstance(path, MySQLTarget):
        from labcore.mysql_backend import MySQLConnection
        return MySQLConnection(path)
    db = sqlite3.connect(path, timeout=10, factory=ClosingConnection)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def prepare_database(target):
    if isinstance(target, MySQLTarget):
        from labcore.mysql_backend import prepare
        prepare(target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)


def database_errors():
    # SQLite-only installation does not require the optional MySQL driver.
    try:
        import pymysql
        return (sqlite3.Error, pymysql.Error)
    except ImportError:
        return (sqlite3.Error,)


def initialize(path, reset=False):
    prepare_database(path)
    with _seed_lock, connect(path) as db:
        create_schema(db, 'base', """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                password_demo TEXT NOT NULL, md5 TEXT NOT NULL, password_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY, mode TEXT NOT NULL, body TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY, owner TEXT NOT NULL, body TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS wallets (mode TEXT PRIMARY KEY, balance INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY, mode TEXT, username TEXT, occurred REAL, success INTEGER);
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY, mode TEXT, name TEXT, body BLOB, mime TEXT);
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, occurred TEXT DEFAULT CURRENT_TIMESTAMP,
                mode TEXT, title TEXT, status INTEGER);
            CREATE TABLE IF NOT EXISTS services (
                name TEXT PRIMARY KEY, port INTEGER, banner TEXT);
        """)
        if reset:
            for table in ("accounts", "comments", "invoices", "wallets", "attempts", "uploads", "events", "services"):
                db.execute(f"DELETE FROM {table}")  # table names are fixed server constants
        if not db.execute("SELECT 1 FROM accounts").fetchone():
            hashes = seed_hashes()
            for user_id, username, password, password_hash in zip(
                    (1, 2, 3), ("admin", "alice", "bob"),
                    ("LabAdmin!2026", "LabUser!2026", "LabUser!2026"), hashes):
                db.execute("INSERT INTO accounts VALUES (?, ?, ?, ?, ?)",
                           (user_id, username, password, hashlib.md5(password.encode()).hexdigest(), password_hash))
            db.executemany("INSERT INTO invoices VALUES (?, ?, ?)", [
                (1, "alice", "Invoice Alice: pelatihan Rp250.000"),
                (2, "bob", "RAHASIA DUMMY BOB: kontrak internal Rp9.000.000")])
            db.executemany("INSERT INTO wallets VALUES (?, ?)", [("vulnerable", 1000), ("secure", 1000)])
            db.executemany("INSERT INTO services VALUES (?, ?, ?)", [
                ("web", 443, "HTTPS storefront dummy"),
                ("database", 5432, "PostgreSQL dummy - bukan database lab sebenarnya"),
                ("admin", 22, "SSH management dummy")])
