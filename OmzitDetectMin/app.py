import json
import logging
import os.path
import socket
from typing import List

import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from conf import CENTRAL_SERVER_URL, SOURCES, SERVER_HOSTNAME, SETTINGS_PATH
from fastapi import FastAPI, UploadFile
from starlette.responses import StreamingResponse, Response, FileResponse

from utils.db_manager import get_source_records, get_photo, get_source_records_xlsx
from utils.image_tools import convert_image_to_bytes
from utils.process_manager import run_sources, stop_sources, run_i_started

app_min = FastAPI(title=f'ODM {socket.gethostname()}')

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://localhost",
    CENTRAL_SERVER_URL,
    f"http://{socket.gethostbyname(SERVER_HOSTNAME)}:8000",
]

app_min.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger('logger')

run_i_started(server_url=CENTRAL_SERVER_URL, endpoint='/api/i_started/', data=SOURCES)

FRAMES = run_sources()


class CreateSettings(BaseModel):
    video_source: str


class StartSettings(BaseModel):
    unknown_save_step: int = 10
    skipped_frames_coeff: int = 50
    faces_distance: float = 0.6
    intervals: list
    crop: list
    width: int


class VideoSettings(BaseModel):
    name: str
    create: CreateSettings
    start: StartSettings


@app_min.get("/start/")
def start_stream():
    global FRAMES
    FRAMES = run_sources()


@app_min.get("/video_stream/{source}")
def video_stream(source: str):
    if FRAMES is None:
        image_bytes = convert_image_to_bytes(os.path.join("data", "no-video.png"))
        return Response(content=image_bytes, media_type="image/png")
    return StreamingResponse(content=FRAMES[source], media_type="multipart/x-mixed-replace;boundary=frame")


@app_min.get("/stop/")
def stop_stream():
    global FRAMES
    stop_sources()
    FRAMES = None


@app_min.post("/settings/")
def update_settings(settings: List[VideoSettings]):
    global FRAMES
    stop_sources()
    settings = list(map(lambda x: x.dict(), settings))
    try:
        with open(SETTINGS_PATH, "w") as saved_file:
            json.dump(settings, saved_file)
        FRAMES = run_sources()
    except Exception as ex:
        logger.error(f'При попытке сохранения настроек возникло исключение: {ex}')


@app_min.get("/ping/{source}")
def ping(source: str):
    video_started = FRAMES is not None and FRAMES.get(source) is not None
    return {"video": video_started}


@app_min.get("/records/{source}")
def get_records(source: str):
    records = get_source_records(source)
    return records


@app_min.get("/records/{source}/xlsx/")
def get_xlsx_records(source: str):
    df = pd.DataFrame(get_source_records_xlsx(source), columns=['id', 'name', 'datetime', 'photo', 'source'])
    file_path = os.path.join('data', 'records.xlsx')
    df.to_excel(file_path)
    return FileResponse(file_path)


@app_min.get("/show_photo/{record_id}/")
def get_records(record_id: int):
    photo = get_photo(record_id)[0]
    return Response(content=photo, media_type="image/jpeg")


@app_min.post("/upload_file/")
def upload_file(file: UploadFile):
    global FRAMES
    stop_sources()

    file_path = os.path.join("data", file.filename)
    with open(file_path, "wb") as image:
        image.write(file.file.read())

    FRAMES = run_sources()
    return {"filename": file.filename}
