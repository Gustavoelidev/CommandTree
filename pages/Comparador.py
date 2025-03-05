import os
import streamlit as st
from difflib import Differ


st.set_page_config(
    page_title="[QA] Comparador",
)

with open("./styles/styles.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
def listar_arquivos(models: list):
    """Lista arquivos disponíveis para comparação."""
    arquivos_disponiveis = {}
    for model in models:
        for root, _, files in os.walk('./resource'):
            for file in files:
                if "Commands" in file and model in file:
                    arquivos_disponiveis[file] = os.path.join(root, file)
    return arquivos_disponiveis

def comparar_firmwares(arquivo_base: str, arquivo_comparacao: str):
    """Compara dois arquivos e gera um log HTML com as diferenças."""
    with open(arquivo_base, "r", encoding="utf-8") as a, open(arquivo_comparacao, "r", encoding="utf-8") as b:
        differ = Differ()
        diferencas = list(differ.compare(a.readlines(), b.readlines()))
    
    firmware_base = arquivo_base.split("version_")[-1].replace(".txt", "")
    firmware_comp = arquivo_comparacao.split("version_")[-1].replace(".txt", "")
    log_name = f"./resource/Diff_{firmware_base}_vs_{firmware_comp}.html"
    
    with open(log_name, "w", encoding="utf-8") as log:
        log.write("""
        <html>
        <head>
            <title>Firmware Comparison</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f9f9f9;
                }
                h1, h4 {
                    color: #333;
                }
                .diff-container {
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                .diff-added {
                    color: #00b300;
                    background-color: #e6ffe6;
                    padding: 2px;
                    border-radius: 4px;
                }
                .diff-removed {
                    color: #ff0000;
                    background-color: #ffe6e6;
                    padding: 2px;
                    border-radius: 4px;
                }
                .diff-unchanged {
                    color: #666;
                }
                .back-button {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: #fff;
                    text-decoration: none;
                    border-radius: 4px;
                }
                .back-button:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
        """)
        log.write(f"<h1>Comparação entre Firmwares</h1>")
        log.write(f"<h4>Modelo Base: {firmware_base}</h4>")
        log.write(f"<h4>Modelo Comparado: {firmware_comp}</h4>")
        log.write("<h4><font color='#ff0000'>Linhas em vermelho: Apenas no firmware base</font></h4>")
        log.write("<h4><font color='#00b300'>Linhas em verde: Apenas no firmware comparado</font></h4>")
        log.write("<div class='diff-container'>")
        
        for linha in diferencas:
            if linha.startswith("+"):
                log.write(f"<p class='diff-added'><strong>Apenas no firmware comparado:</strong> {linha[1:]}</p>")
            elif linha.startswith("-"):
                log.write(f"<p class='diff-removed'><strong>Apenas no firmware base:</strong> {linha[1:]}</p>")
            else:
                log.write(f"<p class='diff-unchanged'>{linha[1:]}</p>")
        
        log.write("</div>")
        log.write("<a href='javascript:history.back()' class='back-button'>Voltar</a>")
        log.write("</body></html>")
    
    return log_name

def main():
    st.title("Comparação de Firmwares")
    modelo1 = st.text_input("Digite o primeiro modelo do dispositivo:")
    modelo2 = st.text_input("Digite o segundo modelo do dispositivo:")
    
    if modelo1 and modelo2:
        arquivos = listar_arquivos([modelo1, modelo2])
        if not arquivos:
            st.warning("Nenhum arquivo encontrado para esses modelos.")
        else:
            arquivos_modelo1 = {k: v for k, v in arquivos.items() if modelo1 in k}
            arquivos_modelo2 = {k: v for k, v in arquivos.items() if modelo2 in k}
            
            arquivo_base = st.selectbox("Selecione o arquivo base (Modelo 1):", list(arquivos_modelo1.keys()))
            arquivo_comparacao = st.selectbox("Selecione o arquivo para comparação (Modelo 2):", list(arquivos_modelo2.keys()))
            
            if st.button("Comparar Firmwares"):
                log_path = comparar_firmwares(arquivos_modelo1[arquivo_base], arquivos_modelo2[arquivo_comparacao])
                st.success("Comparação concluída!")
                
                # Botão de download
                with open(log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()
                st.download_button(
                    label="Baixar Relatório de Comparação",
                    data=log_content,
                    file_name=os.path.basename(log_path),
                    mime="text/html"
                )

if __name__ == "__main__":
    main()