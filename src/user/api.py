import logging
import uuid

from fastapi import APIRouter, HTTPException, status

from src.user.crud import user_crud
from src.user.schemas import LoginRequest, Token, UserBase, UserRequest
from src.user.utils.deps import auth_provider
from src.user.utils.utils import get_sso_user
from utils.db.session import get_db

logger = logging.getLogger(__name__)

user_router = APIRouter()


@user_router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_req: UserRequest, db: get_db):
    if user_crud.get_by_email(db, user_req.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    user_id = str(uuid.uuid4())
    user = user_crud.create(
        db,
        obj_in=UserBase(
            id=user_id, created_by=user_id, updated_by=user_id, **user_req.model_dump()
        ),
    )
    return Token(user=user, token=user.create_token())


@user_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(login_creds: LoginRequest, db: get_db):
    user = user_crud.get_by_email(db, login_creds.email)
    if not user or (not user.verify_password(login_creds.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return Token(user=user, token=user.create_token())


@user_router.get("/auth/{provider}", status_code=status.HTTP_200_OK)
def auth(provider: auth_provider):
    return {"auth_url": provider.get_authorization_url()}


@user_router.get(
    "/auth/{provider}/callback", status_code=status.HTTP_200_OK, response_model=Token
)
def auth_callback(code: str, provider: auth_provider, db: get_db):
    access_token = provider.get_access_token(code)
    email = provider.get_user_info(access_token)
    user = get_sso_user(db, email)
    return Token(user=user, token=user.create_token())
