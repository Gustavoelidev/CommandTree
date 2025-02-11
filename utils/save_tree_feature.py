import os

def save_tree_features(modelo: str, dicionario: dict) -> None:
    # Garante que o diretório "resource" existe
    if not os.path.exists("resource"):
        os.makedirs("resource")

    # Extrai os dados do dicionário, com validação
    firmware = (
        str(dicionario.get("__version_data", ["unknown"])[0])
        .replace(".", "_")
        .replace(",", "")
    )
    guest1 = dicionario.get("__commands_guest1", [])
    guest2 = dicionario.get("__commands_guest2", [])
    guest3 = dicionario.get("__commands_guest3", [])
    guest4 = dicionario.get("__commands_guest4", [])
    guest5 = dicionario.get("__commands_guest5", [])

    # Define o caminho completo para o arquivo
    file_path = f"resource/Commands_{modelo}_version_{firmware}.txt"

    def normalize_command(command):
        """Normaliza valores numéricos dinâmicos para evitar duplicação."""
        return command.replace("<1-253>", "<X>").replace("<1-255>", "<Y>")

    with open(file_path, "w", encoding="utf-8") as f:
        # Nível 1 (comandos principais)
        for i, g1 in enumerate(guest1):
            is_last1 = (i == len(guest1) - 1)
            f.write(g1 + "\n")
            prefix1 = "    " if is_last1 else "│   "

            # Nível 2
            children2 = [cmd for cmd in guest2 if normalize_command(cmd).startswith(g1 + " ")]
            for j, g2 in enumerate(children2):
                is_last2 = (j == len(children2) - 1)
                connector2 = "└── " if is_last2 else "├── "
                linha_g2 = g2[len(g1) + 1:]
                f.write(prefix1 + connector2 + linha_g2 + "\n")
                # Se o comando do nível 2 contiver uma string que impeça o processamento de seus filhos, pula para o próximo.
                if "Nostoragemediumsupportsthisoperation" in g2 or "<cr>" in g2:
                    continue
                prefix2 = prefix1 + ("    " if is_last2 else "│   ")

                # Nível 3
                children3 = [cmd for cmd in guest3 if normalize_command(cmd).startswith(g2 + " ")]
                for k, g3 in enumerate(children3):
                    is_last3 = (k == len(children3) - 1)
                    connector3 = "└── " if is_last3 else "├── "
                    linha_g3 = g3[len(g2) + 1:]
                    f.write(prefix2 + connector3 + linha_g3 + "\n")
                    # Se o comando do nível 3 contiver "Such" ou "<cr>", não processa seus filhos.
                    if "Such" in g3 or "<cr>" in g3:
                        continue
                    prefix3 = prefix2 + ("    " if is_last3 else "│   ")

                    # Nível 4
                    children4 = [cmd for cmd in guest4 if normalize_command(cmd).startswith(g3 + " ")]
                    for l, g4 in enumerate(children4):
                        is_last4 = (l == len(children4) - 1)
                        connector4 = "└── " if is_last4 else "├── "
                        linha_g4 = g4[len(g3) + 1:]
                        f.write(prefix3 + connector4 + linha_g4 + "\n")
                        # Se o comando do nível 4 contiver "Such" ou "<cr>", não processa seus filhos.
                        if "Such" in g4 or "<cr>" in g4:
                            continue
                        prefix4 = prefix3 + ("    " if is_last4 else "│   ")

                        # Nível 5
                        children5 = [cmd for cmd in guest5 if normalize_command(cmd).startswith(g4 + " ")]
                        for m, g5 in enumerate(children5):
                            is_last5 = (m == len(children5) - 1)
                            connector5 = "└── " if is_last5 else "├── "
                            linha_g5 = g5[len(g4) + 1:]
                            f.write(prefix4 + connector5 + linha_g5 + "\n")
                            # Se o comando do nível 5 contiver "TEXT" ou "<cr>", pula o processamento de quaisquer filhos (se houver).
                            if "TEXT" in g5 or "<cr>" in g5:
                                continue
