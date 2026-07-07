from http import HTTPStatus


def test_login_for_access_token(client, user):
    response = client.post(
        '/auth/token/',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_login_for_access_token_not_user(client):
    response = client.post(
        '/auth/token/',
        data={'username': 'teste@gmail.com', 'password': 'teste321'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_for_access_token_not_verify_password(client, user):
    response = client.post(
        '/auth/token/',
        data={'username': user.email, 'password': 'senha-errada'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
