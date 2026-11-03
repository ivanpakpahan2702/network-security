from labcore.runtime import shell_emulator


def run(db, data, context):
    # RENTAN: satu string berisi sintaks dan data tidak tepercaya.
    command = "ping " + data.get("host", "")[:512]
    output = shell_emulator(command)
    return dict(title="Perintah string dievaluasi", detail=output,
                trace=command + "\n\nInterpreter ini emulator terbatas, bukan shell OS.")
