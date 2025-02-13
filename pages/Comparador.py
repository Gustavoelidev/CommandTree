import streamlit as st
import difflib

st.title("Comparador de Árvores TXT")

# Upload dos arquivos de árvore
uploaded_tree_old = st.file_uploader("Selecione a árvore antiga (.txt)", type=["txt"], key="old")
uploaded_tree_new = st.file_uploader("Selecione a árvore nova (.txt)", type=["txt"], key="new")

if uploaded_tree_old and uploaded_tree_new:
    try:
        # Lê e decodifica os conteúdos dos arquivos
        tree_old_content = uploaded_tree_old.read().decode("utf-8")
        tree_new_content = uploaded_tree_new.read().decode("utf-8")
    except Exception as e:
        st.error(f"Erro ao ler os arquivos: {e}")
    else:
        # Exibe os conteúdos carregados
        st.subheader("Árvore Antiga")
        st.text(tree_old_content)
        st.subheader("Árvore Nova")
        st.text(tree_new_content)

        # Gera a comparação usando difflib
        old_lines = tree_old_content.splitlines()
        new_lines = tree_new_content.splitlines()
        diff_lines = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='Árvore Antiga',
            tofile='Árvore Nova',
            lineterm=''
        ))
        diff_text = "\n".join(diff_lines)

        st.subheader("Diferenças Encontradas")
        st.text(diff_text)

        # Botão para gerar e baixar o arquivo com as diferenças
        if st.button("Gerar arquivo com as diferenças"):
            file_name = "diferencas.txt"
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(diff_text)
                st.success(f"Arquivo '{file_name}' gerado com sucesso!")
                with open(file_name, "rb") as f:
                    st.download_button("Baixar arquivo", data=f, file_name=file_name)
            except Exception as e:
                st.error(f"Erro ao gerar o arquivo: {e}")
