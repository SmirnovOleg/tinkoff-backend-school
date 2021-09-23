import pytest


@pytest.mark.usefixtures('reviews')
def test_filtering_films_by_substring(client, credentials):
    resp = client.get(
        url='/films?substring=Harry',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data == {
        'films': [
            {
                'film_id': 2,
                'film_name': 'Harry Potter',
                'year': 2003,
                'avg_score': 3,
            },
            {
                'film_id': 3,
                'film_name': 'Harry Potter 2',
                'year': 2005,
                'avg_score': 6,
            },
        ],
        'page': 1,
        'total_pages': 1,
    }


@pytest.mark.usefixtures('reviews')
def test_filtering_films_by_year(client, credentials):
    resp = client.get(
        url='/films?year=1999',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data == {
        'films': [
            {
                'film_id': 1,
                'film_name': 'Lord of the Rings',
                'year': 1999,
                'avg_score': 10,
            },
            {
                'film_id': 4,
                'film_name': 'The Matrix',
                'year': 1999,
                'avg_score': 1,
            },
        ],
        'page': 1,
        'total_pages': 1,
    }


@pytest.mark.usefixtures('reviews')
def test_sorting_films_descending(client, credentials):
    resp = client.get(
        url='/films?sort_by_avg_score=desc',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data == {
        'films': [
            {
                'film_id': 1,
                'film_name': 'Lord of the Rings',
                'year': 1999,
                'avg_score': 10,
            },
            {
                'film_id': 5,
                'film_name': 'Inception',
                'year': 2010,
                'avg_score': 7.25,
            },
            {
                'film_id': 3,
                'film_name': 'Harry Potter 2',
                'year': 2005,
                'avg_score': 6,
            },
            {
                'film_id': 2,
                'film_name': 'Harry Potter',
                'year': 2003,
                'avg_score': 3,
            },
            {
                'film_id': 4,
                'film_name': 'The Matrix',
                'year': 1999,
                'avg_score': 1,
            },
        ],
        'page': 1,
        'total_pages': 1,
    }


@pytest.mark.usefixtures('reviews')
def test_top_films(client, credentials):
    resp = client.get(
        url='/films?sort_by_avg_score=asc&top=2',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data == {
        'films': [
            {
                'film_id': 4,
                'film_name': 'The Matrix',
                'year': 1999,
                'avg_score': 1,
            },
            {
                'film_id': 2,
                'film_name': 'Harry Potter',
                'year': 2003,
                'avg_score': 3,
            },
        ],
        'page': 1,
        'total_pages': 1,
    }


@pytest.mark.usefixtures('reviews', 'page_size_1')
def test_complex_filter_for_films_page_one(client, credentials):
    resp = client.get(
        url='/films?substring=o&sort_by_avg_score=desc&top=2&page=1',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data == {
        'films': [
            {
                'film_id': 1,
                'film_name': 'Lord of the Rings',
                'year': 1999,
                'avg_score': 10,
            }
        ],
        'page': 1,
        'total_pages': 2,
    }


@pytest.mark.usefixtures('reviews', 'page_size_1')
def test_complex_filter_for_films_page_two(client, credentials):
    resp = client.get(
        url='/films?substring=o&sort_by_avg_score=desc&top=2&page=2',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data == {
        'films': [
            {
                'film_id': 5,
                'film_name': 'Inception',
                'year': 2010,
                'avg_score': 7.25,
            }
        ],
        'page': 2,
        'total_pages': 2,
    }


def test_getting_film_info(client, film, credentials):
    resp = client.get(
        url=f'/films/{film.id}',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_id'] == film.id
    assert data['film_name'] == film.name
    assert data['avg_score'] == film.avg_score
    assert data['total_scores'] == film.total_scores
    assert data['total_comments'] == film.total_comments
