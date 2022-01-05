import http.client as httplib
import json
import os
import platform
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import (
    NoReturn,
    Optional,
    Dict,
    Union
)

from main import *

ip_address: str = '192.168.132.42'
@dataclass
class Bridge:

    ip_address: Optional[str] = None
    username: Optional[str] = None
    config_file_path: Optional[str or Path] = None

    @property
    def name(self) -> str:
        self._name = self.request('GET', f'/api/{self.username}/config')['name']
        return self._name

    @name.setter
    def name(self, value: str) -> NoReturn:
        self._name = value
        data: Dict = dict(name = self._name)
        self.request('PUT', f'/api/{self.username}/config', data)

    @classmethod
    def config_file_verification(self) -> NoReturn:

        if os.getenv(USER_HOME) is not None and os.access(os.getenv(USER_HOME), os.W_OK):
            self.config_file_path = os.path.join(os.getenv(USER_HOME), '.python_hue')
        elif platform.machine() in ['iPad', 'iPhone']:
            self.config_file_path = os.path.join(os.getenv(USER_HOME), 'Documents', '.python_hue')
        else:
            self.config_file_path = os.path.join(os.getcwd(), '.python_hue')

    def request(self, mode: str = 'GET', address: Optional[str] = None, data: Optional[Dict] = None) -> NoReturn:
        connection = httplib.HTTPConnection(self.ip_address, timeout= 10)

        try:
            if mode in ('GET', 'DELETE'):
                connection.request(mode, address)

            if mode in ('PUT', 'POST'):
                connection.request(mode, address, str(data))

            logger.debug(f"{mode} {address} {str(data)}")

        except socket.timeout:
            error: str = f"{mode} Request to {self.ip_address} from {address} timed out."
            logger.exception((error))
            raise TimeoutError(None, error)

        result = connection.getresponse()
        response = result.read()

        connection.close()

        if PY3K:
            response = response.decode('utf-8')
        logger.debug(response)
        return json.loads(response)

    def get_ip_address(self, set_result: bool = False) -> Union[str, bool]:

        connection = httplib.HTTPSConnection('www.meethue.com')
        connection.request('GET', '/api/nupnp')

        logger.info('Connecting to meethue.com/api/nupnp')

        result = connection.getresponse()

        if PY3K:
            string = str(result.read(), encoding='utf-8')
            data = json.loads(string)
        else:
            result_str = result.read()
            data = json.loads(result_str)

        connection.close()

        ip = str(data[0]['internalipaddress'])

        if ip:
            if set_result:
                self.ip_address = ip

            return ip
        else:
            return False

    def __post_init__(self):

        self.config_file_verification()
        self.connect()

    def connect(self) -> NoReturn:

        logger.info(
            """
            Trying to connect to Bridge.
            """
        )

        if {self.ip_address, self.username} is not None:
            logger.info(
                f"""
                Connecting to {self.ip_address} as {self.username}.
                """
            )
        else:
            try:
                with open(self.config_file_path) as file:

                    config = json.load(file.read())

                    if self.ip_address is None:
                        self.ip_address = list(config.keys())[0]
                        logger.info(
                            f"Using obtained ip_address {self.ip_address} from config."
                        )
                    else:
                        logger.info(
                            f"Using ip_address: {self.ip_address}"
                        )

                    if self.username is None:
                        self.username = config.get(self.ip_address)['username']
                        logger.info(
                            f"Using obtained username {self.username} from config."
                        )
                    else:
                        logger.info(
                            f"Using username: {self.username}."
                        )
            except Exception as e:
                logger.info(
                    """
                    There was an error trying to open the config file.
                    Attempting to register Bridge peripheral.
                    """
                )

                self.registration()

    def registration(self):

        registration_request: Dict = dict(
            devicetype = 'python_hue'
        )
        response = self.request('POST', '/api', registration_request)

        for line in response:

            for key in line:

                if 'success' in key:
                    with open(self.config_file_path, 'w') as file:
                        logger.info(
                            'Writing configuration file to ' + self.config_file_path)
                        file.write(json.dumps({self.ip: line['success']}))
                        logger.info('Reconnecting to the bridge')
                    self.connect()

                if 'error' in key:
                    error_type = line['error']['type']

                    if error_type == 101:
                        raise Exception(error_type, "The link button hasn't been pressed recently.")

                    if error_type == 7:
                        raise Exception(error_type, "Unknown username used.")

b = Bridge(ip_address)
b.connect()