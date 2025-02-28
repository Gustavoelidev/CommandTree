import os
import streamlit as st
import difflib


# Função para comparar as versões do firmware
def compare_firmware_version(model: str, firmware_dut: str, file1, file2) -> None:
    firmware_dut = firmware_dut.replace(".", "_").replace(",", "")
    firmware_to_compare = file2.name[file2.name.find("version_"):file2.name.find(".txt"):].replace("version_", "")
    
    # Lê os conteúdos dos arquivos
    a = file1.read().decode("utf-8").splitlines()
    b = file2.read().decode("utf-8").splitlines()
    
    differ = difflib.Differ()
    comparison_result = list(differ.compare(a, b))

    # Contadores para estatísticas
    additions = 0
    deletions = 0
    unchanged = 0

    # Criação do conteúdo HTML para exibição direta no Streamlit
    log_html = f"""
    <html>
    <head>
        <title>CLI Commands - Diff Log</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
                color: #333;
                padding: 20px;
            }}
            h1, h4 {{
                color: #2c3e50;
            }}
            .diff-container {{
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
                max-height: 500px;
                overflow-y: auto;
            }}
            .diff-added {{
                color: #00b300;
                background-color: #e6ffe6;
                padding: 2px 5px;
                border-radius: 3px;
            }}
            .diff-removed {{
                color: #ff0000;
                background-color: #ffe6e6;
                padding: 2px 5px;
                border-radius: 3px;
            }}
            .diff-unchanged {{
                color: #666;
                padding: 2px 5px;
            }}
            .stats {{
                margin-bottom: 20px;
                font-size: 16px;
            }}
            .stats span {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
    <h1>CLI Commands - Comparação de Firmware</h1>
    <div class="stats">
        <p><span>Adições:</span> {additions} | <span>Remoções:</span> {deletions} | <span>Inalterados:</span> {unchanged}</p>
    </div>
    <h4><font color = #ff0000> Linha vermelha - Configuração que não está presente no firmware: {firmware_to_compare.replace('_', '.')} </font></h4>
    <h4><font color = #00b300> Linha verde - Configuração que não está presente no firmware: {firmware_dut.replace('_', '.')} </font></h4>
    <div class="diff-container">
    """

    for line in comparison_result:
        s = line[0:1]
        # Processa a linha fora da f-string
        processed_line = line[1:].replace('\t', '&emsp;&emsp;').replace('<', '').replace('>', '')
        
        if s == "+":
            log_html += f"<p class='diff-added'>{processed_line}</p>\n"
            additions += 1
        elif s == "-":
            log_html += f"<p class='diff-removed'>{processed_line}</p>\n"
            deletions += 1
        else:
            log_html += f"<p class='diff-unchanged'>{processed_line}</p>\n"
            unchanged += 1

    log_html += """
    </div>
    </body>
    </html>
    """
    
    return log_html, additions, deletions, unchanged

# Função para upload dos arquivos e controle do fluxo
def app():
    st.title('Comparação de Árvores de Comandos')

    # Input para o modelo e firmware
    model = st.text_input("Digite o modelo do equipamento")
    firmware_dut = st.text_input("Digite a versão do firmware DUT")
    
    st.markdown("### Upload dos arquivos de configuração")
    file1 = st.file_uploader("Upload do arquivo de configuração 1", type=["txt"], label_visibility="visible")
    file2 = st.file_uploader("Upload do arquivo de configuração 2", type=["txt"], label_visibility="visible")

    if file1 and file2 and model and firmware_dut:
        if st.button('Comparar'):
            # Chama a função para realizar a comparação
            log_html, additions, deletions, unchanged = compare_firmware_version(model, firmware_dut, file1, file2)

            # Exibe o log do resultado da comparação diretamente no Streamlit
            st.markdown("### Resultado da comparação:")
            st.markdown(log_html, unsafe_allow_html=True)

            # Exibe estatísticas
            st.markdown(f"**Adições:** {additions} | **Remoções:** {deletions} | **Inalterados:** {unchanged}")

            # Botão de download do HTML
            st.download_button(
                label="Baixar resultado em formato HTML",
                data=log_html,
                file_name=f"comparacao_firmware_{model}_{firmware_dut}.html",
                mime="text/html"
            )

if __name__ == "__main__":
    app()