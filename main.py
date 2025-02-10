import streamlit as st
import emoji
import time
import json
from utils.get_cli_commands import GetCommands
from utils.save_tree_feature import save_tree_features
from utils.compare_versions import compare_firmware_version

# Carrega o CSS customizado
with open("./styles/styles.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Modelos já testados com o sistema
models = {1: "DUT1", }

def check_ip(ip: str) -> bool:
    """Valida o endereço IP"""
    valores = ip.split(".")
    if len(valores) != 4:
        return False
    for v in valores:
        try:
            num = int(v)
            if not (0 < num < 255):
                return False
        except ValueError:
            return False
    return True

def to_compare(modelo: str, dicionario: dict) -> None:
    """Chama a função de comparação de versões."""
    firmware = dicionario.get("__version_data")
    compare_firmware_version(modelo, firmware[0])

def get_lists_of_commands(op: int, ip: str, password: str, hostname: str) -> dict:
    """Cria o objeto GetCommands, coleta os comandos e salva as features da árvore."""
    get_commands = GetCommands(modelo=models.get(op), ip=ip, password=password, hostname=hostname)
    dicionario_listas = get_commands.return_lists()
    save_tree_features(models.get(op), dicionario_listas)
    return dicionario_listas

def main():
    st.title("Verificação de comandos")
    
    st.markdown("## Selecione o modelo e informe os dados")
    # Seleção do modelo utilizando selectbox; as chaves do dicionário serão usadas internamente
    model_keys = list(models.keys())
    selected_model = st.selectbox("Selecione o modelo:", options=model_keys, format_func=lambda x: models[x])
    
    # Entradas para IP, senha e hostname
    ip = st.text_input("Digite o endereço IPv4 (sem máscara):")
    password = st.text_input("Digite a senha do DUT:", type="password")
    hostname = st.text_input("Digite o hostname configurado no DUT:")

    if st.button("▶ Iniciar"):
        if not ip:
            st.error("Por favor, informe um endereço IP.")
        elif not check_ip(ip):
            st.error("Endereço IP inválido.")
        elif not password:
            st.error("Por favor, informe a senha.")
        elif not hostname:
            st.error("Por favor, informe o hostname.")
        else:
            # Cria um container para simular a saída de um terminal
            terminal_output = st.empty()
            logs = []

            def log(message: str):
                logs.append(message)
                # Atualiza o container com as mensagens em estilo de código (monoespaçado)
                terminal_output.code("\n".join(logs))

            try:
                log("Iniciando conexão com o DUT...")
                time.sleep(1)  # Simulação de tempo de conexão

                log("Conectando e obtendo comandos...")
                dicionario = get_lists_of_commands(selected_model, ip, password, hostname)
                log("Comandos obtidos com sucesso!")

                log("Comparando versão do firmware...")
                to_compare(models.get(selected_model), dicionario)
                log("Firmware verificado com sucesso!")
                
                # Exibição dos dados do firmware
                version_data = dicionario.get("__version_data", [])
                if version_data:
                    log("Dados do Firmware:")
                    log(f"Firmware: {version_data[0] if len(version_data) > 0 else 'N/A'}")
                    log(f"Bootloader: {version_data[1] if len(version_data) > 1 else 'N/A'}")
                    log(f"Compiled: {version_data[2] if len(version_data) > 2 else 'N/A'}")
                
                # Exibição dos comandos de cada nível
                log("Exibindo comandos:")
                log("Guest 1:")
                log(json.dumps(dicionario.get("__commands_guest1"), indent=2, ensure_ascii=False))
                log("Guest 2:")
                log(json.dumps(dicionario.get("__commands_guest2"), indent=2, ensure_ascii=False))
                log("Guest 3:")
                log(json.dumps(dicionario.get("__commands_guest3"), indent=2, ensure_ascii=False))
                log("Guest 4:")
                log(json.dumps(dicionario.get("__commands_guest4"), indent=2, ensure_ascii=False))
                log("Guest 5:")
                log(json.dumps(dicionario.get("__commands_guest5"), indent=2, ensure_ascii=False))
                
            except Exception as e:
                log(f"Ocorreu um erro: {e}")

if __name__ == '__main__':
    main()
