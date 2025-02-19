import time
import json
from utils.get_cli_commands import GetCommands
from utils.save_tree_feature import save_tree_features
from utils.compare_versions import compare_firmware_version



# Modelos já testados com o sistema
models = {1: "DUT-SW", 2:"DUT-AP" }


def check_ip(ip) -> None:
    resultato = None
    valores = ip.split(".")
    if len(valores) == 4:
        for v in valores:
            if 0 < int(v) < 255:
                resultato = True
            else:
                resultato = False
    else:
        resultato = False
    return resultato
1

def to_compare(modelo: str, dicionario: dict) -> None:
    firmware = dicionario.get("__version_data")
    compare_firmware_version(modelo, firmware[0])


def get_lists_of_commands(op: int, ip: str, password: str, hostname: str) -> dict:

    get_commands = GetCommands(modelo=models.get(op), ip=ip, password=password, hostname=hostname)
    dicionario_listas = get_commands.return_lists()
    # # print(f"Dicionário de listas: {dicionario_listas}")
    save_tree_features(models.get(op), dicionario_listas)
    return dicionario_listas


def convert_list_to_json(_dicionario: dict, key: str) -> object:
    _lista: list = _dicionario.get(key)
    _json = json.dumps(_lista)
    # print(f"Lista: {_lista}, JSON: {_json}")
    return _json
1

def main() -> None:
    print("VERIFICACAO DE COMANDOS | INTELBRAS")
    menu()


def menu() -> None:
    print("==============================================")
    print(f"Selecione o modelo desejado na lista abaixo:")
    for model in models:
        print(f"Número {model}, para o modelo {models.get(model)}")
    print(f"Número {len(models) + 1}, para sair")
    print("==============================================")
    op = None
    try:
        # op = 13
        op = int(input())
    except:
        print(f"ERRO: Valor inválido inserido")
        menu()
    if op == len(models) + 1:
        print("Saindo do sistema...")
        time.sleep(1)
        exit(0)
    elif op > len(models) + 1:
        print("Opção inválida, tente novamente")
        time.sleep(1)
        menu()
    else:
        print("Iniciando o sistema...")
        # ip = "10.100.26.120"
        ip: str = str(input(f"Digite o endereço IPv4 do {models.get(op)} sem a máscara: "))
        if check_ip(ip):
            # print(f"O endereço digitado: {ip}")
            password: str = str(input("Digite a senha para acessar o DUT: "))
            if password:
                # print(f"A senha digitada é: {password}")
                hostname: str = str(input("Digite o Hostname configurado no DUT: "))
                if hostname:
                    dicionario = get_lists_of_commands(op, ip, password, hostname)
                    to_compare(models.get(op), dicionario)
            else:
                print("Valor inválido")
                menu()
        else:
            print(f"O endereço {ip} é inválido")
            menu()


if __name__ == '__main__':
    main()
