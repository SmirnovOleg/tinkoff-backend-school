import logging
from pathlib import Path
from typing import Optional

import requests
from requests import RequestException, Response

from app.config import CONNECTION_TIMEOUT, MAX_RETRIES, Url


def send_get_request_with_binary_lifting_timeouts(url: Url) -> Optional[Response]:
    current_timeout = CONNECTION_TIMEOUT
    resp = None
    for _ in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=current_timeout)
        except requests.exceptions.Timeout:
            current_timeout *= 2
        except RequestException as e:  # pragma: no cover
            logging.error(e)
            break
        else:
            break

    return resp


def download_html(url: Url) -> Optional[str]:
    resp = send_get_request_with_binary_lifting_timeouts(url)
    if not resp:
        logging.error('Request has failed.')
        return None
    if resp.status_code != 200:
        logging.error('Response status code: %s', resp.status_code)
        logging.error('Message: %s', resp.text)
        return None

    return resp.text


def download_and_save_file(url: Url, file: Path) -> None:
    resp = send_get_request_with_binary_lifting_timeouts(url)
    if not resp:
        logging.error('Request has failed.')
        return
    if resp.status_code != 200:
        logging.error('Failed to download image from %s', url)
        return
    with file.open('wb') as f:
        f.write(resp.content)


def write_text_to_file(file: Path, text: str) -> None:
    with file.open('w', encoding='utf-8') as f:
        f.write(text)
