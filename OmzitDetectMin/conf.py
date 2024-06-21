import json
import logging.config
import os
from pathlib import Path
import socket

BASEDIR = Path(__file__).parent

DATA_PATH = BASEDIR / "data"

os.makedirs(DATA_PATH, exist_ok=True)

# CENTRAL_SERVER_URL = 'http://192.168.8.30:8080'
# CENTRAL_SERVER_URL = 'http://192.168.8.30:850'
CENTRAL_SERVER_URL = 'http://192.168.8.163:850'

DETECT_PG_DB = {
    "drivername": "postgresql+psycopg2",
    'host': "127.0.0.1",
    'database': "postgres",
    'username': "postgres",
    'password': "Epass1"
}


'rtsp://admin01:Epass1@192.168.9.15:554'

SOURCES = [
    {
        'name': socket.gethostname(),
        'create': {'video_source': '0'},
        'start': {
            'unknown_save_step': 10,
            'skipped_frames_coeff': 50,
            'faces_distance': 0.55,
            'intervals': [],
            'crop': [0, 0, 0, 0],
            'width': 1024
        },
    },
]

SETTINGS_PATH = DATA_PATH / "settings.json"

if os.path.exists(SETTINGS_PATH):
    with open(SETTINGS_PATH, 'r') as file:
        SOURCES = json.load(file)
else:
    with open(SETTINGS_PATH, 'w') as file:
        json.dump(SOURCES, file)

logs_path = BASEDIR / 'logs'
os.makedirs(logs_path, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "console": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(blue)s%(asctime)s: %(log_color)s%(levelname)-8s%(reset)s "
                      "%(white)s%(module)-11s %(lineno)-4s %(light_white)s%(message)s%(reset)s",
            "log_colors": {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
        },
        "file": {
            "format": "%(asctime)s %(levelname)-12s %(module)-12s %(lineno)-12s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": os.path.join(logs_path, "debug.log"),
        },
        "file_prod": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": os.path.join(logs_path, "production.log"),
        },
    },
    "loggers": {
        "logger": {
            "handlers": ["console", "file_debug"],
            "level": "DEBUG",
        },
        "": {
            "handlers": ["file_debug"],
            "level": "DEBUG",
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
