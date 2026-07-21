from http import HTTPStatus

import factory.fuzzy
import pytest
from fastapi import HTTPException

from fastapi_zero.models import Todo, TodoState
from fastapi_zero.routers.todos import (
    create_todo,
    delete_todo,
    patch_todo,
    read_todos,
)
from fastapi_zero.schemas import (  # noqa: F811
    FilterTodo,
    TodoSchema,
    TodoState,
    TodoUpdate,
)


class TodoFactory(factory.Factory):  # type:ignore
    class Meta:
        model = Todo

    title = factory.Faker('text')  # type:ignore
    description = factory.Faker('text')  # type:ignore
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

    todo_create = response.json()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == todo_create


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


@pytest.mark.asyncio
async def test_delete_todo_should_message_deleted(
    client, user, token, session
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }

    # handler direct
    create_td = await create_todo(todo, user, session)
    return_delete = await delete_todo(create_td.id, user, session)

    assert return_delete == {'message': 'Task has been deleted successfully.'}


@pytest.mark.asyncio
async def test_delete_todo_should_return_task_not_found(
    client, token, user, session
):
    response = client.delete(
        '/todos/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}

    # handler direct
    with pytest.raises(HTTPException) as exc_info:
        await delete_todo(2, user, session)

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == 'Task not found.'


@pytest.mark.asyncio
async def test_delete_other_user_todo(client, other_user, token, session):
    other_user_todo = TodoFactory(user_id=other_user.id)
    session.add(other_user_todo)
    await session.commit()

    response = client.delete(
        f'/todos/{other_user_todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_patch_todo(client, token, user, session):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'Teste do patch'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'Teste do patch'

    # handler direct
    todo_update = TodoUpdate(title='Teste do patch')
    created_todo = await create_todo(todo, user, session)
    todo_patch = await patch_todo(created_todo.id, user, session, todo_update)

    assert todo_patch.title == 'Teste do patch'


@pytest.mark.asyncio
async def test_patch_todo_error(
    client,
    token,
    user,
    session,
):
    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}

    # handler direct
    with pytest.raises(HTTPException) as exc_info:
        await patch_todo(10, user, session, todo={})  # type: ignore

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND
    assert exc_info.value.detail == 'Task not found.'
