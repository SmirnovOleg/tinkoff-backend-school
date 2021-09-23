# pylint: disable=redefined-outer-name

import base64
from contextlib import contextmanager
from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.utils as utils_module
from app.db.models import Film, Review, User
from app.db.utils import add_initial_data, get_session
from app.main import app

test_engine = create_engine('sqlite:///test.db')
TestingSessionLocal = sessionmaker(bind=test_engine)


@pytest.fixture(autouse=True)
def create_test_database():
    import app.db.models as models  # pylint: disable=import-outside-toplevel

    app.dependency_overrides[get_session] = get_test_session
    models.Base.metadata.create_all(test_engine)
    with create_test_session() as s:
        add_initial_data(session=s)
    yield
    models.Base.metadata.drop_all(test_engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def session():
    with create_test_session() as s:
        yield s


@contextmanager
def create_test_session() -> Iterator[Any]:
    new_session = TestingSessionLocal()
    try:
        yield new_session
        new_session.commit()
    except Exception:
        new_session.rollback()
        raise
    finally:
        new_session.close()


def get_test_session():
    with create_test_session() as s:
        yield s


@pytest.fixture
def password():
    return '12345'


@pytest.fixture
def user(session, password):
    user = User(
        login='user', hashed_password=utils_module.get_hashed_password(password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def credentials(user, password):
    return base64.b64encode(f'{user.login}:{password}'.encode()).decode()


@pytest.fixture
def six_users(session, password):
    users = []
    for i in range(6):
        users.append(User(login=f'user_{i}', hashed_password=password))
        session.add(users[-1])
        session.commit()
        session.refresh(users[-1])
    return users


@pytest.fixture
def film(session):
    film = Film(name='Inception', year=2010)
    session.add(film)
    session.commit()
    session.refresh(film)
    return film


@pytest.fixture
def reviews(user, six_users, film, session):
    reviews = [
        Review(user_id=six_users[0].id, film_id=film.id, score=10),
        Review(user_id=six_users[1].id, film_id=film.id, score=8),
        Review(user_id=six_users[2].id, film_id=film.id, score=9),
        Review(user_id=six_users[3].id, film_id=film.id, comment='Nice!'),
        Review(user_id=six_users[4].id, film_id=film.id, comment='Bad..', score=2),
        Review(user_id=six_users[5].id, film_id=film.id, comment='Old but gold.'),
        Review(user_id=user.id, film_id=1, score=10),
        Review(user_id=user.id, film_id=2, score=3),
        Review(user_id=user.id, film_id=3, score=6),
        Review(user_id=user.id, film_id=4, score=1),
    ]
    session.bulk_save_objects(reviews)

    film.avg_score = 7.25
    film.total_scores = 4
    film.total_comments = 3

    session.query(Film).get(1).avg_score = 10
    session.query(Film).get(1).total_scores = 1

    session.query(Film).get(2).avg_score = 3
    session.query(Film).get(2).total_scores = 1

    session.query(Film).get(3).avg_score = 6
    session.query(Film).get(3).total_scores = 1

    session.query(Film).get(4).avg_score = 1
    session.query(Film).get(4).total_scores = 1

    session.commit()
    return reviews


@pytest.fixture
def page_size_1():
    app.dependency_overrides[utils_module.get_page_size] = lambda: 1
    yield
    app.dependency_overrides[utils_module.get_page_size] = utils_module.get_page_size


@pytest.fixture
def page_size_2():
    app.dependency_overrides[utils_module.get_page_size] = lambda: 2
    yield
    app.dependency_overrides[utils_module.get_page_size] = utils_module.get_page_size


@pytest.fixture
def page_size_3():
    app.dependency_overrides[utils_module.get_page_size] = lambda: 3
    yield
    app.dependency_overrides[utils_module.get_page_size] = utils_module.get_page_size
