import logging
import uuid

from fastapi import APIRouter, HTTPException, status

from src.billing.crud import stripe_service
from src.user.crud import user_crud
from src.user.schemas import (
    ForgotRequest,
    LoginRequest,
    ResetRequest,
    Token,
    UserBase,
    UserRequest,
    UserStatsResponse,
)
from src.user.utils.deps import auth_provider, authenticated_user, verify_reset_token
from src.user.utils.utils import get_sso_user, send_reset_email
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
    customer = stripe_service.create_customer(user_req.email)
    user = user_crud.create(
        db,
        obj_in=UserBase(
            id=user_id,
            customer_id=customer.id,
            created_by=user_id,
            updated_by=user_id,
            **user_req.model_dump()
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
    (
        email,
        firstname,
        lastname,
    ) = provider.get_user_info(access_token)
    user = get_sso_user(db, email, firstname, lastname)
    return Token(user=user, token=user.create_token())


@user_router.post("/forget-password")
def forgot_password(request: ForgotRequest, db: get_db):
    user = user_crud.get_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    token = user.create_token()

    send_reset_email(request.email, token)

    return {"message": "Password reset link sent to your email"}


@user_router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(request: ResetRequest, db: get_db):
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = user_crud.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.set_password(request.new_password)
    db.commit()

    return {"message": "Password reset successfully"}


@user_router.get(
    "/stats", response_model=UserStatsResponse, status_code=status.HTTP_200_OK
)
def get_user_stats(authenticated: authenticated_user):
    user, db = authenticated

    stats = user_crud.get_user_stats(db, user.id)

    if stats.total_session == 0:
        return UserStatsResponse(total_session=0, avg_score=0.0, high_score=0.0)

    return stats
