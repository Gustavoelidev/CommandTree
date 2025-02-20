import telnetlib
import logging
import re
from typing import List, Union, Tuple, Callable

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("terminal.log"),  # Log será salvo neste arquivo
        logging.StreamHandler()               # Log também será exibido no console
    ]
)

def replace_integer(match: re.Match) -> str:
    """Retorna o maior valor entre dois inteiros capturados."""
    num1 = int(match.group(1))
    num2 = int(match.group(2))
    return str(max(num1, num2))

def replace_string_numeric(match: re.Match) -> str:
    """Retorna o valor máximo do intervalo definido no placeholder STRING."""
    min_val = int(match.group(1))
    max_val = int(match.group(2))
    return str(max_val)

# Definição do tipo para os placeholders:
PlaceholderType = Tuple[str, Union[str, List[str], Callable[[re.Match], str]]]

# ------------------------------
# Placeholders
# ------------------------------
BASE_PLACEHOLDERS_NO_STRING: List[PlaceholderType] = [
    (r"flash:", "flash:/file"),
    (r"http:", "http:/file"),
    (r"ftp:", "ftp:/file"),
    (r"tftp:", "tftp:/file"),
    (r"X.X.X.X", "1.1.1.1"),
    (r"X:X::X:X", "1:1::1:1"),
    (r"TIME", "12:00:00"),
    (r"H-H-H", "1-1-1"),
]

PLACEHOLDERS_GUEST3: List[PlaceholderType] = BASE_PLACEHOLDERS_NO_STRING + [
    (r"INTEGER<0-32>", "1"),
    (r"STRING<1-63>", "1"),
    (r"INTEGER<(\d+)-(\d+)>(?:>*)", replace_string_numeric),
    (r"HEX<0-FFFFFFFF>", "F"),
    (r"HEX<0-FFFFFFFFFFFFFFFE>", "F"),
    (r"H-H-H", "1-1-1"),
    # Placeholder genérico para STRING
    (r"STRING", "Teste.py"),
]

PLACEHOLDERS_GUEST4: List[PlaceholderType] = [
    # Primeiro, o placeholder específico que retorna um número:
    (r"STRING<4-4>", "4444"),
    (r"STRING<1-63>", "1"),
    (r"INTEGER<(\d+)-(\d+)>(?:>*)", replace_string_numeric),
] + BASE_PLACEHOLDERS_NO_STRING + [
    (r"INTEGER<(\d+)-(\d+)>(?:>*)", replace_integer),
    (r"<(\d+)-(\d+)>", lambda m: m.group(1) if m.group(1) == m.group(2) else "1"),
    (r"HEX<0-FFFFFFFF>", "0"),
    (r"HEX<\d+-\d+>", "1"),
    (r"DATE", "08/12/2012"),
    (r"X.X.X.X", "1.1.1.1"),
    (r"<1-2>", "1/0/33"),
    (r"<0-0>", "0"),
    (r"H-H-H", "1-1-1"),
    # Placeholder genérico para STRING
    (r"STRING", "teste.tar"),
]

class GetCommands:
    """
    Classe responsável por estabelecer a conexão Telnet e obter comandos em
    diferentes níveis (guest 1 a 5) a partir do dispositivo.
    """
    ESCAPE_CHAR = b'\x18'  # Caractere para cancelar comandos (Ctrl+X)

    def __init__(self, modelo: str, ip: str, password: str, hostname: str) -> None:
        self._modelo: str = modelo
        self._ip: str = ip
        self._password: str = password
        self._hostname: str = hostname
        self._prompt: bytes = f"<{self._hostname}>".encode("ascii")
        self._connection: telnetlib.Telnet = telnetlib.Telnet(self._ip)
        logging.info(f"Iniciando a conexão Telnet com o IP: {self._ip}")
        self._version_data: List[str] = self.new_connection(
            user="admin", password=self._password, hostname=self._hostname
        )
        self._commands_guest1: List[str] = self.get_guest_commands1()
        self._commands_guest2: List[str] = self.get_guest_commands2()
        self._commands_guest3: List[str] = self.get_guest_commands3()
        self._commands_guest4: List[str] = self.get_guest_commands4()

    @property
    def modelo(self) -> str:
        return self._modelo

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def firmware(self) -> str:
        return self._version_data[0]

    @property
    def bootloader(self) -> str:
        return self._version_data[1]

    @property
    def compiled(self) -> str:
        return self._version_data[2]

    @property
    def password(self) -> str:
        return self._password

    def return_lists(self) -> dict:
        """Retorna os dados de versão e as listas de comandos dos diferentes níveis."""
        return {
            "version_data": self._version_data,
            "commands_guest1": self._commands_guest1,
            "commands_guest2": self._commands_guest2,
            "commands_guest3": self._commands_guest3,
            "commands_guest4": self._commands_guest4,
        }

    def new_connection(self, *, user: str, password: str, hostname: str) -> List[str]:
        try:
            logging.info("Realizando o login via Telnet...")
            ret = self._connection.read_until(b":", timeout=5)
            if b"login:" in ret:
                self._connection.write(f"{user}\n".encode("ascii"))
                logging.debug(f"Login realizado com o usuário: {user}")
            ret = self._connection.read_until(b":", timeout=3)
            if b"Password:" in ret:
                self._connection.write(f"{password}\n".encode("ascii"))
                logging.debug("Senha enviada")
            else:
                logging.error("Erro no Login: Não foi possível realizar o login")
                raise ConnectionError("Erro no Login")
            ret = self._connection.read_until(self._prompt)
            if self._prompt in ret:
                self._connection.write(b"screen-length disable\n")
                ret = self._connection.read_until(self._prompt)
                if self._prompt in ret:
                    version = self.get_firmware_version()
                    logging.info(f"Versão do firmware: {version[0]}")
                    print(f"Version: {version[0]}")
                else:
                    logging.error("Erro ao desabilitar a paginação")
                    raise RuntimeError("Erro ao desabilitar a paginação")
            else:
                logging.error("Erro de comunicação com o dispositivo. Hostname não encontrado.")
                raise ConnectionError("Hostname não encontrado.")
            return version
        except Exception as e:
            logging.error(f"Erro durante a conexão: {e}")
            raise

    def get_firmware_version(self) -> List[str]:
        version: List[str] = []
        try:
            logging.info("Iniciando a obtenção da versão do firmware...")
            self._connection.write(b"display version\n")
            raw_response = self._connection.read_until(self._prompt).decode("utf-8")
            logging.debug("Resposta completa do comando 'display version':")
            for idx, line in enumerate(raw_response.splitlines()):
                logging.debug(f"Linha {idx}: {line}")
            os_version_match = re.search(
                r"INTELBRAS OS Software,\s*Version\s*([\d\.]+,\s*(?:ESS\s*\d+|Release\s*\d+))", 
                raw_response
            )
            boot_version_match = re.search(
               r"Boot image version:\s*([\d\.]+,\s*(?:ESS\s*\d+|Release\s*\d+))", 
                raw_response
            )
            compiled_match = re.search(
                r"Compiled\s+([A-Za-z]+\s+\d+\s+\d+\s+[\d:]+)", 
                raw_response
            )
            if not os_version_match:
                logging.error("Não foi possível extrair a versão do OS.")
                raise ValueError("Formato da resposta não contém a versão do OS.")
            if not boot_version_match:
                logging.error("Não foi possível extrair a versão da imagem de boot.")
                raise ValueError("Formato da resposta não contém a versão da imagem de boot.")
            if not compiled_match:
                logging.error("Não foi possível extrair a data de compilação.")
                raise ValueError("Formato da resposta não contém a data de compilação.")
            os_version = os_version_match.group(1).strip()
            boot_version = boot_version_match.group(1).strip()
            compiled = compiled_match.group(1).strip()
            logging.debug(f"OS Version extraída: {os_version}")
            logging.debug(f"Boot image version extraída: {boot_version}")
            logging.debug(f"Compiled extraída: {compiled}")
            version.extend([os_version, boot_version, compiled])
            logging.info(f"Informações extraídas - OS Version: {os_version}, "
                        f"Boot Version: {boot_version}, Compiled: {compiled}")
        except Exception as e:
            logging.error(f"Erro ao obter a versão do firmware: {e}")
            raise
        return version

    def substitute_placeholders(self, command: str, placeholders: List[PlaceholderType], root_command: str = "") -> str:
        """
        Aplica as substituições definidas na lista de placeholders sobre o comando.
        """
        for pattern, replacement in placeholders:
            if pattern == r"STRING":
                candidate = "teste.tar" if "tar" in root_command.lower() else (
                    replacement[0] if isinstance(replacement, list) else replacement
                )
                command = re.sub(pattern, candidate, command)
            elif isinstance(replacement, list):
                candidate_used = None
                for candidate in replacement:
                    new_command = re.sub(pattern, candidate, command)
                    if new_command != command:
                        candidate_used = candidate
                        command = new_command
                        break
                if candidate_used is None:
                    candidate = replacement[0]
                    command = re.sub(pattern, candidate, command)
            elif callable(replacement):
                command = re.sub(pattern, replacement, command)
            else:
                command = re.sub(pattern, replacement, command)
        return command

    def get_guest_commands1(self) -> List[str]:
        logging.info("Obtendo os comandos do nível guest...")
        commands: List[str] = []
        self._connection.write(b"?")
        ret = self._connection.read_until(self._prompt).decode("utf-8").splitlines()
        for line in ret[2:-1]:
            if line.strip() and "?" not in line:
                cmd = line[1:]
                cmd = cmd.split("  ")[0].replace(" ", "")
                if cmd:
                    commands.append(cmd)
        logging.debug(f"Comandos do nível guest: {commands}")
        return commands

    def _parse_guest_response(self, base_command: str, response_lines: List[str], start: int = 1, end: Union[int, None] = None) -> List[str]:
        commands: List[str] = []
        baseline_indent: Union[int, None] = None
        if end is None:
            end = len(response_lines) - 1
        for line in response_lines[start:end]:
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                if baseline_indent is None:
                    baseline_indent = current_indent
                if current_indent == baseline_indent:
                    command_part = line.strip().split()[0]
                    if "denied" not in command_part:
                        commands.append(f"{base_command} {command_part}")
        return commands

    def get_guest_commands2(self) -> List[str]:
        logging.info("Obtendo os comandos do nível 2 guest...")
        commands: List[str] = []
        for base_cmd in self._commands_guest1:
            self._connection.write(f"{base_cmd} ?".encode("ascii"))
            ret = self._connection.read_until(self._prompt + base_cmd.encode("ascii"), timeout=5)
            response = ret.decode("utf-8").splitlines()
            cmds = self._parse_guest_response(base_cmd, response, start=1, end=len(response) - 1)
            commands.extend(cmds)
            self._connection.write(self.ESCAPE_CHAR)
        logging.debug(f"Comandos do nível 2 guest: {commands}")
        return commands

    def get_guest_commands3(self) -> List[str]:
        """
        Obtém os comandos do nível 3 guest.
        """
        logging.info("Obtendo os comandos do nível 3 guest...")
        commands: List[str] = []
        for base_cmd in self._commands_guest2:
            # Aplica os placeholders para obter o comando final
            command_to_send = self.substitute_placeholders(base_cmd, PLACEHOLDERS_GUEST3, root_command=base_cmd)
            self._connection.write(f"{command_to_send} ?".encode("ascii"))
            ret = self._connection.read_until(self._prompt + command_to_send.encode("ascii"), timeout=5)
            response = ret.decode("utf-8").splitlines()
            # Use o comando substituído para construir a árvore
            cmds = self._parse_guest_response(command_to_send, response, start=1, end=len(response) - 1)
            commands.extend(cmds)
            self._connection.write(self.ESCAPE_CHAR)
        logging.debug(f"Comandos do nível 3 guest: {commands}")
        return commands

    def get_guest_commands4(self) -> List[str]:
        """
        Obtém os comandos do nível 4 guest.
        """
        logging.info("Obtendo os comandos do nível 4 guest...")
        commands: List[str] = []
        for base_cmd in self._commands_guest3:
            # Aplica os placeholders para obter o comando final
            command_to_send = self.substitute_placeholders(base_cmd, PLACEHOLDERS_GUEST4, root_command=base_cmd)
            self._connection.write(f"{command_to_send} ?".encode("ascii"))
            ret = self._connection.read_until(self._prompt + command_to_send.encode("ascii"), timeout=5)
            response = ret.decode("utf-8").splitlines()
            # Use o comando substituído para construir a árvore
            cmds = self._parse_guest_response(command_to_send, response, start=1, end=len(response) - 1)
            commands.extend(cmds)
            self._connection.write(self.ESCAPE_CHAR)
        logging.debug(f"Comandos do nível 4 guest: {commands}")
        return commands

