from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session, sessionmaker

from src.config import Config

engine = create_engine(
    Config.assemble_db_connection(),
    pool_pre_ping=True,  # prevent stale connections that are in pool for long period of time but not connected to database.
    pool_size=500,  # maximum connections handle at a time.
    max_overflow=100,  # extra connections if all pool connections are in use.
    pool_recycle=60
    * 60,  # refresh a connection if it has been idle(present in pool but not in use) for more than given time.
    pool_timeout=30,  # before failing, wait for given time(seconds) to free a connection when all connections are in use.
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db

    except ProgrammingError as pe:
        print("###############################################")
        print("EITHER DATABASE NOT FOUND OR NO TABLES PRESENT")
        print("###############################################")
        return pe
    finally:
        db.close()


get_db = Annotated[Session, Depends(_get_db)]
