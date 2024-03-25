import io
import logging

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger('logger')


def cv_image_to_bytes(image: np.ndarray) -> bytes:
    """
    Преобразование изображения в байты.
    :param image: Изображение в виде массива ndarray
    :return: Массив байтов
    """
    _, image = cv2.imencode(".jpg", image)
    byte_image = image.tobytes()
    return byte_image


def bytes_to_cv(bytes_image: bytes) -> np.ndarray:
    """
    Преобразование изображения из байтов в ndarray.
    :param bytes_image: Изображение в виде массива байтов
    :return: Изображение в виде массива ndarray
    """
    pil_image = Image.open(io.BytesIO(bytes_image))
    pil_image = pil_image.convert('RGB')
    open_cv_image = np.array(pil_image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image


def add_name(frame: np.ndarray, name: str, box: list, color: tuple) -> np.ndarray:
    """
    Добавляет рамку с именем.
    :param frame: Изображение в виде массива ndarray
    :param name: Имя для отображения в рамке
    :param box: Границы рамки
    :param color: Цвет рамки
    :return: Изображение в виде массива ndarray
    """
    if len(box) > 4:
        y1, x2, y2, x1 = box[:5]
    else:
        x1, y1, x2, y2 = box

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
    font = cv2.FONT_HERSHEY_COMPLEX
    parts = name.split()
    scale = ((x2 - x1) / 11.5) / max(map(len, parts))
    offset = 5
    cv2.rectangle(frame, (x1, y1), (x2, int(y1 - offset - 15 * len(parts) * scale)), color, -1)
    for name_part in parts[::-1]:
        cv2.putText(frame, name_part, (x1, y1 - offset), font, 0.5 * scale, (0, 0, 0), 1)
        offset += int(15 * scale)
    return frame


def add_source_photo(frame: np.ndarray, photo: np.ndarray) -> np.ndarray:
    """
    Добавляет исходное фото на кадр.
    :param frame: Кадр в виде массива ndarray
    :param photo: Исходное фото
    :return: Изображение в виде массива ndarray
    """
    try:
        frame_height, _, _ = frame.shape

        min_photo = photo
        img_height, img_width, _ = min_photo.shape

        y = 150
        x = int(img_width * y / img_height)

        min_photo = cv2.resize(min_photo, (x, y))

        img_height, img_width, _ = min_photo.shape

        x = 20
        y = int(frame_height - img_height - 10)
        new_frame = np.copy(frame)
        new_frame[y: y + img_height, x: x + img_width] = min_photo
        return new_frame
    except Exception as ex:
        logger.error(f"При добавлении фото на кадр возникло исключение: {ex}")
        return frame


def convert_image_to_bytes(image: str | np.ndarray) -> bytes:
    """
    Преобразование изображения в байты
    :param image: Путь к файлу с изображением или массив ndarray
    :return: Массив байтов
    """
    if isinstance(image, str):
        image = cv2.imread(image)
    elif not isinstance(image, np.ndarray):
        raise TypeError(
            "Передайте путь к изображению в виде строки или изображение в виде numpy массива"
        )
    ret, image = cv2.imencode(".jpg", image)
    image = image.tobytes()
    return image
