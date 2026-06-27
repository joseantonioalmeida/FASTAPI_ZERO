from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_root_deve_retornar_ola_mundo(client):
    """A)
    - A: Arrange - Arranjo
    Esse teste tem 3 etapas(AA
    - A: Act     - Executa a coisa(o SUT)
    - A: Assert  - Garanta que A é A
    """

    # Act
    response = client.get('/')

    # Assert
    assert response.json() == {'message': 'Olá, Mundo!'}
    assert response.status_code == HTTPStatus.OK


def test_create_user(client):
    user = {'username': 'joseteste', 'email': 'joseteste@gmail.com', 'id': 1}

    response = client.post(
        '/users/',
        json={
            'username': 'joseteste',
            'email': 'joseteste@gmail.com',
            'password': 'jose321',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == user


def test_read_users(
    client,
):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_detail_user(client):
    response = client.get('/users/1/')

    # Usuário Encontrado
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'joseteste',
        'email': 'joseteste@gmail.com',
        'id': 1,
    }

    response = client.get('/users/666/')

    # Usuário não encontrado
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_update_user(client):
    response = client.put(
        '/users/1/',
        json={
            'username': 'jose_put',
            'email': 'jose_put@gmail.com',
            'password': 'jose_put321',
        },
    )

    # Usuário Encontrado
    assert response.json() == {
        'username': 'jose_put',
        'email': 'jose_put@gmail.com',
        'id': 1,
    }

    response = client.put(
        '/users/2/',
        json={
            'username': 'jose_put',
            'email': 'jose_put@gmail.com',
            'password': 'jose_put321',
        },
    )

    # Usuário não encontrado
    assert response.json() == {'detail': 'User Not Found'}


def test_delete_user(client):
    response = client.delete('/users/1/')

    # Usuário Encontrado
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'jose_put',
        'email': 'jose_put@gmail.com',
        'id': 1,
    }

    response = client.delete('/users/999/')

    # Usuário não encontrado
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}
    assert response.text == '{"detail":"User Not Found"}'
