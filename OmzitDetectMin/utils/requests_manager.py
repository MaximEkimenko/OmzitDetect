import json
import logging
from time import sleep

import requests

logger = logging.getLogger('logger')


def post_data_to_server(server_url: str, endpoint: str, data: dict):
    """Направляет данные на сервер"""
    success = False
    while not success:
        try:
            logger.info(f'Отправка данных на сервер {server_url}')
            response = requests.post(url=f'{server_url}{endpoint}', data=json.dumps(data))
            if response.status_code == 200:
                logger.info(f'Настройки сервиса направлены на сервер {server_url}')
                success = True
                break
            else:
                logger.error(f'При обращении к серверу по адресу {server_url}{endpoint} получен статус код: {response.status_code}'
                             f'\nПовтор через 10 секунд')
                sleep(10)
        except Exception as ex:
            logger.error(f'При обращении к серверу по адресу {server_url}{endpoint} вызвано исключение: {ex} '
                         f'\nПовтор через 10 секунд')
            sleep(10)

