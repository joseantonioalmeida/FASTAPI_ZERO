import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from fastapi_zero import security as security_mod
from fastapi_zero.routers import auth as auth_mod
from fastapi_zero.routers import users as users_mod


class DummyUser:
    def __init__(
        self,
        id=1,
        username='Test',
        email='teste@gmail.com',
        password='hashed',
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password = password


class DummyForm:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class DummySession:
    def __init__(
        self,
        scalar_return=None,
        scalars_return=None,
        refresh_raises=False,
    ):
        self._scalar = scalar_return
        self._scalars = scalars_return
        self._refresh_raises = refresh_raises

    async def scalar(self, *args, **kwargs):
        return self._scalar

    async def scalars(self, *args, **kwargs):
        return self._scalars

    def add(self, obj):
        self._added = obj

    async def commit(self):  # noqa: PLR6301
        return None

    async def refresh(self, obj):
        if self._refresh_raises:
            raise IntegrityError('msg', params=None, orig=None)

    async def delete(self, obj):  # noqa: PLR6301
        return None


@pytest.mark.asyncio
async def test_login_for_access_token_direct_user_not_found():
    form = DummyForm('no@user.com', 'pw')
    session = DummySession(scalar_return=None)
    with pytest.raises(HTTPException):
        await auth_mod.login_for_access_token(form, session)


@pytest.mark.asyncio
async def test_login_for_access_token_direct_wrong_password(monkeypatch):
    user = DummyUser()
    form = DummyForm(user.email, 'wrong')
    session = DummySession(scalar_return=user)

    monkeypatch.setattr(auth_mod, 'verify_password', lambda a, b: False)

    with pytest.raises(HTTPException):
        await auth_mod.login_for_access_token(form, session)


@pytest.mark.asyncio
async def test_login_for_access_token_direct_success(monkeypatch):
    user = DummyUser()
    form = DummyForm(user.email, 'pw')
    session = DummySession(scalar_return=user)

    monkeypatch.setattr(auth_mod, 'verify_password', lambda a, b: True)
    monkeypatch.setattr(auth_mod, 'create_access_token', lambda data: 'tok')

    result = await auth_mod.login_for_access_token(form, session)
    assert result['token_type'] == 'Bearer'
    assert 'access_token' in result


@pytest.mark.asyncio
async def test_create_user_conflicts_and_success(monkeypatch):
    # conflict by username
    existing = DummyUser(username='u1', email='e1')
    new_user = type('U', (), {'username': 'u1', 'email': 'x', 'password': 'p'})
    session = DummySession(scalar_return=existing)
    with pytest.raises(HTTPException):
        await users_mod.create_user(new_user, session)

    # conflict by email
    existing2 = DummyUser(username='u2', email='e2')
    new_user2 = type(
        'U', (), {'username': 'other', 'email': 'e2', 'password': 'p'}
    )
    session2 = DummySession(scalar_return=existing2)
    with pytest.raises(HTTPException):
        await users_mod.create_user(new_user2, session2)

    # success path
    new_user3 = type(
        'U', (), {'username': 'ok', 'email': 'ok@x', 'password': 'p'}
    )
    session3 = DummySession(scalar_return=None)

    # monkeypatch hashing to avoid heavy deps
    monkeypatch.setattr(users_mod, 'get_password_hash', lambda p: 'h')

    res = await users_mod.create_user(new_user3, session3)
    assert hasattr(res, 'username')
    assert res.username == 'ok'


@pytest.mark.asyncio
async def test_update_user_integrity_error(monkeypatch):
    current = DummyUser()
    user_payload = type(
        'U', (), {'username': 'x', 'email': 'y', 'password': 'p'}
    )
    # session.refresh will raise IntegrityError
    session = DummySession(scalar_return=current, refresh_raises=True)

    with pytest.raises(HTTPException):
        await users_mod.update_user(current.id, user_payload, session, current)


@pytest.mark.asyncio
async def test_delete_user_returns_message():
    current = DummyUser()
    session = DummySession(scalar_return=current)
    res = await users_mod.delete_user(current.id, session, current)
    assert res == {'message': 'User deleted'}


@pytest.mark.asyncio
async def test_read_users_direct():
    # prepare a dummy scalars result (list-like)
    user = DummyUser()

    class ScalarResult(list):
        pass

    scalars = ScalarResult([user])
    session = DummySession(scalars_return=scalars)

    class FP:
        def __init__(self):
            self.limit = 10
            self.offset = 0

    res = await users_mod.read_users(session, user, FP())
    assert isinstance(res, dict)
    assert 'users' in res


@pytest.mark.asyncio
async def test_get_current_user_invalid_and_missing_subject(monkeypatch):
    # decode raises DecodeError
    def _raise_decode(*args, **kwargs):
        raise security_mod.DecodeError()

    monkeypatch.setattr(security_mod, 'decode', _raise_decode)
    with pytest.raises(HTTPException):
        await security_mod.get_current_user(
            session=DummySession(), token='tok'
        )

    # decode returns payload without sub
    monkeypatch.setattr(security_mod, 'decode', lambda *a, **k: {})
    with pytest.raises(HTTPException):
        await security_mod.get_current_user(
            session=DummySession(scalar_return=None), token='tok'
        )


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(monkeypatch):
    # decode returns a subject email but DB has no user
    monkeypatch.setattr(
        security_mod, 'decode', lambda *a, **k: {'sub': 'no@one@example.com'}
    )
    with pytest.raises(HTTPException):
        await security_mod.get_current_user(
            session=DummySession(scalar_return=None), token='tok'
        )


@pytest.mark.asyncio
async def test_get_current_user_success(monkeypatch):
    # decode returns a subject email and DB returns a user
    user = DummyUser(email='found@example.com')
    monkeypatch.setattr(
        security_mod, 'decode', lambda *a, **k: {'sub': 'found@example.com'}
    )
    session = DummySession(scalar_return=user)
    res = await security_mod.get_current_user(session=session, token='tok')
    assert res is user


@pytest.mark.asyncio
async def test_update_user_success(monkeypatch):
    current = DummyUser()
    user_payload = type(
        'U', (), {'username': 'ok2', 'email': 'ok2@x', 'password': 'p'}
    )
    session = DummySession(scalar_return=current, refresh_raises=False)

    # monkeypatch hashing function
    monkeypatch.setattr(users_mod, 'get_password_hash', lambda p: 'h2')

    res = await users_mod.update_user(
        current.id, user_payload, session, current
    )
    assert res is current
