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


def test_create_user(client, user):
    user_ = {'username': 'joseteste', 'email': 'joseteste@gmail.com', 'id': 2}

    response = client.post(
        '/users/',
        json={
            'username': 'joseteste',
            'email': 'joseteste@gmail.com',
            'password': 'jose321',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == user_

    # Se um usuário já estiver criado e colocar um username igual
    response = client.post(
        '/users/',
        json={
            'username': 'Test',
            'email': 'blabla@gmail.com',
            'password': 'blabla',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}

    # Se um usuário já estiver criado e colocar um email igual
    response = client.post(
        '/users/',
        json={
            'username': 'BlaBla',
            'email': 'joseteste@gmail.com',
            'password': 'blabla',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


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


def test_detail_user(client, user):
    response = client.get('/users/1/')

    # Usuário Encontrado

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Test',
        'email': 'teste@gmail.com',
        'id': 1,
    }

    response = client.get('/users/666/')

    # Usuário não encontrado
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_update_user(client, user):
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


def test_update_integrity_error(client, user):
    # Inserindo Fausto
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    # Alterando o user das fixtures para fausto
    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_delete_user(client, user):
    response = client.delete('/users/1/')

    # Usuário Encontrado
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}

    response = client.delete('/users/999/')

    # Usuário não encontrado
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_login_for_acess_token(client, user):
    response = client.post(
        '/token/',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'acess_token' in token
