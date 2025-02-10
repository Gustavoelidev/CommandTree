import streamlit as st

st.set_page_config(
    page_title="[TEST] Home",
)

st.write("# Web Home | Testes automatizados")

st.markdown(
    """
    Software criado para verificar todos os niveis de comandos dos Device em desenvolvimento.
    
"""
)

# st.session_state.whoami = str(os.popen("whoami").read())
# st.write(st.session_state.whoami)
st.session_state.app = False
