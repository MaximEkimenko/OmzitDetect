import json
import logging
from typing import BinaryIO

import requests

logger = logging.getLogger('logger')


def post_data_to_server(server_url: str, endpoint: str, data: dict) -> bool:
    """Направляет данные на сервер"""
    success = False
    try:
        logger.info(f'Отправка данных на сервер {server_url}')
        response = requests.post(url=f'{server_url}{endpoint}', data=json.dumps(data))
        if response.status_code == 200:
            logger.info(f'Настройки сервиса направлены на сервер {server_url}')
            success = True
        else:
            logger.error(f'При обращении к серверу по адресу '
                         f'{server_url}{endpoint} получен статус код: {response.status_code}')
    except Exception as ex:
        logger.error(f'При обращении к серверу по адресу {server_url}{endpoint} вызвано исключение: {ex}')

    return success


def post_file_to_server(server_url: str, endpoint: str, file: BinaryIO) -> bool:
    """Направляет файл на сервер"""
    success = False
    try:
        logger.info(f'Отправка файла на сервер {server_url}')
        files = {'file': ('enc', file)}
        response = requests.post(url=f'{server_url}{endpoint}', files=files)
        if response.status_code == 200:
            logger.info(f'Файл направлен на сервер {server_url}')
            success = True
        else:
            logger.error(f'При обращении к серверу по адресу '
                         f'{server_url}{endpoint} получен статус код: {response.status_code}')
    except Exception as ex:
        logger.error(f'При обращении к серверу по адресу {server_url}{endpoint} вызвано исключение: {ex}')

    return success
