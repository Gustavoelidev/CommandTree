import sys
import os
import time
import streamlit as st
from utils.main import check_ip, models  # Supondo que as funções originais estão em utils.main

st.set_page_config(page_title="[TEST] Comandos")

# Carrega o CSS customizado
with open("./styles/styles.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inicializa a flag de cancelamento, se ainda não existir
if "cancel_process" not in st.session_state:
    st.session_state.cancel_process = False

def main():
    st.title("VERIFICAÇÃO DE COMANDOS")
    st.markdown("Utilize os campos abaixo para inserir as informações necessárias:")

    # --- Seleção do modelo ---
    st.markdown("#### Selecione o modelo desejado:")
    model_options = list(models.values())
    modelo_selecionado = st.selectbox("Modelo", model_options)
    op = [key for key, value in models.items() if value == modelo_selecionado][0]

    # --- Inputs para IP, senha e hostname ---
    ip = st.text_input(f"Digite o endereço IPv4 do {modelo_selecionado} (sem a máscara):")
    password = st.text_input("Digite a senha para acessar o DUT:", type="password")
    hostname = st.text_input("Digite o hostname configurado no DUT:")

    # --- Botões de execução e interrupção ---
    col1, col2 = st.columns(2)
    with col1:
        executar = st.button("Executar")
    with col2:
        interromper = st.button("Interromper")

    # Se o botão "Interromper" for clicado, atualiza a flag
    if interromper:
        st.session_state.cancel_process = True
        st.warning("Solicitação de interrupção enviada!")

    # Se o botão "Executar" for clicado, inicia o processamento
    if executar:
        # Reseta a flag de cancelamento antes de iniciar
        st.session_state.cancel_process = False

        if check_ip(ip):
            with st.spinner("Processando, por favor aguarde..."):
                # Chama a função que obtém a lista de comandos com verificação de cancelamento
                dicionario = get_lists_of_commands_with_cancellation(op, ip, password, hostname)
                if st.session_state.cancel_process:
                    st.error("Processo interrompido pelo usuário!")
                    return

                # Chama a função de comparação com verificação de cancelamento
                to_compare_with_cancellation(modelo_selecionado, dicionario)
                if st.session_state.cancel_process:
                    st.error("Processo interrompido pelo usuário!")
                else:
                    st.success("Processo concluído com sucesso!")
        else:
            st.error(f"O endereço IP {ip} é inválido.")

def get_lists_of_commands_with_cancellation(op, ip, password, hostname):
    """
    Exemplo de função que simula um processo longo, verificando periodicamente
    se o usuário solicitou a interrupção.
    """
    result = {}
    total_passos = 10  # por exemplo, 10 etapas
    for i in range(total_passos):
        # Verifica se houve solicitação de cancelamento
        if st.session_state.cancel_process:
            st.warning("Interrupção detectada durante a obtenção de comandos.")
            break

        # Simula a execução de uma etapa do processamento
        result[f"command_group_{i}"] = f"Resultado {i}"
        time.sleep(0.5)  # Simula atraso (processamento)

    return result

def to_compare_with_cancellation(modelo_selecionado, dicionario):
    """
    Exemplo de função que simula a comparação de resultados, verificando periodicamente
    se o usuário solicitou a interrupção.
    """
    total_passos = 10
    for i in range(total_passos):
        if st.session_state.cancel_process:
            st.warning("Interrupção detectada durante a comparação.")
            break

        st.write(f"Comparando {modelo_selecionado}: passo {i+1}/{total_passos}")
        time.sleep(0.5)  # Simula atraso

if __name__ == '__main__':
    main()
