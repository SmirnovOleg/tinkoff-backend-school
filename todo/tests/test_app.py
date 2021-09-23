from todo_list.app import app


def test_redirect_to_active_items(client):
    resp = client.get('/', follow_redirects=True)
    assert b'Review new article' in resp.data
    assert b'Reply to customers' in resp.data


def test_finished_items(client):
    resp = client.get('/finished', follow_redirects=True)
    # There is no finished tasks or pages at the beginning
    assert b'<li class="list-group-item">' not in resp.data


def test_adding_new_item(client):
    resp = client.post(
        '/active/1', data=dict(new_item_desc='New test task'), follow_redirects=True
    )
    assert b'New test task' in resp.data
    assert b'Review new article' in resp.data
    assert b'Reply to customers' in resp.data


def test_adding_invalid_empty_item(client):
    resp = client.post('/active/1', data=dict(new_item_desc=''), follow_redirects=True)
    assert resp.status_code == 400
    assert b'task description should not be empty' in resp.data


def test_finishing_item_from_active(client):
    item_id_to_finish = app.todo_list.get_active_items()[1].id
    resp = client.post(
        '/active/1', data=dict(finish_item_id=item_id_to_finish), follow_redirects=True
    )
    assert b'Review new article' in resp.data
    assert b'Reply to customers' not in resp.data
    resp = client.get('/finished/1', follow_redirects=True)
    assert b'<strike>Reply to customers</strike>' in resp.data


def test_finishing_item_from_all(client):
    item_id_to_finish = app.todo_list.get_all_items()[1].id
    resp = client.post(
        '/all/1', data=dict(finish_item_id=item_id_to_finish), follow_redirects=True
    )
    assert b'Review new article' in resp.data
    assert b'<strike>Reply to customers</strike>' in resp.data


def test_finishing_item_from_all_by_invalid_id(client):
    item_id_to_finish = 'abc'
    resp = client.post(
        '/all/1', data=dict(finish_item_id=item_id_to_finish), follow_redirects=True
    )
    assert resp.status_code == 400
    assert b'ID of the finished task must be numeric' in resp.data


def test_finishing_item_from_active_by_invalid_id(client):
    item_id_to_finish = '-1'
    resp = client.post(
        '/active/1', data=dict(finish_item_id=item_id_to_finish), follow_redirects=True
    )
    assert resp.status_code == 400
    assert b'ID of the finished task must be numeric' in resp.data


def test_getting_all_items_after_finishing_item(client):
    item_id_to_finish = app.todo_list.get_all_items()[1].id
    client.post(
        '/active/1', data=dict(finish_item_id=item_id_to_finish), follow_redirects=True
    )
    resp = client.get('/all', follow_redirects=True)
    assert b'Review new article' in resp.data
    assert b'<strike>Reply to customers</strike>' in resp.data


def test_search_for_substring(client):
    resp = client.get('/all/1?filter=article', follow_redirects=True)
    assert b'Review new article' in resp.data
    assert b'Reply to customers' not in resp.data


def test_search_for_substring_ignore_case(client):
    client.post(
        '/all/1', data=dict(new_item_desc='New test task'), follow_redirects=True
    )
    resp = client.get('/all/1?filter=re', follow_redirects=True)
    assert b'Review new article' in resp.data
    assert b'Reply to customers' in resp.data
    assert b'New test task' not in resp.data


def test_pagination(client):
    """Check if page №2 appears in case we want to add more than 10 new items."""
    for i in range(10):
        client.post(
            '/active/1',
            data=dict(new_item_desc=f'New test task #{i}'),
            follow_redirects=True,
        )
    resp = client.get('/active/2', follow_redirects=True)
    assert b'Review new article' in resp.data
    assert b'Reply to customers' in resp.data
