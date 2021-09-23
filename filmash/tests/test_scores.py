import pytest


@pytest.mark.usefixtures('user')
def test_posting_score(client, credentials, film):
    resp = client.post(
        url=f'/films/{film.id}/scores',
        headers={'Authorization': f'Basic {credentials}'},
        json={'score': 10},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['posted_score'] == 10
    assert data['avg_score'] == 10
    assert data['total_scores'] == 1


@pytest.mark.usefixtures('user')
def test_posting_many_scores(client, credentials, film):
    client.post(
        url=f'/films/{film.id}/scores',
        headers={'Authorization': f'Basic {credentials}'},
        json={'score': 10},
    )
    resp = client.post(
        url=f'/films/{film.id}/scores',
        headers={'Authorization': f'Basic {credentials}'},
        json={'score': 0},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['posted_score'] == 0
    assert data['avg_score'] == 0
    assert data['total_scores'] == 1


@pytest.mark.usefixtures('user')
def test_posting_invalid_score(client, credentials, film):
    resp = client.post(
        url=f'/films/{film.id}/scores',
        headers={'Authorization': f'Basic {credentials}'},
        json={'score': 11},
    )
    data = resp.json()

    assert resp.status_code == 422
    assert data['detail'] == [
        {
            'loc': ['body', 'score'],
            'msg': 'must be between 0 and 10',
            'type': 'value_error',
        }
    ]


@pytest.mark.usefixtures('user')
def test_posting_score_from_unauthenticated_user(client, film):
    resp = client.post(
        url=f'/films/{film.id}/scores',
        json={'score': 10},
    )

    assert resp.status_code == 401
    assert resp.json()['detail'] == 'Not authenticated'


@pytest.mark.usefixtures('user')
def test_posting_score_from_incorrect_login(client, film):
    resp = client.post(
        url=f'/films/{film.id}/scores',
        headers={'Authorization': 'Basic b2xlZzoxMjM0NQ=='},
        json={'score': 10},
    )

    assert resp.status_code == 401
    assert resp.json()['detail'] == 'Incorrect login or password'


@pytest.mark.usefixtures('user')
def test_posting_score_from_invalid_credentials(client, film):
    resp = client.post(
        url=f'/films/{film.id}/scores',
        headers={'Authorization': 'Basic abc=='},
        json={'score': 10},
    )

    assert resp.status_code == 401
    assert resp.json()['detail'] == 'Invalid authentication credentials'


def test_getting_all_scores_by_film(client, film, credentials, reviews):
    resp = client.get(
        url=f'/films/{film.id}/scores',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['avg_score'] == 7.25
    assert data['total_scores'] == 4
    assert data['scores'] == [
        {'user_id': reviews[0].user_id, 'score': reviews[0].score},
        {'user_id': reviews[1].user_id, 'score': reviews[1].score},
        {'user_id': reviews[2].user_id, 'score': reviews[2].score},
        {'user_id': reviews[4].user_id, 'score': reviews[4].score},
    ]
    assert data['page'] == 1
    assert data['total_pages'] == 1


@pytest.mark.usefixtures('page_size_3')
def test_getting_scores_by_film_page_one(client, film, credentials, reviews):
    resp = client.get(
        url=f'/films/{film.id}/scores?page=1',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['avg_score'] == 7.25
    assert data['total_scores'] == 4
    assert data['scores'] == [
        {'user_id': reviews[0].user_id, 'score': reviews[0].score},
        {'user_id': reviews[1].user_id, 'score': reviews[1].score},
        {'user_id': reviews[2].user_id, 'score': reviews[2].score},
    ]
    assert data['page'] == 1
    assert data['total_pages'] == 2


@pytest.mark.usefixtures('page_size_3')
def test_getting_scores_by_film_page_two(client, film, credentials, reviews):
    resp = client.get(
        url=f'/films/{film.id}/scores?page=2',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 200
    assert data['film_name'] == film.name
    assert data['avg_score'] == 7.25
    assert data['total_scores'] == 4
    assert data['scores'] == [
        {'user_id': reviews[4].user_id, 'score': reviews[4].score}
    ]
    assert data['page'] == 2
    assert data['total_pages'] == 2


def test_getting_scores_by_nonexistent_film(client, credentials):
    resp = client.get(
        url='/films/1000/scores',
        headers={'Authorization': f'Basic {credentials}'},
    )
    data = resp.json()

    assert resp.status_code == 404
    assert data['detail'] == 'Film with specified id = 1000 does not exist'


def test_posting_score_for_nonexistent_film(client, credentials):
    resp = client.post(
        url='/films/1000/scores',
        headers={'Authorization': f'Basic {credentials}'},
        json={'score': 10},
    )
    data = resp.json()

    assert resp.status_code == 404
    assert data['detail'] == 'Film with specified id = 1000 does not exist'
