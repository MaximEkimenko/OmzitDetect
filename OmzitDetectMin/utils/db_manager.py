import logging
import socket
from datetime import datetime

from sqlalchemy import create_engine, DateTime, String, URL, LargeBinary, func
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

from conf import DETECT_PG_DB

logger = logging.getLogger("logger")

connection_url = URL.create(**DETECT_PG_DB)

engine = create_engine(connection_url)


class Base(DeclarativeBase):
    pass


class Detection(Base):
    __tablename__ = 'detection'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    datetime: Mapped[datetime] = mapped_column(DateTime(), default=func.now())
    photo: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
    source: Mapped[str] = mapped_column(String(255))


Base.metadata.create_all(engine)


def create(model, **kwargs) -> None:
    with Session(autoflush=False, bind=engine) as db:
        record = model(**kwargs)
        db.add(record)
        try:
            db.commit()
        except Exception as ex:
            logger.exception(ex)


def get_source_records(source: str) -> list:
    with Session(autoflush=False, bind=engine) as db:
        records = db.query(Detection).filter(Detection.source == source)
        results = []
        for record in records:
            results.append(
                [
                    record.id,
                    record.name,
                    record.datetime.strftime("%d.%m.%Y %H:%M:%S"),
                    f'<a href="http://{socket.gethostname()}:8000/show_photo/{record.id}/">Show photo<a>',
                    record.source,
                ]
            )
        return results


def get_source_records_xlsx(source: str) -> list:
    with Session(autoflush=False, bind=engine) as db:
        records = db.query(Detection).filter(Detection.source == source)
        results = []
        for record in records:
            results.append(
                [
                    record.id,
                    record.name,
                    record.datetime.strftime("%d.%m.%Y %H:%M:%S"),
                    f'http://{socket.gethostname()}:8000/show_photo/{record.id}/',
                    record.source,
                ]
            )
        return results


def get_photo(record_id: int):
    with Session(autoflush=False, bind=engine) as db:
        photo = db.query(Detection.photo).filter(Detection.id == record_id).first()
        return photo
