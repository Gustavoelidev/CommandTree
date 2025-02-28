import streamlit as st
import sys
import os
import json

st.set_page_config(
    page_title="[QA] Comandos",
)
# Adiciona o diretório raiz ao sys.path para encontrar os módulos em utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

with open("./styles/styles.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Importa as funções necessárias dos módulos
from utils.get_cli_commands import GetCommands
from utils.save_tree_feature import save_tree_features
from utils.compare_versions import compare_firmware_version

# Exemplo de modelos já testados (pode vir de outro módulo)
models = {1: "WA7539", 2:"AP7739" }

def obter_comandos_e_gerar_arquivo(op, ip, password, hostname):
    """
    Função que instancia a classe GetCommands, obtém os comandos e gera o arquivo
    com a árvore de comandos.
    """
    get_commands = GetCommands(modelo=models.get(op), ip=ip, password=password, hostname=hostname)
    dicionario_listas = get_commands.return_lists()
    save_tree_features(models.get(op), dicionario_listas)
    return dicionario_listas

def comparar_comandos(modelo, dicionario):
    """
    Exemplo de função para comparar versões ou comandos.
    Você pode chamar a função compare_firmware_version ou
    adicionar aqui sua lógica de comparação.
    """
    firmware = dicionario.get("__version_data", ["unknown"])[0]
    # Chama a função de comparação (ajuste conforme sua lógica real)
    resultado = compare_firmware_version(modelo, firmware)
    return f"Resultado da comparação: {resultado}"

def mostrar_arquivo_gerado(modelo, dicionario):
    """
    Lê o arquivo gerado pela função save_tree_features e exibe um botão de download.
    """
    firmware = (
        str(dicionario.get("__version_data", ["unknown"])[0])
        .replace(".", "_")
        .replace(",", "")
    )
    file_name = f"Commands_{str(modelo)}_version_{firmware}.txt"
    file_path = os.path.join("resource", file_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        st.download_button("Baixar Arquivo", file_content, file_name=file_name)
        st.text_area("Conteúdo do Arquivo", file_content, height=300)
    else:
        st.error("Arquivo não encontrado. Verifique se a árvore de comandos foi gerada corretamente.")

def main():
    st.title("Comandos e Árvore de Comandos")
    st.markdown("### Informe os dados do dispositivo")
    
    # Seleção do modelo (baseado no dicionário 'models')
    model_options = list(models.values())
    modelo_selecionado = st.selectbox("Modelo", model_options)
    # Recupera a chave correspondente ao modelo selecionado
    op = [key for key, value in models.items() if value == modelo_selecionado][0]

    # Entradas para IP, senha e hostname
    ip = st.text_input(f"Digite o endereço IPv4 do {modelo_selecionado}:")
    password = st.text_input("Digite a senha para acessar o DUT:", type="password")
    hostname = st.text_input("Digite o hostname configurado no DUT:")

    if st.button("Obter Comandos"):
        if not ip or not password or not hostname:
            st.error("Preencha todos os campos!")
        elif not ip.replace(".", "").isdigit() or len(ip.split(".")) != 4:
            st.error("Endereço IP inválido!")
        else:
            try:
                with st.spinner("Obtendo comandos e gerando arquivo..."):
                    # Executa a captura dos comandos e gera o arquivo com a árvore
                    dicionario = obter_comandos_e_gerar_arquivo(op, ip, password, hostname)
                    st.session_state["dicionario"] = dicionario
                    st.session_state["modelo"] = modelo_selecionado
                    st.success("Arquivo gerado com sucesso!")
            except Exception as e:
                # Exibe a mensagem de erro na web
                st.error(f"Ocorreu um erro: {e}")
                # Encerra a função (ou simplesmente não prossegue com outras ações)
                return

    # Se os comandos já foram obtidos, apresenta as opções para o usuário
    if "dicionario" in st.session_state:
        st.markdown("### O que deseja fazer agora?")
        acao = st.radio("Escolha uma opção:", ("Comparar Comandos", "Visualizar/baixar Arquivo"))
        
        if acao == "Comparar Comandos":
            resultado = comparar_comandos(modelo_selecionado, st.session_state["dicionario"])
            st.write(resultado)
        elif acao == "Visualizar/baixar Arquivo":
            mostrar_arquivo_gerado(modelo_selecionado, st.session_state["dicionario"])

if __name__ == '__main__':
    main()
