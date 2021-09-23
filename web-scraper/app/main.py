import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterator, Optional

import typer
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from app.config import HABR_ARTICLES_DIR, HABR_URL, ParsedArticleData, Url
from app.utils import download_and_save_file, download_html, write_text_to_file
from app.validators import check_directory, check_if_positive


def parse_habr_article(habr_article_url: Url) -> Optional[ParsedArticleData]:
    logging.info('Downloading article...')

    html = download_html(habr_article_url)
    if not html:
        return None

    logging.info('Parsing data...')

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('span', class_='post__title-text').get_text()
    body = soup.find('div', class_='post__body post__body_full')
    text = body.get_text(strip=True)
    images_urls = [
        item.get('src') for item in body.find_all('img') if item.get('src') is not None
    ]

    logging.info('Finished extracting data from article: %s', habr_article_url)

    return ParsedArticleData(sanitize_filename(title), text, images_urls)


def get_habr_articles_urls(articles_num: int) -> Iterator[Url]:
    current_page = 1
    logging.info('Started retrieving articles urls')

    while articles_num > 0:
        html = download_html(url=f'{HABR_URL}/page{current_page}')
        if not html:
            break
        soup = BeautifulSoup(html, 'html.parser')
        for element in soup.find_all('a', class_='post__title_link')[:articles_num]:
            yield element.get('href')
            articles_num -= 1
        current_page += 1

    logging.info("Finished retrieving articles' urls")


def process_articles(
    threads: int = typer.Option(
        multiprocessing.cpu_count(), callback=check_if_positive
    ),
    articles: int = typer.Option(1, callback=check_if_positive),
    save_dir: Path = typer.Option(HABR_ARTICLES_DIR, callback=check_directory),
) -> None:
    logging.info('Started scraping...')

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for url in get_habr_articles_urls(articles):
            futures.append(executor.submit(parse_habr_article, habr_article_url=url))

        for future in as_completed(futures):
            parsed_data = future.result()
            if not parsed_data:
                continue
            article_dir = save_dir / parsed_data.sanitized_title
            article_dir.mkdir(parents=True, exist_ok=True)

            logging.info('Saving images...')

            for image_num, image_url in enumerate(parsed_data.images_urls):
                extension = image_url.split('.')[-1]
                image_file = article_dir / f'image{image_num}.{extension}'
                executor.submit(download_and_save_file, url=image_url, file=image_file)

            logging.info('Saving text...')

            text_file = article_dir / 'article.txt'
            executor.submit(
                write_text_to_file, file=text_file, text=parsed_data.article_text
            )

            logging.info(
                'Finished processing article <<%s>>', parsed_data.sanitized_title
            )

    logging.info('Done.')


def main() -> None:  # pragma: no cover
    logging.basicConfig(
        filename='scraper.log',
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S',
    )
    typer.run(process_articles)


if __name__ == '__main__':
    main()
