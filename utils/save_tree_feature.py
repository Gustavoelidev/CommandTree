import os

def filter_commands(commands: list) -> list:
    """
    Remove comandos que começam com "serviewcommands:" ou "user view commands:".
    A verificação é feita após remover espaços à esquerda e convertendo para minúsculas.
    """
    filtered = []
    for cmd in commands:
        cmd_clean = cmd.strip()
        if cmd_clean.lower().startswith("serviewcommands:") or cmd_clean.lower().startswith("user view commands:"):
            continue
        filtered.append(cmd)
    return filtered

def save_tree_features(modelo: str, dicionario: dict) -> None:
    """
    Salva em arquivo .txt a árvore de comandos gerada a partir dos níveis de comandos.
    As chaves do dicionário devem ser:
      - "version_data"
      - "commands_guest1"
      - "commands_guest2"
      - "commands_guest3"
      - "commands_guest4"
      - "commands_guest5"
    """
    # Garante que o diretório "resource" existe
    os.makedirs("resource", exist_ok=True)

    # Extrai os dados do dicionário com as chaves atualizadas
    firmware = (
        str(dicionario.get("version_data", ["unknown"])[0])
        .replace(".", "_")
        .replace(",", "")
    )
    guest1 = filter_commands(dicionario.get("commands_guest1", []))
    guest2 = filter_commands(dicionario.get("commands_guest2", []))
    guest3 = filter_commands(dicionario.get("commands_guest3", []))
    guest4 = filter_commands(dicionario.get("commands_guest4", []))
    guest5 = filter_commands(dicionario.get("commands_guest5", []))

    # Define o caminho completo para o arquivo
    file_path = f"resource/Commands_{modelo}_version_{firmware}.txt"

    def normalize_command(command: str) -> str:
        """Normaliza valores numéricos dinâmicos para evitar duplicação."""
        return command.replace("<1-253>", "<X>").replace("<1-255>", "<Y>")

    with open(file_path, "w", encoding="utf-8") as f:
        # Nível 1 (comandos principais)
        for i, g1 in enumerate(guest1):
            f.write(g1 + "\n")
            prefix1 = "    " if (i == len(guest1) - 1) else "│   "

            # Nível 2
            children2 = [cmd for cmd in guest2 if normalize_command(cmd).startswith(g1 + " ")]
            for j, g2 in enumerate(children2):
                connector2 = "└── " if (j == len(children2) - 1) else "├── "
                linha_g2 = g2[len(g1) + 1:]
                f.write(prefix1 + connector2 + linha_g2 + "\n")
                if "Nostoragemediumsupportsthisoperation" in g2 or "<cr>" in g2:
                    continue
                prefix2 = prefix1 + ("    " if (j == len(children2) - 1) else "│   ")

                # Nível 3
                children3 = [cmd for cmd in guest3 if normalize_command(cmd).startswith(g2 + " ")]
                for k, g3 in enumerate(children3):
                    connector3 = "└── " if (k == len(children3) - 1) else "├── "
                    linha_g3 = g3[len(g2) + 1:]
                    f.write(prefix2 + connector3 + linha_g3 + "\n")
                    if "Such" in g3 or "<cr>" in g3:
                        continue
                    prefix3 = prefix2 + ("    " if (k == len(children3) - 1) else "│   ")

                #     # Nível 4
                    children4 = [cmd for cmd in guest4 if normalize_command(cmd).startswith(g3 + " ")]
                    for l, g4 in enumerate(children4):
                        connector4 = "└── " if (l == len(children4) - 1) else "├── "
                        linha_g4 = g4[len(g3) + 1:]
                        f.write(prefix3 + connector4 + linha_g4 + "\n")
                        if "Such" in g4 or "<cr>" in g4:
                            continue
                        prefix4 = prefix3 + ("    " if (l == len(children4) - 1) else "│   ")

                #         # Nível 5
                        children5 = [cmd for cmd in guest5 if normalize_command(cmd).startswith(g4 + " ")]
                        for m, g5 in enumerate(children5):
                            connector5 = "└── " if (m == len(children5) - 1) else "├── "
                            linha_g5 = g5[len(g4) + 1:]
                            f.write(prefix4 + connector5 + linha_g5 + "\n")
                            if "TEXT" in g5 or "<cr>" in g5:
                                continue
