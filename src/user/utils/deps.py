from typing import Annotated, Tuple

import jwt
from fastapi import (
    Depends,
    Header,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.orm import Session

from src.config import Config
from src.user.crud import user_crud
from src.user.models import AuthProvider, User
from src.user.utils.sso import BaseSSO
from src.user.utils.sso.google_sso import GoogleSSO
from utils.db.session import get_db


def _authenticated(authorization: str = Header(None, alias="Authorization")):
    try:
        authorization = authorization.strip().replace("Bearer ", "")
        jwt.decode(
            authorization, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
        )

        return True

    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


def _authenticated_user(
    db: get_db, authorization: str = Header(None, alias="Authorization")
) -> Tuple[User, Session]:
    try:
        user = None
        if authorization:
            payload = jwt.decode(
                authorization.split()[1],
                Config.JWT_SECRET_KEY,
                algorithms=[Config.JWT_ALGORITHM],
            )
            user_id = payload["id"]
            if not user_id:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

            user = user_crud.get(db, id=user_id)
            if not user:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid User")
        else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authorization not found")

        return user, db

    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


is_authorized = Annotated[bool, Depends(_authenticated)]
authenticated_user = Annotated[Tuple[User, Session], Depends(_authenticated_user)]


async def _websocket_authenticated(db: get_db, websocket: WebSocket):
    token = websocket.headers.get("Authorization")
    if not token:
        await websocket.close(code=403)
        raise WebSocketDisconnect(code=403)

    payload = jwt.decode(
        token,
        Config.JWT_SECRET_KEY,
        algorithms=[Config.JWT_ALGORITHM],
    )

    user_id = payload["id"]
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    user = user_crud.get(db, id=user_id)

    return user, db


websocket_authenticated = Annotated[
    Tuple[User, Session], Depends(_websocket_authenticated)
]


def _is_authorized_for(roles: list):
    def _is_authorized(user_db: authenticated_user):
        user, db = user_db
        if user.role not in roles:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
        return user, db

    return _is_authorized


is_authorized_for = lambda _roles: Annotated[
    Tuple[User, Session], Depends(_is_authorized_for(_roles))
]


def get_auth_provider(provider: AuthProvider) -> BaseSSO:
    if provider == AuthProvider.GOOGLE:
        return GoogleSSO()
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid provider")


auth_provider = Annotated[BaseSSO, Depends(get_auth_provider)]


def verify_reset_token(token):
    try:
        payload = jwt.decode(
            token, key=Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
        )
        email = payload.get("email")
        if email is None:
            return None
        return email
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
