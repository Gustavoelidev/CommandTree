import telnetlib
import time
import logging
import re

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("terminal.log"),  # Log será salvo neste arquivo
        logging.StreamHandler()  # Log também será exibido no console
    ]
)

def replace_integer(match):
    # Extrai os dois números capturados nos grupos e retorna o maior valor como string
    num1 = int(match.group(1))
    num2 = int(match.group(2))
    return str(max(num1, num2))

class GetCommands:

    # Dicionário base com os placeholders comuns
    BASE_PLACEHOLDERS = {
        r"STRING": "TESTE",
        r"flash:": "flash:/file",
        r"http:": "http:/file",
        r"ftp:": "ftp:/file",
        r"tftp:": "tftp:/file",
        r"X.X.X.X": "1.1.1.1",
        r"X:X::X:X": "1:1::1:1",
        r"TIME": "12:00:00"
    }

    # Placeholders específicos para cada nível de comando
    PLACEHOLDERS_GUEST3 = {**BASE_PLACEHOLDERS, **{
        r"INTEGER<0-32>": "1"
    }}

    PLACEHOLDERS_GUEST4 = {**BASE_PLACEHOLDERS, **{
        r"INTEGER<(\d+)-(\d+)>": replace_integer,
        r"<(\d+)-(\d+)>": lambda m: m.group(1) if m.group(1) == m.group(2) else "1",
        r"HEX<\d+-\d+>": "1",
        r"STRING<\d+-\d+>": "1",
        r"DATE": "08/12/2012"
    }}

    PLACEHOLDERS_GUEST5 = {**BASE_PLACEHOLDERS, **{
        r"INTEGER<(\d+)-(\d+)>": replace_integer,
        r"HEX<\d+-\d+>": "1",
        r"DATE": "08/12/2012",
        r"<2>": "2",
        r"<1-2>": "2",
        r"HEX<1-FFFFFFFF>": "1",
        r"HEX<1-FFFFFFFFFFFFFFFE>": "1",
        r"STRING<(\d+)-(\d+)>": replace_integer,
    }}

    def __init__(self, modelo: str, ip: str, password: str, hostname: str) -> None:
        self.__modelo: str = modelo
        self.__ip: str = ip
        self.__password: str = password
        self.__hostname: str = hostname
        self.__connection: object = telnetlib.Telnet(self.__ip)
        logging.info(f"Iniciando a conexão Telnet com o IP: {self.__ip}")
        self.__version_data: list = self.new_connection(user="ped", hostname=self.__hostname, password=self.__password)
        self.__commands_guest1: list = self.get_guest_commands1()
        self.__commands_guest2: list = self.get_guest_commands2()
        self.__commands_guest3: list = self.get_guest_commands3()
        self.__commands_guest4: list = self.get_guest_commands4()
        self.__commands_guest5: list = self.get_guest_commands5()

    @property
    def modelo(self) -> str:
        return self.__modelo

    @property
    def ip(self) -> str:
        return self.__ip

    @property
    def firmware(self) -> str:
        return self.__version_data[0]

    @property
    def bootloader(self) -> str:
        return self.__version_data[1]

    @property
    def compiled(self) -> str:
        return self.__version_data[2]

    @property
    def password(self) -> str:
        return self.__password

    def return_lists(self) -> dict:
        dict_list = {"__version_data": self.__version_data,
                     "__commands_guest1": self.__commands_guest1,
                     "__commands_guest2": self.__commands_guest2,
                     "__commands_guest3": self.__commands_guest3,
                     "__commands_guest4": self.__commands_guest4,
                     "__commands_guest5": self.__commands_guest5,
                     }
        return dict_list

    def new_connection(self, user: str, password: str, hostname: str) -> list:
        try:
            logging.info("Realizando o login via Telnet...")
            ret = self.__connection.read_until(b":", timeout=5)
            if b'Login:' in ret:
                self.__connection.write(user.encode("ascii") + b"\n")
                logging.debug(f"Login realizado com o usuário: {user}")
            ret = self.__connection.read_until(b":", timeout=3)
            if b"Password:" in ret:
                self.__connection.write(password.encode("ascii") + b"\n")
                logging.debug("Senha enviada")
            else:
                logging.error("Erro no Login: Não foi possível realizar o login")
                print("Erro no Login")
            ret = self.__connection.read_until(b'<' + self.__hostname.encode("ascii") + b'>')
            if self.__hostname.encode("ascii") in ret:
                self.__connection.write(b"screen-length disable\n")
                ret = self.__connection.read_until(b'<' + self.__hostname.encode("ascii") + b'>')
                if self.__hostname.encode("ascii") in ret:
                    version: list = self.get_firmware_version()
                    logging.info(f"Versão do firmware: {version[0]}")
                    print(f"Version: {version[0]}")
                else:
                    logging.error("Erro ao desabilitar a paginação")
                    print("Erro 2")
            else:
                logging.error("Erro de comunicação com o dispositivo. Hostname não encontrado.")
                print("Erro 3")
                exit(0)
            return version
        except Exception as e:
            logging.error(f"Erro durante a conexão: {e}")
            raise

    def get_firmware_version(self) -> list:
        version = []
        try:
            logging.info("Obtendo a versão do firmware...")
            self.__connection.write(b"display version\n")
            ret = self.__connection.read_until(b'<' + self.__hostname.encode("ascii") + b'>').decode("utf-8").split("\n")
            firmware = ret[10].split(": ")[1].replace("\r", "")
            bootloader = ret[21].split(": ")[1].replace("\r", "").replace(" ", "")
            compiled = ret[8].split(" Compiled")[1].replace("\r", "")
            version.append(firmware)
            version.append(bootloader)
            version.append(compiled)
            logging.info(f"Firmware: {firmware}, Bootloader: {bootloader}, Compiled: {compiled}")
        except Exception as e:
            logging.error(f"Erro ao obter a versão do firmware: {e}")
            raise
        return version

    def get_guest_commands1(self) -> list:
        logging.info("Obtendo os comandos do nível guest...")
        commands = []
        self.__connection.write(b"?")
        ret = self.__connection.read_until(b'<' + self.__hostname.encode("ascii") + b'>').decode("utf-8").split("\n")
        for i, v in enumerate(ret):
            if len(ret) - 1 > i > 1:
                if v != " \r" and "?" not in v:
                    v = v[1:]
                    v = v[:v.find("  ")].replace(" ", "")
                    if v != "":
                        commands.append(v)
        logging.debug(f"Comandos do nível guest: {commands}")
        return commands

    def get_guest_commands2(self) -> list:
        logging.info("Obtendo os comandos do nível 2 guest...")
        commands = []
        for i in self.__commands_guest1:
            self.__connection.write(i.encode("ascii") + b" ?")
            ret = (self.__connection.read_until(b'<' + self.__hostname.encode("ascii") + b'>' + i.encode("ascii"))
                   .decode("utf-8").split("\n"))
            for j, v in enumerate(ret):
                if len(ret) - 1 > j > 0:
                    if v != " \r" and "?" not in v:
                        v = v[1:]
                        v = v[:v.find("  ")].replace(" ", "")
                        if v != "" and "denied" not in v:
                            commands.append(i + " " + v)
            self.__connection.write(chr(24).encode("ascii"))
        logging.debug(f"Comandos do nível 2 guest: {commands}")
        return commands

    def substitute_placeholders(self, command: str, placeholders: dict) -> str:
        """
        Aplica as substituições definidas no dicionário de placeholders sobre o comando.
        """
        for pattern, replacement in placeholders.items():
            command = re.sub(pattern, replacement, command)
        return command

    def get_guest_commands3(self) -> list:
        logging.info("Obtendo os comandos do nível 3 guest...")
        commands = []

        # Utiliza o dicionário de placeholders específico para guest3
        for i in self.__commands_guest2:
            # Substitui os placeholders
            command_to_send = self.substitute_placeholders(i, self.PLACEHOLDERS_GUEST3)

            # Envia o comando modificado para buscar os subcomandos
            self.__connection.write(command_to_send.encode("ascii") + b" ?")
            ret = (self.__connection.read_until(
                b'<' + self.__hostname.encode("ascii") + b'>' + command_to_send.encode("ascii")
            ).decode("utf-8").split("\n"))

            baseline_indent = None  # Para armazenar a indentação base dos subcomandos
            for j, line in enumerate(ret):
                # Ignora a primeira e a última linha (geralmente cabeçalho e prompt)
                if 0 < j < len(ret) - 1 and line.strip():
                    current_indent = len(line) - len(line.lstrip())
                    if baseline_indent is None:
                        baseline_indent = current_indent
                    if current_indent == baseline_indent:
                        command_part = line.strip().split()[0]
                        commands.append(i + " " + command_part)
            # Envia Ctrl+X para sair do modo de ajuda
            self.__connection.write(chr(24).encode("ascii"))
        logging.debug(f"Comandos do nível 3 guest: {commands}")
        return commands

    def get_guest_commands4(self) -> list:
        logging.info("Obtendo os comandos do nível 4 guest...")
        commands = []

        # Utiliza o dicionário de placeholders específico para guest4
        for i in self.__commands_guest3:
            command_to_send = self.substitute_placeholders(i, self.PLACEHOLDERS_GUEST4)

            self.__connection.write(command_to_send.encode("ascii") + b" ?")
            ret = (self.__connection.read_until(
                    b"<" + self.__hostname.encode("ascii") + b">" + command_to_send.encode("ascii")
                )
                .decode("utf-8")
                .split("\n")
            )

            baseline_indent = None  # Armazenará a indentação base dos subcomandos
            for j, line in enumerate(ret):
                if 0 < j < len(ret) - 1 and line.strip():
                    current_indent = len(line) - len(line.lstrip())
                    if baseline_indent is None:
                        baseline_indent = current_indent
                    if current_indent == baseline_indent:
                        command_part = line.strip().split()[0]
                        commands.append(i + " " + command_part)
            self.__connection.write(chr(24).encode("ascii"))
        logging.debug(f"Comandos do nível 4 guest: {commands}")
        return commands

    def get_guest_commands5(self) -> list:
        logging.info("Obtendo os comandos do nível 5 guest...")
        commands = []

        # Utiliza o dicionário de placeholders específico para guest5
        for i in self.__commands_guest4:
            command_to_send = self.substitute_placeholders(i, self.PLACEHOLDERS_GUEST5)
            logging.debug(f"Enviando comando para o DUT: {command_to_send} ?")
            self.__connection.write(command_to_send.encode("ascii") + b" ?")
            ret = (self.__connection.read_until(
                    b'<' + self.__hostname.encode("ascii") + b'>' + command_to_send.encode("ascii"),
                    timeout=5
                )
                .decode("utf-8")
                .split("\n")
            )

            logging.debug("Saída completa do DUT:")
            for line in ret:
                logging.debug(line)

            baseline_indent = None  # Armazenará a indentação base dos subcomandos
            for j, line in enumerate(ret):
                if 0 < j < len(ret) - 1 and line.strip():
                    current_indent = len(line) - len(line.lstrip())
                    if baseline_indent is None:
                        baseline_indent = current_indent
                    if current_indent == baseline_indent:
                        command_part = line.strip().split()[0]
                        commands.append(i + " " + command_part)
            self.__connection.write(chr(24).encode("ascii"))
        logging.debug(f"Comandos do nível 5 guest: {commands}")
        return commands
