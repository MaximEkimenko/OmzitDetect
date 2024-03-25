import logging
import os
import socket
from typing import List, Annotated

from pydantic import BaseModel

from fastapi import FastAPI, Request, UploadFile, Form, File
from starlette import status
from starlette.responses import Response

from utils.db import Source, bulk_create, get_sources_list, delete_host_sources, get_source_data, \
    update_source_settings, get_host_settings, new_employee
from utils.encodings import get_or_create_encodings
from utils.requests_manager import post_data_to_server, post_file_to_server

logger = logging.getLogger("logger")

api_app = FastAPI(title=f"ODS {socket.gethostname()}")


class CreateSettings(BaseModel):
    video_source: str


class StartSettings(BaseModel):
    unknown_save_step: int = 10
    skipped_frames_coeff: int = 50
    faces_distance: float = 0.6
    intervals: list
    crop: list
    width: int = 1024


class VideoSettings(BaseModel):
    name: str
    create: CreateSettings
    start: StartSettings


@api_app.get("/sources/")
def get_sources():
    sources = get_sources_list()
    return sources


@api_app.get("/sources/{hostname}/{source}/")
def get_source(hostname: str, source: str):
    source_data = get_source_data(hostname, source)
    data = {
        'video_link': f'{source_data["address"]}/video_stream/{source}',
        'start_link': f'{source_data["address"]}/start/',
        'stop_link': f'{source_data["address"]}/stop/',
        'records_link': f'{source_data["address"]}/records/',
        'settings': source_data['settings'],
    }
    return data


@api_app.post("/sources/{hostname}/{source}/")
def save_source_data(hostname: str, source: str, settings: VideoSettings):
    update_source_settings(hostname, source, settings.dict())
    host_data = get_host_settings(hostname)
    success = post_data_to_server(
        server_url=host_data['address'],
        endpoint="/settings/",
        data=host_data["settings_list"]
    )
    return {'success': success}


@api_app.post("/i_started/")
def i_started(request: Request, settings: List[VideoSettings]):
    hostname = socket.gethostbyaddr(request.client.host)[0].split('.')[0]
    delete_host_sources(hostname=hostname)
    records = [
        {
            'hostname': hostname,
            'address': f'http://{hostname}:8000',
            'source_name': source_settings.dict()["name"],
            'settings': source_settings.dict()
        }
        for source_settings in settings
    ]
    bulk_create(Source, records)


@api_app.post("/employees/new/")
def create_employee(
        photo: Annotated[UploadFile, File()],
        name: Annotated[str, Form()],
        department: Annotated[str, Form()],
):
    data = {
        "name": name,
        "department": department,
        "photo": photo.file.read()
    }
    new_employee(**data)


@api_app.post("/employees/encodings/")
def update_encodings(response: Response):
    get_or_create_encodings()
    sources = get_sources_list()
    errors = []
    with open(os.path.join('data', 'enc'), 'rb') as file:
        for source in sources:
            success = post_file_to_server(server_url=source["address"], endpoint="/upload_file/", file=file)
            if not success:
                logger.error(f"Ошибка отправки файла кодировок на {source['address']}")
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                errors.append(f"Неудачная попытка отправки кодировок на сервис {source['address']}")
    return {'errors': errors}
