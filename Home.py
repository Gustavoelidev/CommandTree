import streamlit as st

st.set_page_config(
    page_title="[QA] Home",
)

st.write("# Web Home | Testes automatizados")

st.markdown(
    """
    Software desenvolvido para acessar a camada mais profunda de comandos de switches, controladoras, roteadores e Access Points.

    Modo de uso:

    Insira o endereço IPv4 do dispositivo. O software se comunica via Telnet, portanto, certifique-se de que essa opção esteja habilitada no DUT (Device Under Test).

    Informe a senha e o nome do sysname configurado no dispositivo.

    Observação: O código está parametrizado para realizar o login no DUT utilizando o usuário ped. Verifique essa configuração antes de executar o código.
    
"""
)

# st.session_state.whoami = str(os.popen("whoami").read())
# st.write(st.session_state.whoami)
st.session_state.app = False
