import logging.config
import os
from pathlib import Path
from dotenv import load_dotenv

BASEDIR = Path(__file__).parent

if os.path.exists(BASEDIR / ".env"):
    load_dotenv()

DATA_PATH = BASEDIR / "data"

os.makedirs(DATA_PATH, exist_ok=True)

DETECT_LITE_DB = DATA_PATH / "db_detect.db"

SCUD_DB = {
    "drivername": "mssql+pyodbc",
    'host': "192.168.11.200",
    'database': "Orion15.11.2022",
    'username': "ASUP",
    'password': "qC4HptD",
    "query": {
        "driver": "ODBC Driver 17 for SQL Server",
        "TrustServerCertificate": "yes",
    },
}

DETECT_PG_DB = {
    "drivername": "postgresql+psycopg2",
    'host': "localhost",
    'database': "detect",
    'username': "admin",
    'password': "Epass1"
}


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
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
        "message_queue": {
            "format": "%(asctime)s %(levelname)s <span style='color: green;'>%(message)s</span>",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
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
            "filename": os.path.join("logs", "debug.log"),
        },
        "file_prod": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": os.path.join("logs", "production.log"),
        },
    },
    "loggers": {
        "logger": {
            "handlers": ["console", "file_prod"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
        },
        "": {
            "handlers": ["file_debug"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
        },
    },
}

logs_path = BASEDIR / 'logs'
os.makedirs(logs_path, exist_ok=True)

logging.config.dictConfig(LOGGING_CONFIG)