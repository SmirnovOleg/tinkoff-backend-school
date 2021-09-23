from contextlib import contextmanager
from typing import Any, Callable, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base, Film

engine = None
SessionLocal: Callable[[], Any]


def add_initial_data(session: Session) -> None:
    if session.query(Film).count() == 0:
        session.bulk_save_objects(
            [
                Film(name='Lord of the Rings', year=1999),
                Film(name='Harry Potter', year=2003),
                Film(name='Harry Potter 2', year=2005),
                Film(name='The Matrix', year=1999),
            ]
        )


def init_db() -> None:  # pragma: no cover
    global engine, SessionLocal  # pylint: disable=global-statement
    engine = create_engine('sqlite:///filmash.db')
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    with create_session() as session:
        add_initial_data(session)


@contextmanager
def create_session() -> Iterator[Any]:  # pragma: no cover
    new_session = SessionLocal()
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


def get_session() -> Any:
    with create_session() as s:
        yield s
