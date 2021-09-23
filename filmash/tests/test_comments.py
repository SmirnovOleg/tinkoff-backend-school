import pytest


@pytest.mark.usefixtures('user')
def test_posting_comment(client, credentials, film):
    resp = client.post(
        url=f'/films/{film.id}/comments',
        headers={'Authorization': f'Basic {credentials}'},
        json={'comment': "Very cool! I've really liked it!"},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['posted_comment'] == "Very cool! I've really liked it!"
    assert data['total_comments'] == 1


@pytest.mark.usefixtures('user')
def test_posting_many_comments(client, credentials, film):
    client.post(
        url=f'/films/{film.id}/comments',
        headers={'Authorization': f'Basic {credentials}'},
        json={'comment': "Very cool! I've really liked it!"},
    )
    resp = client.post(
        url=f'/films/{film.id}/comments',
        headers={'Authorization': f'Basic {credentials}'},
        json={'comment': 'So cool!'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['posted_comment'] == 'So cool!'
    assert data['total_comments'] == 1


@pytest.mark.usefixtures('user')
def test_posting_empty_comment(client, credentials, film):
    resp = client.post(
        url=f'/films/{film.id}/comments',
        headers={'Authorization': f'Basic {credentials}'},
        json={'comment': ''},
    )

    assert resp.status_code == 422
    assert resp.json()['detail'] == [
        {'loc': ['body', 'comment'], 'msg': 'can not be empty', 'type': 'value_error'}
    ]


def test_getting_all_comments_by_film(client, film, credentials, reviews):
    resp = client.get(
        url=f'/films/{film.id}/comments',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['comments'] == [
        {'user_id': reviews[3].user_id, 'comment': reviews[3].comment},
        {'user_id': reviews[4].user_id, 'comment': reviews[4].comment},
        {'user_id': reviews[5].user_id, 'comment': reviews[5].comment},
    ]
    assert data['page'] == 1
    assert data['total_pages'] == 1


@pytest.mark.usefixtures('page_size_2')
def test_getting_comments_by_film_page_one(client, film, credentials, reviews):
    resp = client.get(
        url=f'/films/{film.id}/comments?page=1',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['comments'] == [
        {'user_id': reviews[3].user_id, 'comment': reviews[3].comment},
        {'user_id': reviews[4].user_id, 'comment': reviews[4].comment},
    ]
    assert data['page'] == 1
    assert data['total_pages'] == 2


@pytest.mark.usefixtures('page_size_2')
def test_getting_comments_by_film_page_two(client, film, credentials, reviews):
    resp = client.get(
        url=f'/films/{film.id}/comments?page=2',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['comments'] == [
        {'user_id': reviews[5].user_id, 'comment': reviews[5].comment}
    ]
    assert data['page'] == 2
    assert data['total_pages'] == 2


def test_getting_comments_by_nonexistent_film(client, credentials):
    resp = client.get(
        url='/films/1000/comments',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 404
    assert data['detail'] == 'Film with specified id = 1000 does not exist'


def test_posting_comment_for_nonexistent_film(client, credentials):
    resp = client.post(
        url='/films/1000/comments',
        headers={'Authorization': f'Basic {credentials}'},
        json={'comment': 'Haha'},
    )
    data = resp.json()

    assert resp.status_code == 404
    assert data['detail'] == 'Film with specified id = 1000 does not exist'
