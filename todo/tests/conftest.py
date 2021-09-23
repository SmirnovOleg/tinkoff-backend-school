import pytest

from todo_list.app import app
from todo_list.models import TodoItem, TodoList


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        app.todo_list = TodoList(
            [
                TodoItem(description='Reply to customers'),
                TodoItem(description='Review new article'),
            ]
        )
        yield test_client
