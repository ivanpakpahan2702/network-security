"""Fixture dan state SQLite untuk praktik baru, tanpa efek pada konfigurasi host."""
import json
import re
from labcore.mysql_schema import create_schema
from labcore.dbqueries import insert_missing, upsert

EVIDENCE = [
    dict(id="E01", time="2026-01-15T08:00:00Z", source="inventory", host="web-01", account="alice", event="Akun alice adalah user biasa; aplikasi publik menyimpan invoice per pemilik."),
    dict(id="E02", time="2026-01-15T08:02:00Z", source="auth", host="web-01", account="alice", event="Lima login gagal dari 192.0.2.66; wawancara dummy mengonfirmasi password digunakan ulang di layanan lain."),
    dict(id="E03", time="2026-01-15T08:04:00Z", source="auth", host="web-01", account="alice", event="Login sukses dari 192.0.2.66 tanpa MFA."),
    dict(id="E04", time="2026-01-15T08:05:00Z", source="app", host="web-01", account="alice", event="GET /invoice/2 memberi HTTP 200; invoice 2 milik bob. Tidak ada pemeriksaan owner."),
    dict(id="E05", time="2026-01-15T08:06:00Z", source="egress", host="web-01", account="alice", event="Ekspor 8 MiB ke tujuan fixture 203.0.113.66 yang tidak terdaftar dalam kebijakan egress."),
]

LOGS = [
    *[dict(id=f"A{i}", second=i * 10, source="auth", account="alice", host="web-01", event="login_failed", ip="192.0.2.66") for i in range(1, 6)],
    dict(id="A6", second=120, source="auth", account="alice", host="web-01", event="login_success", ip="192.0.2.66"),
    dict(id="A7", second=180, source="audit", account="alice", host="web-01", event="role_change", ip="192.0.2.66"),
    dict(id="A8", second=240, source="proxy", account="alice", host="web-01", event="data_export", ip="192.0.2.66"),
    dict(id="B1", second=10, source="auth", account="bob", host="web-01", event="login_failed", ip="192.0.2.30"),
    dict(id="B2", second=1800, source="auth", account="bob", host="web-01", event="login_success", ip="192.0.2.30"),
    dict(id="B3", second=1850, source="app", account="bob", host="web-01", event="view_own_invoice", ip="192.0.2.30"),
]


def initialize_exercises(db):
    create_schema(db, 'exercises', """
        CREATE TABLE IF NOT EXISTS exercise_records (kind TEXT, name TEXT, payload TEXT NOT NULL, PRIMARY KEY(kind,name));
        CREATE TABLE IF NOT EXISTS exercise_state (mode TEXT, name TEXT, payload TEXT NOT NULL, PRIMARY KEY(mode,name));
        CREATE TABLE IF NOT EXISTS profiles (mode TEXT PRIMARY KEY, display_name TEXT, bio TEXT, role TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS race_wallets (id TEXT PRIMARY KEY, balance INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, mode TEXT NOT NULL, request_id TEXT NOT NULL, amount INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS idempotency (mode TEXT, request_id TEXT, amount INTEGER NOT NULL, payment_id INTEGER NOT NULL, PRIMARY KEY(mode,request_id));
    """)
    fixtures = [
        ("route", "0-default", dict(prefix="0.0.0.0/0", next_hop="192.0.2.1", interface="wan")),
        ("route", "1-internal", dict(prefix="10.20.0.0/16", next_hop="10.0.0.2", interface="core")),
        ("route", "2-specific", dict(prefix="10.20.1.0/24", next_hop="10.0.0.3", interface="server-vlan")),
        ("arp_binding", "gateway", dict(ip="10.10.10.1", mac="02:00:00:00:00:01", switch_port="uplink-1")),
        ("conntrack", "browser", dict(source_ip="198.51.100.20", source_port=443, destination_port=62000, private="10.0.0.10:49152", state="ESTABLISHED")),
    ]
    fixtures += [("evidence", row["id"], row) for row in EVIDENCE]
    fixtures += [("log", row["id"], row) for row in LOGS]
    # Ground truth labels hanya dipakai untuk evaluasi, bukan input algoritma deteksi.
    for index, (source, ports, times, attack) in enumerate((
            ("192.0.2.66", [22,23,80,443,445,3389], [0,2,4,6,8,10], True),
            ("192.0.2.30", [80,443,8080], [0,3,6], False),
            ("192.0.2.40", [22,80,443,445,3389], [0,120,240,360,480], False))):
        for j, (port, second) in enumerate(zip(ports, times)):
            fixtures.append(("ids", f"{index}-{j}", dict(source=source, destination="192.0.2.20", port=port, second=second, syn=True, attack=attack)))
    labels = ["mzxw6ytboi3gk4tfon2he5dvm5wwk3tb", "nbswy3dpeb3w64tmmq2gk3tfnrxxezlf", "on2g65dfnz2gk4ttmfxgk3tug5qwy3df",
              "ifbegryse5tgw2lpnz2hk3tpo5tgc3tu", "jbswy3dpfqqfo33snrscc2dpmfzgk3tg", "orsxg5banruw4z3fob2gk3tfoj2gc3lt"]
    for index, label in enumerate(labels):
        fixtures.append(("dns_log", f"t{index}", dict(domain="telemetry.lab.test", label=label, approved=False)))
        fixtures.append(("dns_log", f"c{index}", dict(domain="cdn.lab.test", label=label[::-1], approved=True)))
    fixtures.append(("dns_log", "normal", dict(domain="portal.lab.test", label="www", approved=True)))
    for kind, name, payload in fixtures:
        insert_missing(db, 'exercise_records', dict(kind=kind, name=name, payload=json.dumps(payload)), ('kind', 'name'))
    for mode in ('vulnerable', 'secure'):
        insert_missing(db, 'profiles', dict(mode=mode, display_name='Alice', bio='Peserta lab', role='user'), ('mode',))
    db.commit()


def records(db, kind):
    return [json.loads(row[0]) for row in db.execute("SELECT payload FROM exercise_records WHERE kind=? ORDER BY name", (kind,))]


def evidence_bytes(db):
    """Representasi identik untuk unduhan dan hash chain-of-custody latihan."""
    return (json.dumps(records(db, "evidence"), sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def state(db, mode, name, default):
    row = db.execute("SELECT payload FROM exercise_state WHERE mode=? AND name=?", (mode, name)).fetchone()
    return json.loads(row[0]) if row else default


def save_state(db, mode, name, value):
    upsert(db, 'exercise_state', dict(mode=mode, name=name, payload=json.dumps(value)), ('mode', 'name'))


def json_object(raw):
    if len(raw) > 4096:
        raise ValueError("JSON maksimal 4096 karakter.")
    try:
        value = json.loads(raw)
    except (ValueError, RecursionError) as error:
        raise ValueError("JSON tidak valid.") from error
    if not isinstance(value, dict):
        raise ValueError("Input harus objek JSON.")
    return value


def integer(data, key, low, high):
    value = int(data.get(key, "0"))
    if not low <= value <= high:
        raise ValueError(f"{key} harus berada antara {low} dan {high}.")
    return value


def tokens(value, choices):
    values = [item.strip().lower() for item in value.split(",") if item.strip()]
    if len(values) > 32 or any(item not in choices for item in values):
        raise ValueError("Pilihan tidak dikenal atau terlalu banyak langkah.")
    return values


def validate_mac(value):
    if not re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", value):
        raise ValueError("MAC harus memiliki enam pasangan hex.")
    return value.lower()
