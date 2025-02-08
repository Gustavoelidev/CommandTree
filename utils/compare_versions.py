import os
from difflib import Differ

dicionario_arquivos = {}
modelo = ""
firmware = ""


def compare_firmware_version(model: str, firmware_dut: str) -> None:
    global modelo
    modelo = model
    global firmware
    firmware = firmware_dut.replace(".", "_").replace(",", "")
    lista_arquivos = []
    for arquivos in os.walk('./resource'):
        for arquivo in arquivos:
            lista_arquivos.append(arquivo)
    # print(f"Lista de arquivos: {lista_arquivos}")
    i = 1
    for a in lista_arquivos:
        for b in a:
            if "Commands" in b and model in b:
                dicionario_arquivos[int(i)] = b
                i += 1
    # print(f"Dicionário de arquivos: f{dicionario_arquivos}")
    select_comparison(dicionario_arquivos)


def select_comparison(arquivos: dict) -> None:
    if len(arquivos) == 0:
        print("Não existem arquivos para comparação")
        print("Encerrando o programa...")
        exit(0)
    print(f"\nArquivos disponíveis: ")
    print(f"\t\tNúmero 0, para encerrar o programa e pular a comparação")
    for arquivo in arquivos:
        print(f"\t\tNúmero {arquivo}, para o modelo {arquivos.get(arquivo)}")
    op = int(input("\nDigite o número desejado: "))
    if op > len(arquivos):
        print("Número inválido")
        select_comparison(dicionario_arquivos)
    elif op == 0:
        print("Encerrando o programa...")
        exit(0)
    elif op in arquivos.keys():
        # print(f"Arquivo selecionado: {dicionario_arquivos.get(op)}")
        make_comparison(dicionario_arquivos.get(op))
    else:
        print("Digite apenas números")
        select_comparison(dicionario_arquivos)


def make_comparison(arquivo: str) -> None:
    print("\n----------------------Diff Verification-----------------------")
    firmware_to_compare = arquivo[arquivo.find("version_"):arquivo.find(".txt"):].replace("version_", "")
    arquivo_1 = "resource/" + arquivo
    arquivo_2 = "resource/Commands_" + modelo + "_version_" + firmware + ".txt"
    print(f"Comparação entre os arquivos: {arquivo_1[9::]} e {arquivo_2[9::]}")
    a = open(arquivo_1, "r")
    b = open(arquivo_2, "r")
    differ = Differ()
    arq = []
    m = 0
    n = 0
    for line in differ.compare(a.readlines(), b.readlines()):
        arq.append(line)
    log_name = ("resource/" + modelo + "_Diff_beteween_versions_" + firmware.replace('.', '_')
                .replace(',', '') + "_and_" + firmware_to_compare + ".html")
    log = open(log_name, "w")
    log.write("<html>\n<head>\n<title> \nLOG </title>\n</head> "
              "<body><h1>CLI Commands</h1>"
              "<h4><font color = #ff0000> Line Red - "
              "Configuration present only in firmware: " + firmware_to_compare.replace('_', '.') + "</font></h4>"
              "<h4><font color = #00b300> Line Green - "
              "Configuration present only in firmware: " + firmware.replace('_', '.') + "</font></h4>")
    for i in arq:
        s = i[0:1]
        if s == "+":
            log.write("<p><font color = #00b300>" + i[1:].replace("\t\t", "&emsp;&emsp;&emsp;").replace("<", "").
                      replace(">", "") + "</font>")
            n = n + 1
        elif s == "-":
            log.write("<p><font color = #ff0000>" + i[1:].replace("\t\t", "&emsp;&emsp;&emsp;").replace("<", "").
                      replace(">", "") + "</font>")
            m = m + 1
        else:
            log.write("<p>" + i[1:].replace("\t\t", "&emsp;&emsp;&emsp;").replace("<", "").replace(">", ""))
    log.close()
    log = open(log_name, "a")
    log.write("\n</body></html>")

    if m == 0 and n == 0:
        print(f"\n\tThe features in both firmwares are the same")
        print(f"\n\tSee {log_name[9::]} to more details")
    else:
        print(f"\n\tSettings not present in firmware version: {firmware.replace('_','.')} - " + str(m))
        print(f"\tSettings not present in firmware version: {firmware_to_compare.replace('_','.')} - " + str(n))
        print(f"\n\tSee {log_name[9::]} to more details")
