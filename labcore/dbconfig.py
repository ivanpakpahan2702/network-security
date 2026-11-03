"""Konfigurasi backend eksplisit. Factory tanpa konfigurasi tetap memakai SQLite."""
import os
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class DatabaseSettings:
    backend: str = "sqlite"
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "security_lab"
    password: str = field(default="", repr=False)
    prefix: str = "security_lab"

    def __post_init__(self):
        if any(not isinstance(value, str) for value in (self.backend, self.host, self.user, self.password, self.prefix)):
            raise ValueError("Backend, host, user, password, dan prefix harus berupa teks.")
        if self.backend not in {"sqlite", "mysql"}:
            raise ValueError("Backend harus sqlite atau mysql.")
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,19}", self.prefix):
            raise ValueError("Prefix MySQL harus 1–20 karakter: huruf kecil, angka, underscore; diawali huruf.")
        if type(self.port) is not int or not 1 <= self.port <= 65535:
            raise ValueError("Port MySQL harus angka antara 1 dan 65535.")
        if not self.host or not self.user:
            raise ValueError("Host dan user MySQL wajib diisi.")


@dataclass(frozen=True)
class MySQLTarget:
    settings: DatabaseSettings = field(repr=False)
    schema: str


def load_settings(backend=None, config_file=None):
    explicit = config_file is not None
    path = Path(config_file) if explicit else Path(__file__).resolve().parents[1] / "database.local.toml"
    config = {}
    if path.is_file():
        try:
            with path.open("rb") as stream:
                config = tomllib.load(stream)
        except tomllib.TOMLDecodeError as error:
            raise ValueError("Format TOML database tidak valid. Cocokkan dengan database.example.toml.") from None
    elif explicit:
        raise ValueError(f"Berkas konfigurasi tidak ditemukan: {path}")
    database, mysql = config.get("database", {}), config.get("mysql", {})
    if not isinstance(database, dict) or not isinstance(mysql, dict):
        raise ValueError("Konfigurasi harus memakai bagian [database] dan [mysql].")
    chosen = backend or database.get("backend", "sqlite")
    if chosen == "sqlite":
        return DatabaseSettings()
    return DatabaseSettings(backend=chosen, host=mysql.get("host", "127.0.0.1"),
                            port=mysql.get("port", 3306), user=mysql.get("user", "security_lab"),
                            password=os.environ.get("SECURITY_LAB_MYSQL_PASSWORD", mysql.get("password", "")),
                            prefix=mysql.get("prefix", "security_lab"))


def target_for(sqlite_path, scope, settings=None):
    settings = settings or DatabaseSettings()
    if settings.backend == "sqlite":
        return sqlite_path
    # Scope adalah ID katalog server, tidak berasal dari input eksperimen.
    if not re.fullmatch(r"[a-z0-9_]{1,42}", scope):
        raise ValueError("Scope database lab tidak valid.")
    return MySQLTarget(settings, settings.prefix + "_" + scope)


def describe(target):
    if isinstance(target, MySQLTarget):
        return {"DB_BACKEND": "mysql", "DB_LABEL": "MySQL", "DATABASE_DISPLAY": target.schema}
    return {"DB_BACKEND": "sqlite", "DB_LABEL": "SQLite", "DATABASE_DISPLAY": str(target)}


def add_database_arguments(parser):
    parser.add_argument("--db", choices=("sqlite", "mysql"), help="Backend database (default SQLite atau database.local.toml)")
    parser.add_argument("--db-config", type=Path, help="Konfigurasi koneksi TOML; default database.local.toml")
