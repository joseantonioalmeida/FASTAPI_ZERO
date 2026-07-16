from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from factory import Factory, LazyAttribute, Sequence  # type:ignore
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import User, table_registry
from fastapi_zero.security import get_password_hash
from fastapi_zero.settings import Settings


class UserFactory(Factory):
    class Meta:
        model = User

    username = Sequence(lambda n: f'test{n}')
    email = LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = LazyAttribute(lambda obj: f'{obj.username}&AdSfGr231Lkv')


@pytest.fixture
def client(session: AsyncSession):
    # Arange
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)

        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session
    finally:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(table_registry.metadata.drop_all)
        finally:
            await engine.dispose()


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 6, 23)):

    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(User, 'before_insert', fake_time_hook)

    yield time

    event.remove(User, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = 'teste123'
    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password  # type:ignore

    return user


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):
    password = 'teste123'
    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password  # type:ignore

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token/',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def settings():

    return Settings()  # type:ignore
