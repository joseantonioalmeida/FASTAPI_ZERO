from http import HTTPStatus

from jwt import decode, encode

from fastapi_zero.security import create_access_token


def test_jwt(settings):
    data = {'mensagem': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)

    assert decoded['mensagem'] == data['mensagem']
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1/', headers={'Authorization': 'Bearer token-invalid'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_invalid_not_subject_email(client, settings):
    token_sem_sub = encode({}, settings.SECRET_KEY, settings.ALGORITHM)
    response = client.delete(
        '/users/1/', headers={'Authorization': f'Bearer {token_sem_sub}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
