import ipaddress

from labcore.runtime import argv_emulator


def run(db, data, context):
    # DIPERBAIKI: validasi IP dan pemisahan argumen dari sintaks.
    host = str(ipaddress.ip_address(data.get("host", "")))
    arguments = ["ping", host]
    output = argv_emulator(arguments)
    # Untuk OS nyata: subprocess.run([...], shell=False, timeout=2, ...).
    return dict(title="Argumen terstruktur diterima", detail=output,
                trace=repr(arguments) + "\nTidak ada string yang dievaluasi oleh shell.")
