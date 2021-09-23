# pylint: disable=redefined-outer-name

import pathlib
from shutil import rmtree

import pytest
from typer import Typer
from typer.testing import CliRunner

from app.config import HABR_URL
from app.main import process_articles

resources_path = pathlib.Path(__file__).parent.absolute() / 'resources'


@pytest.fixture()
def test_app():
    app = Typer()
    app.command()(process_articles)
    return app


@pytest.fixture()
def runner():
    runner = CliRunner()
    return runner


@pytest.fixture()
def articles_page_1():
    return f'{HABR_URL}/page1'


@pytest.fixture(scope='session')
def sony_article_html():
    with open(resources_path / 'sony_article.html') as f:
        data = f.read()
    return data


@pytest.fixture(scope='session')
def articles_list_html():
    with open(resources_path / 'articles_list.html') as f:
        data = f.read()
    return data


@pytest.fixture(scope='session')
def sony_image():
    with open(resources_path / 'sony_image.jpeg', 'rb') as f:
        data = f.read()
    return data


@pytest.fixture()
def sony_article_url():
    return 'https://habr.com/ru/post/549630/'


@pytest.fixture()
def articles_list_url():
    return 'https://habr.com/ru/page1'


@pytest.fixture()
def tmp_image_url():
    return 'https://habrastorage.org/webt/el/sm/tb/elsmtbmqisdj5xya58maazawiwu.png'


@pytest.fixture()
def incorrect_url():
    return 'https://habr.com/ru/artcls/'


@pytest.fixture()
def clear():
    yield
    rmtree('articles')
