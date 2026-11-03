from labcore.exercises import integer, records


def run(db, data, context):
    account = data.get("account")
    if account not in {"alice", "bob"}:
        raise ValueError("Akun fixture hanya alice atau bob.")
    window = integer(data, "window", 1, 60) * 60
    rows = sorted((row for row in records(db, "log") if row["account"] == account), key=lambda row: row["second"])
    chains = []
    for success in (row for row in rows if row["event"] == "login_success"):
        failures = [row for row in rows if row["event"] == "login_failed" and row["ip"] == success["ip"]
                    and success["second"] - window <= row["second"] < success["second"]]
        for role in (row for row in rows if row["event"] == "role_change" and row["ip"] == success["ip"] and row["second"] > success["second"]):
            exports = [row for row in rows if row["event"] == "data_export" and row["ip"] == role["ip"]
                       and role["second"] < row["second"] <= success["second"] + window]
            if len(failures) >= 3 and exports:
                chains.append([failures[0]["id"], success["id"], role["id"], exports[0]["id"]])
    return dict(title="Rantai insiden terindikasi" if chains else "Belum ada rantai yang cocok",
                detail=f"{len(chains)} rantai cocok dengan rule gagal → sukses → role → export. Korelasi perlu investigasi lanjutan.",
                rows=rows, trace="Bukti rantai: " + repr(chains))
