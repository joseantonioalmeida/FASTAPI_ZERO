from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import Todo, User
from fastapi_zero.schemas import TodoPublic, TodoSchema
from fastapi_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
Current_User = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema,
    current_user: Current_User,
    session: T_Session,
):
    db_todo = Todo(
        user_id=current_user.id,
        title=todo.title,
        description=todo.description,
        state=todo.state,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo
