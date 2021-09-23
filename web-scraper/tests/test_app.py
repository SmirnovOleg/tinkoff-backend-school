import os
from pathlib import Path

import pytest
import requests

from app.config import ParsedArticleData
from app.main import get_habr_articles_urls, parse_habr_article
from app.utils import download_and_save_file, write_text_to_file


def test_invalid_threads_arg(test_app, runner):
    result = runner.invoke(test_app, ['--threads', '0'])
    assert result.exit_code == 2
    assert "Error: Invalid value for '--threads': must be positive" in result.stdout


def test_invalid_articles_arg(test_app, runner):
    result = runner.invoke(test_app, ['--articles', '-100'])
    assert result.exit_code == 2
    assert "Error: Invalid value for '--articles': must be positive" in result.stdout


def test_not_empty_save_dir_arg(test_app, runner):
    result = runner.invoke(test_app, ['--save-dir', os.path.dirname(__file__)])
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '--save-dir': specified directory is not empty"
        in result.stdout
    )


def test_if_save_dir_arg_is_not_a_dir(test_app, runner):
    result = runner.invoke(test_app, ['--save-dir', os.path.abspath(__file__)])
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '--save-dir': specified path is not a directory"
        in result.stdout
    )


def test_writing_text_to_file(tmp_path):
    path_to_test_file = tmp_path / 'article.txt'
    write_text_to_file(path_to_test_file, 'Some text')

    assert path_to_test_file.exists()
    with open(path_to_test_file, 'r') as file:
        assert file.read() == 'Some text'


def test_write_image(requests_mock, tmp_path, sony_image, tmp_image_url):
    requests_mock.get(tmp_image_url, content=sony_image)

    path_to_test_file = tmp_path / 'image.jpeg'
    download_and_save_file(tmp_image_url, path_to_test_file)

    with open(path_to_test_file, 'rb') as file:
        assert file.read() == sony_image


def test_extracting_data_from_article(
    requests_mock, sony_article_url, sony_article_html
):
    requests_mock.get(sony_article_url, text=sony_article_html)

    data = parse_habr_article(sony_article_url)
    assert data
    sanitized_title, text, links = data

    assert (
        sanitized_title
        == 'It`s a Sony! Впечатления от ультрапортативного флагмана 20 лет спустя'
    )
    assert text == 'Не уверен, что это ещё актуально, но ниже около 25-ти картинок.'
    assert len(links) == 2 and links[0] == links[1]


def test_timeout_for_parsing_habr_article(requests_mock, sony_article_url):
    requests_mock.register_uri(
        'GET', sony_article_url, exc=requests.exceptions.ConnectTimeout
    )
    assert not parse_habr_article(sony_article_url)


def test_timeout_for_downloading_file(requests_mock, tmp_image_url, tmp_path):
    requests_mock.register_uri(
        'GET', tmp_image_url, exc=requests.exceptions.ConnectTimeout
    )
    download_and_save_file(tmp_image_url, tmp_path / 'image.png')
    assert not (tmp_path / 'image.png').exists()


def test_extracting_data_from_article_from_incorrect_url(incorrect_url):
    assert not parse_habr_article(incorrect_url)


def test_get_all_article_list(requests_mock, articles_list_url, articles_list_html):
    requests_mock.get(articles_list_url, text=articles_list_html)

    urls = list(get_habr_articles_urls(2))

    assert urls == ['article', 'another-article']


@pytest.mark.usefixtures('clear')
def test_process_articles(mocker, test_app, runner, sony_article_url, tmp_image_url):
    mocker.patch('app.main.get_habr_articles_urls', return_value=[sony_article_url])
    mocker.patch(
        'app.main.parse_habr_article',
        return_value=ParsedArticleData('Title', 'Text', [tmp_image_url]),
    )

    result = runner.invoke(test_app, ['--threads', '4', '--articles', '1'])
    path_to_articles = Path('articles')
    path_to_article = path_to_articles / 'Title'

    assert result.exit_code == 0
    assert path_to_articles.exists() and path_to_articles.is_dir()
    assert path_to_article.exists() and path_to_article
    assert 'article.txt' in os.listdir(path_to_article)
    assert 'image0.png' in os.listdir(path_to_article)
