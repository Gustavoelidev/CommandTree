import os
import streamlit as st
from difflib import Differ

# Dicionário global para armazenar os arquivos encontrados
dicionario_arquivos = {}
modelo = []
firmware = ""


def compare_firmware_version(models: list[str], firmware_dut: str) -> None:
    global modelo, firmware
    modelo = models  # Ex: ["SC 3570", "SC 3170"]
    firmware = firmware_dut.replace(".", "_").replace(",", "")
    lista_arquivos = []

    for root, dirs, files in os.walk('./resource'):
        for file in files:
            lista_arquivos.append(file)

    i = 1
    for arquivo in lista_arquivos:
        if "Commands" in arquivo and any(model in arquivo for model in models):
            dicionario_arquivos[i] = arquivo
            i += 1

    select_comparison(dicionario_arquivos)


def select_comparison(arquivos: dict) -> None:
    if len(arquivos) == 0:
        st.write("Não existem arquivos para comparação. Encerrando a comparação.")
        st.stop()

    # Cria uma lista de opções para o usuário escolher, incluindo a opção 0 para encerrar
    opcoes = {0: "Encerrar a comparação / pular"}
    opcoes.update(arquivos)

    # Converte o dicionário em uma lista de rótulos para exibição
    opcoes_lista = [f"Número {chave} - {valor}" for chave, valor in opcoes.items()]

    st.write("### Arquivos disponíveis:")
    for linha in opcoes_lista:
        st.write(linha)

    # Cria um selectbox para o usuário escolher a opção desejada
    opcao_escolhida = st.selectbox("Selecione o número desejado:", list(opcoes.keys()), format_func=lambda x: opcoes[x])

    if opcao_escolhida == 0:
        st.write("Encerrando o programa...")
        st.stop()
    else:
        make_comparison(opcoes[opcao_escolhida])


def make_comparison(arquivo: str) -> None:
    st.write("\n----------------------Diff Verification-----------------------")
    # Extrai a firmware do arquivo selecionado
    firmware_to_compare = arquivo[arquivo.find("version_"):arquivo.find(".txt")].replace("version_", "")
    
    # Monta os caminhos completos dos arquivos
    arquivo_1 = os.path.join("resource", arquivo)
    # Extrai o modelo (por exemplo, SC_3570) e converte para SC 3570
    parte_nome = arquivo.split("Commands_")[1]
    modelo_detectado = parte_nome.split("_version_")[0].replace("_", " ")

    arquivo_2 = os.path.join("resource", f"Commands_{modelo_detectado.replace(' ', '_')}_version_{firmware}.txt")


    
    st.write(f"Comparação entre os arquivos: {arquivo_1} e {arquivo_2}")

    # Verifica se os arquivos existem
    if not os.path.exists(arquivo_1):
        st.error(f"Arquivo {arquivo_1} não encontrado. Verifique se a árvore de comandos foi gerada corretamente.")
        return
    if not os.path.exists(arquivo_2):
        st.error(f"Arquivo {arquivo_2} não encontrado. Verifique se a árvore de comandos foi gerada corretamente.")
        return

    try:
        with open(arquivo_1, "r") as a, open(arquivo_2, "r") as b:
            diferenca = list(Differ().compare(a.readlines(), b.readlines()))
    except Exception as e:
        st.error(f"Erro ao abrir os arquivos: {e}")
        return

    log_name = os.path.join("resource", f"{modelo_detectado.replace(' ', '_')}_Diff_between_versions_{firmware}_and_{firmware_to_compare}.html")



    conteudo_html = (
        "<html>\n<head>\n<title>LOG</title>\n</head>"
        "<body><h1>CLI Commands</h1>"
        f"<h4><font color='#ff0000'>Linha Vermelha - Configuração presente somente na firmware: {firmware_to_compare.replace('_', '.')}</font></h4>"
        f"<h4><font color='#00b300'>Linha Verde - Configuração presente somente na firmware: {firmware.replace('_', '.')}</font></h4>"
    )
    m = 0
    n = 0
    for linha in diferenca:
        sinal = linha[0:1]
        texto = linha[1:].replace("\t\t", "&emsp;&emsp;&emsp;").replace("<", "").replace(">", "")
        if sinal == "+":
            conteudo_html += f"<p><font color='#00b300'>{texto}</font></p>"
            n += 1
        elif sinal == "-":
            conteudo_html += f"<p><font color='#ff0000'>{texto}</font></p>"
            m += 1
        else:
            conteudo_html += f"<p>{texto}</p>"
    conteudo_html += "\n</body></html>"

    try:
        with open(log_name, "w", encoding="utf-8") as log:
            log.write(conteudo_html)
    except Exception as e:
        st.error(f"Erro ao salvar o log: {e}")
        return

    if m == 0 and n == 0:
        st.success("As configurações são idênticas entre as firmwares.")
        st.write(f"Veja o arquivo {log_name} para mais detalhes.")
    else:
        st.warning(f"Configurações não presentes na firmware {firmware.replace('_', '.')} - {m} linhas")
        st.warning(f"Configurações não presentes na firmware {firmware_to_compare.replace('_', '.')} - {n} linhas")
        st.write(f"Veja o arquivo {log_name} para mais detalhes.")

