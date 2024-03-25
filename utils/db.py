import logging
from typing import Optional, Any

from sqlalchemy import create_engine, String, URL, LargeBinary, JSON
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

from conf import DETECT_PG_DB
from utils.b2p import get_scud_employees_data

logger = logging.getLogger("logger")

connection_url = URL.create(**DETECT_PG_DB)

engine = create_engine(connection_url)


class Base(DeclarativeBase):
    pass


class EmployeePhoto(Base):
    """Модель с фотографиями сотрудников"""
    __tablename__ = 'employee'

    id: Mapped[int] = mapped_column(primary_key=True)
    scud_id: Mapped[Optional[int]]
    name: Mapped[str] = mapped_column(String(255))
    department: Mapped[Optional[str]] = mapped_column(String(255))
    photo: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)


class Source(Base):
    """Модель источников видео"""
    __tablename__ = 'sources'

    id: Mapped[int] = mapped_column(primary_key=True)
    hostname: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))
    source_name: Mapped[str] = mapped_column(String(255))
    settings: Mapped[dict[str: Any]] = mapped_column(JSON)


Base.metadata.create_all(engine)


def create(model, **kwargs) -> None:
    with Session(autoflush=False, bind=engine) as db:
        record = model(**kwargs)
        db.add(record)
        try:
            db.commit()
        except Exception as ex:
            logger.exception(ex)


def update_source_settings(hostname: str, source_name: str, settings: dict) -> None:
    with Session(autoflush=False, bind=engine) as db:
        source = db.query(Source).filter(
            Source.hostname == hostname, Source.source_name == source_name
        ).first()
        source.source_name = settings["name"]
        source.settings = settings
        try:
            db.commit()
        except Exception as ex:
            logger.exception(ex)


def bulk_create(model, records) -> None:
    with Session(autoflush=False, bind=engine) as db:
        add_records = []
        for record in records:
            add_records.append(model(**record))
        db.add_all(add_records)
        try:
            db.commit()
        except Exception as ex:
            logger.exception(ex)


def get_sources_list() -> list:
    with Session(autoflush=False, bind=engine) as db:
        rows = db.query(Source)
        sources = []
        for row in rows:
            sources.append(
                {
                    'hostname': row.hostname,
                    'address': row.address,
                    'source_name': row.source_name
                }
            )
    return sources


def get_source_data(hostname: str, source_name: str) -> dict:
    with Session(autoflush=False, bind=engine) as db:
        source = db.query(Source).filter(Source.hostname == hostname, Source.source_name == source_name).first()
        source = (
            {
                'hostname': source.hostname,
                'address': source.address,
                'source_name': source.source_name,
                'settings': source.settings
            }
        )
    return source


def get_host_settings(hostname: str) -> dict:
    with Session(autoflush=False, bind=engine) as db:
        sources = db.query(Source).filter(Source.hostname == hostname)
        host_data = {
            "address": '',
            "settings_list": []
        }
        for source in sources:
            host_data["address"] = source.address
            host_data["settings_list"].append(source.settings)

        return host_data


def delete_host_sources(hostname):
    with Session(autoflush=False, bind=engine) as db:
        db.query(Source).filter(Source.hostname == hostname).delete()
        db.commit()


def sync_db_with_scud() -> dict:
    scud_employees = get_scud_employees_data()
    if scud_employees:
        scud_ids = {emp['scud_id'] for emp in scud_employees}
        with Session(autoflush=False, bind=engine) as db:
            employees = db.query(EmployeePhoto).filter(EmployeePhoto.scud_id is not None)
            ids = {employee.scud_id for employee in employees}
            deleted_ids = list(ids - scud_ids)
            if deleted_ids:
                employees.filter(EmployeePhoto.scud_id.in_(deleted_ids)).delete()
                db.commit()
        created_ids = list(scud_ids - ids)
        if created_ids:
            created = list(filter(lambda x: x['scud_id'] in created_ids, scud_employees))
            bulk_create(EmployeePhoto, created)
        logger.info(f'Синхронизация со СКУД завершена')

        with Session(autoflush=False, bind=engine) as db:
            rows = db.query(EmployeePhoto)
            employees = {'ids': [], 'names': [], 'photos': []}
            for row in rows:
                employees['ids'].append(row.id)
                employees['names'].append(row.name)
                employees['photos'].append(row.photo)
        return employees


def new_employee(**kwargs):
    create(EmployeePhoto, **kwargs)

