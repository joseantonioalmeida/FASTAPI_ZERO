import json
from http import HTTPStatus


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


def test_read_users(client):
    response = client.get('/users/')

    EXPECTED_USERS_COUNT = 1

    assert response.status_code == HTTPStatus.OK
    assert (
        len(json.loads(response.content.decode('utf-8'))['users'])
        == EXPECTED_USERS_COUNT
    )

    # return response
