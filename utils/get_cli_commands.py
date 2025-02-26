import telnetlib
import logging
import re
import os
from typing import List, Union, Tuple, Callable

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("terminal.log"), logging.StreamHandler()]
)

PlaceholderType = Tuple[str, Union[str, List[str], Callable[[re.Match], str]]]

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
    (r"INTEGER<(\d+)-(\d+)>(?:>*)", lambda m: str(max(int(m.group(1)), int(m.group(2))))),
    (r"HEX<0-FFFFFFFF>", "F"),
    (r"HEX<0-FFFFFFFFFFFFFFFE>", "F"),
    (r"H-H-H", "1-1-1"),
    (r"STRING", "Teste.py"),
]

PLACEHOLDERS_GUEST4: List[PlaceholderType] = [
    (r"STRING<4-4>", "4444"),
    (r"STRING<1-63>", "1"),
    (r"INTEGER<(\d+)-(\d+)>(?:>*)", lambda m: str(max(int(m.group(1)), int(m.group(2))))),
] + BASE_PLACEHOLDERS_NO_STRING + [
    (r"INTEGER<(\d+)-(\d+)>(?:>*)", lambda m: str(max(int(m.group(1)), int(m.group(2))))),
    (r"<(\d+)-(\d+)>", lambda m: m.group(1) if m.group(1) == m.group(2) else "1"),
    (r"HEX<0-FFFFFFFF>", "0"),
    (r"HEX<\d+-\d+>", "1"),
    (r"DATE", "08/12/2012"),
    (r"X.X.X.X", "1.1.1.1"),
    (r"<1-2>", "1/0/33"),
    (r"<0-0>", "0"),
    (r"H-H-H", "1-1-1"),
    (r"STRING", "teste.tar"),
]

PLACEHOLDERS_GUEST5: List[PlaceholderType] = [
    (r"STRING<(\d+)-(\d+)>", lambda m: str(max(int(m.group(1)), int(m.group(2))))),
] + BASE_PLACEHOLDERS_NO_STRING + [
    (r"INTEGER<(\d+)-(\d+)>", lambda m: str(max(int(m.group(1)), int(m.group(2))))),
    (r"INTEGER<0,3,16-1048575>", "0"),
    (r"<2>", "2"),
    (r"<1-2>", "2"),
    (r"<0-0>", "0"),
    (r"<1-1>", ["1/0/1", "1"]),
    (r"HEX<1-FFFE>", "F"),
    (r"HEX<1-FFFFFFFF>", "1"),
    (r"HEX<1-FFFFFFFFFFFFFFFE>", "1"),
    (r"HEX<0-FFFFFFFF>", "0"),
    (r"HEX<0-FFFFFFFFFFFFFFFE>", "F"),
    (r"HEX<\d+-\d+>", "1"),
    (r"DATE", "08/12/2012"),
    (r"STRING", ["Teste.py", "teste.tar"]),
    (r"STRING<1-63>", "Teste"),
    (r"STRING<1-31>", "Teste"),
    (r"H-H-H", "1-1-1"),
]

class GetCommands:
    def __init__(self, modelo: str, ip: str, password: str, hostname: str) -> None:
        self._modelo = modelo
        self._ip = ip
        self._password = password
        self._hostname = hostname
        self._prompt = f"<{hostname}>".encode("ascii")
        self._connection = telnetlib.Telnet(ip)
        logging.info(f"Conectando a {ip}")
        self._version_data = self.new_connection(user="admin", password=password, hostname=hostname)
        self._commands_guest1 = self.get_guest_commands1()
        self._commands_guest2 = self.get_guest_commands2()
        self._commands_guest3 = self.get_guest_commands3()
        self.enter_sys_mode()
        self._commands_sys1 = self.get_sys_commands1()
        self._commands_sys2 = self.get_sys_commands2()
        self._commands_sys3 = self.get_sys_commands3()

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

    @property
    def sys_prompt(self) -> bytes:
        return f"[{self._hostname}]".encode("ascii")

    def new_connection(self, *, user: str, password: str, hostname: str) -> List[str]:
        try:
            logging.info("Login via Telnet")
            ret = self._connection.read_until(b":", timeout=5)
            if b"Login:" in ret:
                self._connection.write(f"{user}\n".encode("ascii"))
                logging.debug(f"Login: {user}")
            ret = self._connection.read_until(b":", timeout=3)
            if b"Password:" in ret:
                self._connection.write(f"{password}\n".encode("ascii"))
                logging.debug("Senha enviada")
            else:
                logging.error("Erro de login")
                raise ConnectionError("Erro no Login")
            ret = self._connection.read_until(self._prompt)
            if self._prompt in ret:
                self._connection.write(b"screen-length disable\n")
                ret = self._connection.read_until(self._prompt)
                if self._prompt in ret:
                    version = self.get_firmware_version()
                    logging.info(f"Firmware: {version[0]}")
                    print(f"Version: {version[0]}")
                else:
                    logging.error("Erro ao desabilitar paginação")
                    raise RuntimeError("Erro ao desabilitar paginação")
            else:
                logging.error("Hostname não encontrado")
                raise ConnectionError("Hostname não encontrado")
            return version
        except Exception as e:
            logging.error(f"Erro: {e}")
            raise

    def get_firmware_version(self) -> List[str]:
        version: List[str] = []
        try:
            logging.info("Obtendo versão do firmware")
            self._connection.write(b"display version\n")
            raw_response = self._connection.read_until(self._prompt).decode("utf-8")
            os_version_match = re.search(
                r"INTELBRAS OS Software,\s*Version\s*([\d\.]+,\s*(?:ESS\s*\d+|Release\s*\d+))", raw_response
            )
            boot_version_match = re.search(
                r"Boot image version:\s*([\d\.]+,\s*(?:ESS\s*\d+|Release\s*\d+))", raw_response
            )
            compiled_match = re.search(
                r"Compiled\s+([A-Za-z]+\s+\d+\s+\d+\s+[\d:]+)", raw_response
            )
            if not os_version_match or not boot_version_match or not compiled_match:
                logging.error("Erro ao extrair versão")
                raise ValueError("Formato da resposta inválido")
            version.extend([
                os_version_match.group(1).strip(),
                boot_version_match.group(1).strip(),
                compiled_match.group(1).strip()
            ])
            logging.info(f"Versão extraída: {version}")
        except Exception as e:
            logging.error(f"Erro ao obter versão: {e}")
            raise
        return version

    def substitute_placeholders(self, command: str, placeholders: List[PlaceholderType], root_command: str = "") -> str:
        for pattern, replacement in placeholders:
            if pattern == r"STRING":
                candidate = "teste.tar" if "tar" in root_command.lower() else (replacement[0] if isinstance(replacement, list) else replacement)
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
                    command = re.sub(pattern, replacement[0], command)
            elif callable(replacement):
                command = re.sub(pattern, replacement, command)
            else:
                command = re.sub(pattern, replacement, command)
        return command

    def get_guest_commands1(self) -> List[str]:
        logging.info("Obtendo comandos guest nível 1")
        commands: List[str] = []
        self._connection.write(b"?")
        ret = self._connection.read_until(self._prompt).decode("utf-8").splitlines()
        for line in ret[2:-1]:
            if line.strip() and "?" not in line:
                cmd = line[1:].split("  ")[0].replace(" ", "")
                if cmd:
                    commands.append(cmd)
        logging.debug(f"Guest 1: {commands}")
        return commands

    def _parse_guest_response(self, base_command: str, response_lines: List[str], start: int = 0, end: Union[int, None] = None) -> List[str]:
        commands: List[str] = []
        if end is None:
            end = len(response_lines)
        for i in range(start, end):
            line = response_lines[i].strip()
            if not line:
                continue
            lower_line = line.lower()
            if lower_line.startswith("system view commands:") or lower_line in ("system", "[ap7739]system"):
                continue
            if "^" in line or "%" in line or "unrecognized" in lower_line:
                continue
            if line.startswith("[") and line.endswith("]"):
                continue
            tokens = line.split()
            if tokens:
                subcommand = tokens[0]
                if subcommand:
                    commands.append(f"{base_command} {subcommand}")
        return commands

    def get_guest_commands2(self) -> List[str]:
        logging.info("Obtendo comandos guest nível 2")
        commands: List[str] = []
        for base_cmd in self._commands_guest1:
            self._connection.write(f"{base_cmd} ?".encode("ascii"))
            ret = self._connection.read_until(self._prompt + base_cmd.encode("ascii"), timeout=5)
            response = ret.decode("utf-8").splitlines()
            cmds = self._parse_guest_response(base_cmd, response, start=1, end=len(response) - 1)
            commands.extend(cmds)
            self._connection.write(self.ESCAPE_CHAR)
        logging.debug(f"Guest 2: {commands}")
        return commands

    def get_guest_commands3(self) -> List[str]:
        logging.info("Obtendo comandos guest nível 3")
        commands: List[str] = []
        for base_cmd in self._commands_guest2:
            command_to_send = self.substitute_placeholders(base_cmd, PLACEHOLDERS_GUEST3, root_command=base_cmd)
            self._connection.write(f"{command_to_send} ?".encode("ascii"))
            ret = self._connection.read_until(self._prompt + command_to_send.encode("ascii"), timeout=5)
            response = ret.decode("utf-8").splitlines()
            cmds = self._parse_guest_response(command_to_send, response, start=1, end=len(response) - 1)
            commands.extend(cmds)
            self._connection.write(self.ESCAPE_CHAR)
        logging.debug(f"Guest 3: {commands}")
        return commands

    def enter_sys_mode(self) -> None:
        logging.info("Entrando no modo sys")
        self._connection.write(b"sys\n")
        ret = self._connection.read_until(self.sys_prompt, timeout=5)
        if self.sys_prompt not in ret:
            logging.error("Falha ao entrar no modo sys")
            raise ConnectionError("Não foi possível entrar no modo sys.")
        logging.info("Modo sys ativado")

    def get_sys_commands1(self) -> List[str]:
        logging.info("Obtendo comandos sys nível 1")
        sys_commands: List[str] = []
        self._connection.write(b"?\n")
        ret = self._connection.read_until(self.sys_prompt, timeout=5).decode("utf-8")
        for line in ret.splitlines()[2:-1]:
            if line.strip() and "?" not in line:
                cmd = line.strip().split()[0]
                if cmd:
                    sys_commands.append(cmd)
        logging.debug(f"Sys 1: {sys_commands}")
        return sys_commands

    def get_sys_commands2(self) -> List[str]:
        logging.info("Obtendo comandos sys nível 2")
        commands: List[str] = []
        for base_cmd in self._commands_sys1:
            self._connection.write(f"{base_cmd} ?".encode("ascii"))
            ret = self._connection.read_until(self.sys_prompt + base_cmd.encode("ascii"), timeout=5)
            response = ret.decode("utf-8").splitlines()
            cmds = self._parse_guest_response(base_cmd, response, start=1, end=len(response) - 1)
            commands.extend(cmds)
            self._connection.write(self.ESCAPE_CHAR)
        logging.debug(f"Sys 2: {commands}")
        return commands

    def get_sys_commands3(self) -> List[str]:
        logging.info("Obtendo comandos sys nível 3")
        commands: List[str] = []
        for base_cmd in self.get_sys_commands2():
            command_to_send = self.substitute_placeholders(base_cmd, [], root_command=base_cmd)
            self._connection.write(f"{command_to_send} ?".encode("ascii"))
            ret = self._connection.read_until(self.sys_prompt + command_to_send.encode("ascii"), timeout=5)
            response = ret.decode("utf-8").splitlines()
            cmds = self._parse_guest_response(base_cmd, response, start=1, end=len(response) - 1)
            commands.extend(cmds)
            self._connection.write(self.ESCAPE_CHAR)
        logging.debug(f"Sys 3: {commands}")
        return commands

    def return_lists(self) -> dict:
        return {
            "version_data": self._version_data,
            "commands_guest1": self._commands_guest1,
            "commands_guest2": self._commands_guest2,
            "commands_guest3": self._commands_guest3,
            "commands_sys1": self._commands_sys1,
            "commands_sys2": self._commands_sys2,
            "commands_sys3": self._commands_sys3,
        }

    # def get_guest_commands4(self) -> List[str]:
    #     """
    #     Captura os comandos de nível 4 (guest).
    #     """
    #     logging.info("Obtendo os comandos do nível 4 guest...")
    #     commands: List[str] = []
    #     for base_cmd in self._commands_guest3:
    #         command_to_send = self.substitute_placeholders(base_cmd, PLACEHOLDERS_GUEST4, root_command=base_cmd)
    #         self._connection.write(f"{command_to_send} ?".encode("ascii"))
    #         ret = self._connection.read_until(self._prompt + command_to_send.encode("ascii"), timeout=5)
    #         response = ret.decode("utf-8").splitlines()
    #         cmds = self._parse_guest_response(command_to_send, response, start=1, end=len(response) - 1)
    #         commands.extend(cmds)
    #         self._connection.write(self.ESCAPE_CHAR)
    #     logging.debug(f"Comandos do nível 4 guest: {commands}")
    #     return commands

    # def get_guest_commands5(self) -> List[str]:
    #     """
    #     Captura os comandos de nível 5 (guest).
    #     """
    #     logging.info("Obtendo os comandos do nível 5 guest...")
    #     commands: List[str] = []
    #     for base_cmd in self._commands_guest4:
    #         command_to_send = self.substitute_placeholders(base_cmd, PLACEHOLDERS_GUEST5, root_command=base_cmd)
    #         logging.debug(f"Enviando comando para o DUT: {command_to_send} ?")
    #         self._connection.write(f"{command_to_send} ?".encode("ascii"))
    #         ret = self._connection.read_until(self._prompt + command_to_send.encode("ascii"), timeout=5)
    #         response = ret.decode("utf-8").splitlines()
    #         logging.debug("Saída completa do DUT:")
    #         for line in response:
    #             logging.debug(line)
    #         cmds = self._parse_guest_response(base_cmd, response, start=1, end=len(response) - 1)
    #         commands.extend(cmds)
    #         self._connection.write(self.ESCAPE_CHAR)
    #     logging.debug(f"Comandos do nível 5 guest: {commands}")
    #     return commands
