import os

def filter_commands(commands: list) -> list:
    filtered = []
    for cmd in commands:
        cmd_clean = cmd.strip()
        lower_cmd = cmd_clean.lower()
        if (lower_cmd.startswith("serviewcommands:") or
            lower_cmd.startswith("user view commands:") or
            lower_cmd.startswith("system view commands:") or
            lower_cmd == "[ap7739]system"):
            continue
        if cmd_clean == "?":
            continue
        filtered.append(cmd)
    return filtered

def save_tree_features(modelo: str, dicionario: dict) -> None:
    os.makedirs("resource", exist_ok=True)
    firmware = str(dicionario.get("version_data", ["unknown"])[0]).replace(".", "_").replace(",", "")
    
    guest1 = filter_commands(dicionario.get("commands_guest1", []))
    guest2 = filter_commands(dicionario.get("commands_guest2", []))
    guest3 = filter_commands(dicionario.get("commands_guest3", []))
    
    sys1 = filter_commands(dicionario.get("commands_sys1", []))
    sys2 = filter_commands(dicionario.get("commands_sys2", []))
    sys3 = filter_commands(dicionario.get("commands_sys3", []))
    if sys1 and sys1[0].strip().lower() == "system":
        sys1 = sys1[1:]
    
    file_path = f"resource/Commands_{modelo}_version_{firmware}.txt"
    
    def normalize_command(command: str) -> str:
        return command.replace("<1-253>", "<X>").replace("<1-255>", "<Y>")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("Comandos modo não privilegiado:\n")
        for i, g1 in enumerate(guest1):
            f.write(g1 + "\n")
            prefix1 = "    " if i == len(guest1) - 1 else "│   "
            children2 = [cmd for cmd in guest2 if normalize_command(cmd).startswith(g1 + " ")]
            for j, g2 in enumerate(children2):
                connector2 = "└── " if j == len(children2) - 1 else "├── "
                linha_g2 = g2[len(g1) + 1:]
                f.write(prefix1 + connector2 + linha_g2 + "\n")
                if "Nostoragemediumsupportsthisoperation" in g2 or "<cr>" in g2:
                    continue
                prefix2 = prefix1 + ("    " if j == len(children2) - 1 else "│   ")
                children3 = [cmd for cmd in guest3 if normalize_command(cmd).startswith(g2 + " ")]
                for k, g3 in enumerate(children3):
                    connector3 = "└── " if k == len(children3) - 1 else "├── "
                    linha_g3 = g3[len(g2) + 1:]
                    f.write(prefix2 + connector3 + linha_g3 + "\n")
                    if "Such" in g3 or "<cr>" in g3:
                        continue

        f.write("\nComandos Modo System-view:\n")
        for i, s1 in enumerate(sys1):
            f.write(s1 + "\n")
            prefix1 = "    " if i == len(sys1) - 1 else "│   "
            children2 = [
                cmd for cmd in sys2
                if normalize_command(cmd).startswith(s1 + " ") and 
                   normalize_command(cmd)[len(s1) + 1:].strip().lower() != "[ap7739]system"
            ]
            for j, s2 in enumerate(children2):
                connector2 = "└── " if j == len(children2) - 1 else "├── "
                linha_s2 = s2[len(s1) + 1:]
                f.write(prefix1 + connector2 + linha_s2 + "\n")
                prefix2 = prefix1 + ("    " if j == len(children2) - 1 else "│   ")
                if "<cr>" in s2:
                    continue
                children3 = [cmd for cmd in sys3 if normalize_command(cmd).startswith(s2 + " ")]
                for k, s3 in enumerate(children3):
                    connector3 = "└── " if k == len(children3) - 1 else "├── "
                    linha_s3 = s3[len(s2) + 1:]
                    f.write(prefix2 + connector3 + linha_s3 + "\n")
                    if "<cr>" in s3:
                        continue



                #     # Nível 4
                #     children4 = [cmd for cmd in guest4 if normalize_command(cmd).startswith(g3 + " ")]
                #     for l, g4 in enumerate(children4):
                #         connector4 = "└── " if (l == len(children4) - 1) else "├── "
                #         linha_g4 = g4[len(g3) + 1:]
                #         f.write(prefix3 + connector4 + linha_g4 + "\n")
                #         if "Such" in g4 or "<cr>" in g4 or "TEXT" in g4:
                #             continue
                #         prefix4 = prefix3 + ("    " if (l == len(children4) - 1) else "│   ")

                #         # Nível 5
                #         children5 = [cmd for cmd in guest5 if normalize_command(cmd).startswith(g4 + " ")]
                #         for m, g5 in enumerate(children5):
                #             connector5 = "└── " if (m == len(children5) - 1) else "├── "
                #             linha_g5 = g5[len(g4) + 1:]
                #             f.write(prefix4 + connector5 + linha_g5 + "\n")
                #             if "TEXT" in g5 or "<cr>" in g5:
                #                 continue

       
                #     # Nível 4
                #     children4 = [cmd for cmd in sys4 if normalize_command(cmd).startswith(s3 + " ")]
                #     for l, s4 in enumerate(children4):
                #         connector4 = "└── " if (l == len(children4) - 1) else "├── "
                #         linha_s4 = s4[len(s3) + 1:]
                #         f.write(prefix3 + connector4 + linha_s4 + "\n")
                #         prefix4 = prefix3 + ("    " if (l == len(children4) - 1) else "│   ")

                #         # Nível 5
                #         children5 = [cmd for cmd in sys5 if normalize_command(cmd).startswith(s4 + " ")]
                #         for m, s5 in enumerate(children5):
                #             connector5 = "└── " if (m == len(children5) - 1) else "├── "
                #             linha_s5 = s5[len(s4) + 1:]
                #             f.write(prefix4 + connector5 + linha_s5 + "\n")
