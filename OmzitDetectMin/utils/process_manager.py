import json
import os
from multiprocessing import Queue, Process
from typing import Generator

from utils.recognizer import InsightFace

from utils.image_tools import convert_image_to_bytes
from conf import SETTINGS_PATH
import logging

from utils.requests_manager import post_data_to_server

logger = logging.getLogger("logger")

ACTIVE_PROCESSES: list[Process] = []


def run_sources(settings_path: str = SETTINGS_PATH) -> dict:
    """
    Создает для всех источников видео генераторы кадров.
    :return: Словарь, где ключ - имя источника, значение - генератор кадров
    """
    running_sources = dict()
    with open(settings_path, 'r') as settings_file:
        sources_settings = json.load(settings_file)
    for source_settings in sources_settings:
        source_name = source_settings['name']
        frames = start_source_process(source_settings)
        running_sources[source_name] = frame_generator(frames)
    return running_sources


def frame_generator(frame_queue: Queue) -> Generator:
    """
    Генератор кадров
    :param: source_name: Очередь кадров
    :return: Генератор кадров
    """
    while True:
        try:
            yield frame_queue.get()
        except Exception as ex:
            logger.exception(ex)
            yield


def start_source_process(parameters: dict) -> Queue:
    """
    Запускает функцию распознавания для источника видео в отдельном процессе с отдельной очередью кадров
    :param: parameters: Параметры для источника видео
    :return: Очередь кадров для запущенного процесса
    """
    frame_queue = Queue()
    proc = Process(target=create_source_frame_queue, args=(frame_queue, parameters))
    proc.start()
    ACTIVE_PROCESSES.append(proc)
    return frame_queue


def create_source_frame_queue(frame_queue: Queue, parameters: dict) -> None:
    """
    Запускает распознавание с заданными параметрами и заполняет очередь кадров
    :param: parameters: Параметры для источника видео
    :param: frame_queue: Очередь кадров для обмена между порождающим процессом (длина очереди <= 3)
    """
    rec = InsightFace(name=parameters['name'], **parameters['create'])
    frames = rec.start(**parameters['start'])
    while True:
        frame_queue.put(next(frames))
        if frame_queue.qsize() > 3:
            frame_queue.get()


def stop_sources() -> None:
    """Останавливает все активные процессы"""
    for process in ACTIVE_PROCESSES:
        process.kill()


def run_i_started(server_url: str, endpoint: str, data: dict):
    proc = Process(target=post_data_to_server, args=(server_url, endpoint, data))
    proc.start()
