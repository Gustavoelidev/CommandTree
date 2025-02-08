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
    guest = dicionario.get("__commands_guest1", [])
    guest_2 = dicionario.get("__commands_guest2", [])
    guest_3 = dicionario.get("__commands_guest3", [])
    guest_4 = dicionario.get("__commands_guest4", [])
    guest_5 = dicionario.get("__commands_guest5", [])

    # Define o caminho completo para o arquivo
    file_path = f"resource/Commands_{str(modelo)}_version_{firmware}.txt"

    processed_commands = set()
    def normalize_command(command):
        """Normaliza valores numéricos dinâmicos como <X-Y> para evitar duplicação."""
        return command.replace("<1-253>", "<X>").replace("<1-255>", "<Y>") 

    with open(file_path, "w") as f:
        # Percorre a lista de comandos do primeiro nível
        for g in guest:
            f.write(g + "\n")
            processed_commands.clear()

            for g2 in guest_2:
                norm_g2 = normalize_command(g2)

                if norm_g2.startswith(g + " ") and norm_g2 not in processed_commands:
                    f.write("|\t\t|_" + g2[len(g) + 1:] + "\n")
                    processed_commands.add(norm_g2)

                    if "<cr>" in g2:
                        continue  

                    for g3 in guest_3:
                        norm_g3 = normalize_command(g3)

                        if norm_g3.startswith(g2 + " ") and norm_g3 not in processed_commands:
                            f.write("|\t\t|\t\t|_" + g3[len(g2) + 1:] + "\n")
                            processed_commands.add(norm_g3)

                            if "<cr>" in g3:
                                continue  

                            for g4 in guest_4:
                                norm_g4 = normalize_command(g4)

                                if norm_g4.startswith(g3 + " ") and norm_g4 not in processed_commands:
                                    f.write("|\t\t|\t\t|\t\t|_" + g4[len(g3) + 1:] + "\n")
                                    processed_commands.add(norm_g4)

                                    if "<cr>" in g4:
                                        continue  

                                    for g5 in guest_5:
                                        norm_g5 = normalize_command(g5)

                                        if norm_g5.startswith(g4 + " ") and norm_g5 not in processed_commands:
                                            f.write("|\t\t|\t\t|\t\t\t|_" + g5[len(g4) + 1:] + "\n")
                                            processed_commands.add(norm_g5)

                                            if "<cr>" in g5:
                                                continue  


