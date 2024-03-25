import io
import logging
import os
import pickle

import cv2
import numpy as np
from PIL import Image
from insightface.app import FaceAnalysis
from tqdm import tqdm

from utils.db import sync_db_with_scud

logger = logging.getLogger("logger")


def bytes_to_cv(bytes_image):
    pil_image = Image.open(io.BytesIO(bytes_image))
    pil_image = pil_image.convert('RGB')
    open_cv_image = np.array(pil_image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image


def get_or_create_encodings():
    app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_thresh=0.7, det_size=(256, 256))

    encodings_path = os.path.join('data', 'enc')
    employees = sync_db_with_scud()

    data = None

    if os.path.exists(encodings_path):
        logger.info('Открытие файла кодировок...')
        try:
            with open(encodings_path, "rb") as file:
                data = pickle.load(file)
        except Exception as ex:
            logger.exception(f'При попытке открытия файла {encodings_path} возникло исключение: {ex}')

    if employees:
        ids = employees['ids']
        if data:
            logger.info('Поиск изменений...')
            changes = list(set(data['ids']) ^ set(ids))
            logger.info(f'Найдено {len(changes)} изменений')
        else:
            data = {"ids": [], "photos": [], "encodings": [], "names": []}
            changes = ids

        if len(changes) > 0:
            logger.info('Создание кодировок...')

        delete = []
        new_counter = 0
        created_counter = 0
        if changes:
            for emp_id in tqdm(changes, colour='green'):
                if emp_id not in ids:
                    delete.append(emp_id)
                    continue
                new_counter += 1
                i = ids.index(emp_id)
                name = employees['names'][i]
                cv_image = bytes_to_cv(employees['photos'][i])
                encodings = app.get(cv_image)
                for encoding in encodings:
                    try:
                        data["ids"].append(emp_id)
                        data["photos"].append(cv2.resize(cv_image, (0, 0), fx=0.3, fy=0.3))
                        data["encodings"].append(encoding.embedding)
                        data["names"].append(name)
                        created_counter += 1
                    except Exception as ex:
                        logger.exception(ex)
            logger.info(f'Создано кодировок: {created_counter} из {new_counter}')

        if delete:
            logger.info('Удаление старых кодировок...')
            for emp_id in delete:
                i = data["ids"].index(emp_id)
                for key in data.keys():
                    data[key].pop(i)
            logger.info(f'Удалено кодировок: {len(delete)}')

        if len(changes) > 0:
            logger.info('Сохранение файла с кодировками...')
            with open(encodings_path, "wb") as file:
                pickle.dump(data, file)
    elif not data:
        logger.warning('Файл с кодировками не создан!')
    return data
