import os
from pathlib import Path
from typing import List, NamedTuple, Union

HABR_URL = os.environ.get('HABR_URL', 'https://habr.com/ru')
HABR_ARTICLES_DIR = Path(os.environ.get('HABR_ARTICLES_DIR', 'articles'))

CONNECTION_TIMEOUT = 15
MAX_RETRIES = 3

Url = str


class ParsedArticleData(NamedTuple):
    sanitized_title: Union[str, Path]
    article_text: str
    images_urls: List[Url]
