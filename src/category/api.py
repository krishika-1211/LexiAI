from typing import List

from fastapi import APIRouter, HTTPException, status

from src.category.crud import category_crud, topic_crud
from src.category.schemas import (
    CategoryRequest,
    CategoryResponse,
    TopicRequest,
    TopicResponse,
)
from src.user.models import UserRoles
from src.user.utils.deps import is_authorized, is_authorized_for
from utils.db.session import get_db

category_router = APIRouter()


@category_router.post(
    "/category", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
def add_category(
    request: CategoryRequest, user_db: is_authorized_for([UserRoles.ADMIN.value])
):
    user, db = user_db

    return category_crud.create(db, obj_in=request, created_by=user.email)


@category_router.get(
    "/category", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK
)
def get_category(db: get_db, authenticated: is_authorized):
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    categories = category_crud.get_multi(db=db)
    return categories


@category_router.post(
    "/topic", response_model=TopicResponse, status_code=status.HTTP_201_CREATED
)
def add_topic(
    request: TopicRequest, user_db: is_authorized_for([UserRoles.ADMIN.value])
):
    user, db = user_db

    return topic_crud.create(db, obj_in=request, created_by=user.email)


@category_router.get(
    "/topic", response_model=List[TopicResponse], status_code=status.HTTP_200_OK
)
def get_topic(db: get_db, authenticated: is_authorized):
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    topics = topic_crud.get_multi(db=db)
    return topics
