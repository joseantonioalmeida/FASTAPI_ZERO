from http import HTTPStatus

import pytest

from fastapi_zero.models import TodoState
from fastapi_zero.routers.todos import create_todo
from fastapi_zero.schemas import TodoSchema


@pytest.mark.asyncio
async def test_create_todo(client, token, session):
    response = client.post(
        '/todos/',
        json={
            'title': 'title teste',
            'description': 'description teste',
            'state': TodoState.todo,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'title': 'title teste',
        'description': 'description teste',
        'state': 'todo',
        'id': 1,
    }


@pytest.mark.asyncio
async def test_create_todo_handler_direct(user, session):
    todo_data = TodoSchema(
        title='title teste',
        description='description teste',
        state=TodoState.todo,
    )

    created_todo = await create_todo(todo_data, user, session)

    assert created_todo.id == 1
    assert created_todo.user_id == user.id
    assert created_todo.title == 'title teste'
    assert created_todo.state == TodoState.todo
