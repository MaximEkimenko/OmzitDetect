import logging
import os
import pickle
import time
from datetime import datetime
from math import ceil
from typing import Dict, Tuple, Optional

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.app.common import Face

from conf import DATA_PATH
from utils.image_tools import add_name, cv_image_to_bytes, add_source_photo
from scipy import spatial

from utils.db_manager import create, Detection

logger = logging.getLogger("logger")


class InsightFace:
    def __init__(self, name, video_source=0, db_path=DATA_PATH):
        self.app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_thresh=0.7, det_size=(256, 256))
        self.source_name = name
        self.db_path = db_path
        self.encodings = self.get_or_create_encodings()
        self.detected_faces = dict()

        logger.info('Получение данных с камеры...')
        if video_source == '0':
            self.video_source = 0
        else:
            self.video_source = video_source
        self.video_capture = cv2.VideoCapture(self.video_source)

    def get_or_create_encodings(self):
        encodings_path = os.path.join(self.db_path, 'enc')

        if os.path.exists(encodings_path):
            logger.info('Открытие файла кодировок...')
            try:
                with open(encodings_path, "rb") as file:
                    data = pickle.load(file)
                    return data
            except Exception as ex:
                logger.exception(f'При попытке открытия файла {encodings_path} возникло исключение: {ex}')

    def save_photo(self, frame, name, photo):
        frame = add_source_photo(frame, photo)
        create(Detection, name=name, photo=cv_image_to_bytes(frame), source=self.source_name)
        logger.debug(f"Сохранена запись для {name} в БД")

    @classmethod
    def recognize(cls, face: Face, encodings: Dict, distance: float) -> Optional[Tuple[str, np.ndarray]]:
        for i, encoding in enumerate(encodings['encodings']):
            result_distance = spatial.distance.cosine(face.embedding, encoding)
            if result_distance < distance:
                name = encodings['names'][i]
                photo = encodings['photos'][i]
                return name, photo
        return None

    def start(self, intervals, crop, width, unknown_save_step=10, skipped_frames_coeff=50, faces_distance=0.55):
        logger.info('В работе!')
        skipped_frames = 0  # количество пропускаемых кадров для синхронизации времени
        unknown_encodings = {"photos": [], "encodings": [], "names": []}
        time_to_save_db = False
        logger.info(f'Интервалы времени сохранения в базу данных: {intervals}')
        while True:

            for interval in intervals:
                hours_now = int(datetime.now().strftime('%H'))
                minutes_now = int(datetime.now().strftime('%M'))
                minutes = hours_now * 60 + minutes_now
                start_interval, end_interval = interval
                if start_interval <= minutes <= end_interval:
                    time_to_save_db = True
                else:
                    time_to_save_db = False

            ret, frame = self.video_capture.read()

            full_frame = np.copy(frame)
            top, bottom, left, right = crop
            frame_height, frame_width, _ = frame.shape
            frame = frame[top: (frame_height - bottom), left: (frame_width - right)]

            if not ret:
                logger.debug("Отсутствует подключение к видеопотоку! Восстановление подключения...")
                self.video_capture = cv2.VideoCapture(self.video_source)
                logger.info('В работе!')
                continue

            if skipped_frames == 0:
                start_detection = time.time()
                faces = self.app.get(frame)
                faces_found = True if faces else False
                boxes = []
                names = []
                for face in faces:
                    name_counter_step = 1
                    box = face.bbox.astype(np.int64)

                    known = self.recognize(face, self.encodings, faces_distance)
                    if known:
                        name, photo = known
                        name_counter_step = unknown_save_step
                        color = (0, 255, 0)
                    else:
                        unknown = self.recognize(face, unknown_encodings, faces_distance - 0.20)
                        if unknown:
                            name, photo = unknown
                            color = (255, 0, 0)
                        else:
                            name = str(time.time())
                            x1, y1, x2, y2 = box
                            photo = frame[y1 - 20:y2 + 20, x1 - 20:x2 + 20]
                            color = (0, 0, 255)
                            unknown_encodings['encodings'].append(face.embedding)
                            unknown_encodings['names'].append(name)
                            unknown_encodings['photos'].append(photo)

                    count = self.detected_faces.get(name, 0)
                    count += name_counter_step
                    self.detected_faces[name] = count

                    if count % unknown_save_step == 0 and time_to_save_db:
                        self.save_photo(
                            add_name(frame, name, box, color),
                            name,
                            photo
                        )

                    logger.info(f'Обнаружен(а): {name}')

                    boxes.append((box, color))
                    names.append(name)

                detection_time = time.time() - start_detection
                if faces_found:
                    skipped_frames = ceil(detection_time * skipped_frames_coeff)
            else:
                skipped_frames -= 1

            # отображаем рамки лиц, пока пропускаются кадры
            if faces_found:
                for box, name in zip(boxes, names):
                    box, color = box
                    frame = add_name(frame, name, box, color)

            full_frame[top: (frame_height - bottom), left: (frame_width - right)] = frame
            cv2.rectangle(full_frame, (left, top), ((frame_width - right), (frame_height - bottom)), (0, 0, 255), 2)

            ratio = width / frame_width
            full_frame = cv2.resize(full_frame, (int(width), int(frame_height * ratio)))

            ret, full_frame = cv2.imencode('.jpg', full_frame)
            full_frame = full_frame.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + full_frame + b'\r\n')
