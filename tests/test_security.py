from jwt import decode

from fastapi_zero.security import ALGORITHM, SECRET_KEY, create_acess_token


def test_jwt():
    data = {'mensagem': 'test'}
    token = create_acess_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)

    assert decoded['mensagem'] == data['mensagem']
    assert 'exp' in decoded
