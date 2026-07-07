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
