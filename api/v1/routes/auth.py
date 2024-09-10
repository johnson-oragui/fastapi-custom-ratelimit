from typing import Annotated
from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.utils.check_rate_limit import check_rate_limits_sync
from api.utils.background.producer import send_to_queue_sync
from api.v1.services.auth import (RegisterUserResponse,
                                  auth_service,
                                  RegisterUserSchema,
                                  oauth2_scheme,
                                  OAuth2,
                                  AccessToken)
from api.db.database import get_db
from api.v1.schemas.user import LoginUserSchema, LoginUserResponse


auth = APIRouter(prefix='/auth', tags=['AUTH'])

@auth.post('/login',
           status_code=status.HTTP_200_OK,
           response_model=LoginUserResponse)
async def login(request: Request,
                login_schema: LoginUserSchema,
                db: Annotated[AsyncSession, Depends(get_db)]):
    """sumary_line
    
        Keyword arguments:
            argument -- description
        Return:
            return_description
    """
    check_rate_limits_sync(request)
    user_ip: str = request.client.host
    path: str = request.url.path
    message_body: str = f'{user_ip},{path}'
    send_to_queue_sync(message_body)
    return await auth_service.login_user(
        login_schema.username,
        login_schema.password,
        db
    )


@auth.post('/register',
           status_code=status.HTTP_200_OK,
           response_model=RegisterUserResponse)
async def register(request: Request,
                   register_schema: RegisterUserSchema,
                   db: Annotated[AsyncSession, Depends(get_db)]):
    """Registers a user.
    """
    check_rate_limits_sync(request)
    user_ip: str = request.client.host
    path: str = request.url.path
    message_body: str = f'{user_ip},{path}'
    send_to_queue_sync(message_body)
    return await auth_service.create(register_schema, db)

@auth.post('/token',
           status_code=status.HTTP_200_OK,
           response_model=AccessToken,
           include_in_schema=False)
async def token(request: Request,
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Annotated[AsyncSession, Depends(get_db)]):
    """Logs in a user.
    """
    check_rate_limits_sync(request)
    user_ip: str = request.client.host
    path: str = request.url.path
    message_body: str = f'{user_ip},{path}'
    send_to_queue_sync(message_body)
    
    return await auth_service.oauth2_authenticate(
        form_data.username,
        form_data.password,
        db
    )

@auth.post('/others',
           status_code=status.HTTP_200_OK)
async def get(request: Request,
              token: Annotated[OAuth2, Depends(oauth2_scheme)],
              db: Annotated[AsyncSession, Depends(get_db)]):
    """Placeholder for other routes.
    """
    check_rate_limits_sync(request)
    user_ip: str = request.client.host
    path: str = request.url.path
    message_body: str = f'{user_ip},{path}'
    send_to_queue_sync(message_body)
    await auth_service.get_current_active_user(token, db)
    return {'message': 'others route attempt recorded'}
