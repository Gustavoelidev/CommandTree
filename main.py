import streamlit as st
import time
import json
from utils.get_cli_commands import GetCommands
from utils.save_tree_feature import save_tree_features
from utils.compare_versions import compare_firmware_version

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
    st.title("Verificacao de comandos")
    
    st.markdown("## Selecione o modelo e informe os dados")
    # Seleção do modelo utilizando selectbox; as chaves do dicionário serão usadas internamente
    model_keys = list(models.keys())
    selected_model = st.selectbox("Selecione o modelo:", options=model_keys, format_func=lambda x: models[x])
    
    # Entradas para IP, senha e hostname
    ip = st.text_input("Digite o endereço IPv4 (sem máscara):")
    password = st.text_input("Digite a senha do DUT:", type="password")
    hostname = st.text_input("Digite o hostname configurado no DUT:")
    
    if st.button("Iniciar verificação"):
        if not ip:
            st.error("Por favor, informe um endereço IP.")
        elif not check_ip(ip):
            st.error("Endereço IP inválido.")
        elif not password:
            st.error("Por favor, informe a senha.")
        elif not hostname:
            st.error("Por favor, informe o hostname.")
        else:
            with st.spinner("Conectando e obtendo comandos..."):
                try:
                    # Obtém os comandos e exibe os resultados
                    dicionario = get_lists_of_commands(selected_model, ip, password, hostname)
                    to_compare(models.get(selected_model), dicionario)
                    st.success("Comandos obtidos com sucesso!")
                    
                    # Exibição dos dados do firmware
                    version_data = dicionario.get("__version_data", [])
                    if version_data:
                        st.markdown("### Dados do Firmware")
                        st.write("Firmware:", version_data[0] if len(version_data) > 0 else "N/A")
                        st.write("Bootloader:", version_data[1] if len(version_data) > 1 else "N/A")
                        st.write("Compiled:", version_data[2] if len(version_data) > 2 else "N/A")
                    
                    # Exibição dos comandos de cada nível utilizando st.json
                    st.markdown("### Comandos")
                    st.subheader("Guest 1")
                    st.json(dicionario.get("__commands_guest1"))
                    
                    st.subheader("Guest 2")
                    st.json(dicionario.get("__commands_guest2"))
                    
                    st.subheader("Guest 3")
                    st.json(dicionario.get("__commands_guest3"))
                    
                    st.subheader("Guest 4")
                    st.json(dicionario.get("__commands_guest4"))
                    
                    st.subheader("Guest 5")
                    st.json(dicionario.get("__commands_guest5"))
                    
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")

if __name__ == '__main__':
    main()
