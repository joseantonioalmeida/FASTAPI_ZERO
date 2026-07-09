from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


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
            'username': f'{user.username}',
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


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_detail_user(client, user, token):
    response = client.get(
        f'/users/{user.id}/', headers={'Authorization': f'Bearer {token}'}
    )

    # Usuário Encontrado

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': f'{user.username}',
        'email': f'{user.email}',
        'id': int(f'{user.id}'),
    }

    # user_id diferente do current_user.id
    response = client.get(
        '/users/666/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}/',
        json={
            'username': 'jose_put',
            'email': 'jose_put@gmail.com',
            'password': 'jose_put321',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    # Usuário Encontrado
    assert response.json() == {
        'username': 'jose_put',
        'email': 'jose_put@gmail.com',
        'id': 1,
    }

    response = client.put(
        '/users/666/',
        json={
            'username': 'jose_put',
            'email': 'jose_put@gmail.com',
            'password': 'jose_put321',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    # Usuário não encontrado
    assert response.json() == {'detail': 'Could not validate credentials'}
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_update_current_user_id_diferrent_user_id(client, outher_user, token):

    response = client.put(
        f'/users/{outher_user.id}',
        json={
            'username': f'{outher_user.username}',
            'email': f'{outher_user.email}',
            'password': f'{outher_user.clean_password}',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_integrity_error(client, user, outher_user, token):

    # Alterando o user das fixtures para fausto
    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': f'{outher_user.username}',
            'email': f'{outher_user.email}',
            'password': f'{outher_user.clean_password}',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}/', headers={'Authorization': f'Bearer {token}'}
    )

    # Usuário Encontrado
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}

    response = client.delete(
        '/users/666/', headers={'Authorization': f'Bearer {token}'}
    )

    # Usuário não encontrado
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_delete_current_user_diferent_user_id(client, outher_user, token):
    # Deletando um user onde o user_id é diferente do current_user.id
    response = client.delete(
        f'/users/{outher_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == {'detail': 'Not enough permissions'}
