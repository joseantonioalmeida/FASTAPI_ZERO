from http import HTTPStatus

import factory.fuzzy
import pytest

from fastapi_zero.models import Todo, TodoState
from fastapi_zero.routers.todos import create_todo, read_todos
from fastapi_zero.schemas import (  # noqa: F811
    FilterTodo,
    TodoSchema,
    TodoState,
)


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token):
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


@pytest.mark.asyncio
async def test_read_todos(client, user, session, token):
    # arrange
    expected_todos = 5
    todos = TodoFactory.create_batch(expected_todos, user_id=user.id)
    session.add_all(todos)
    await session.commit()

    # act
    response = client.get(  # sem query
        '/todos/', headers={'Authorization': f'Bearer {token}'}
    )

    # assert
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_read_todos_should_return_paginated_and_filtered(
    session, user, client, token
):
    expected_todos = 2
    todos = TodoFactory.create_batch(
        5,
        user_id=user.id,
        title='FastAPI',
        state='doing',
        description='FastAPI',
    )
    session.add_all(todos)
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2&title=FastAPI&description=FastAPI&state=doing',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['todos']) == expected_todos
    assert response.json()['todos'][0]['title'] == 'FastAPI'
    assert response.json()['todos'][0]['description'] == 'FastAPI'
    assert response.json()['todos'][0]['state'] == 'doing'


@pytest.mark.asyncio
async def test_read_todos_should_return_empty_list_dict_when_no_records_match(
    user, session
):
    todo_public = FilterTodo(
        title='FastAPI',
        state=TodoState.doing,
        description='FastAPI',
    )

    read = await read_todos(user, session, todo_public)

    assert read == {'todos': []}
