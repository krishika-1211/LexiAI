from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import NoResultFound

from src.category.crud import category_crud, topic_crud
from src.category.schemas import (
    CategoryRequest,
    CategoryResponse,
    TopicRequest,
    TopicResponse,
)
from src.user.models import UserRoles
from src.user.utils.deps import authenticated_user, is_authorized, is_authorized_for
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
def get_topic(authenticated: authenticated_user, category_name: Optional[str] = None):
    user, db = authenticated

    try:
        topics = topic_crud.get_by_category(db, category_name)

        topic_responses = []
        for topic in topics:
            high_score = topic_crud.get_high_score(db, topic.name)
            your_score = topic_crud.get_user_score(db, user.id, topic.id)

            topic_responses.append(
                TopicResponse(
                    id=topic.id,
                    name=topic.name,
                    description=topic.description,
                    category_id=topic.category_id,
                    high_score=high_score,
                    your_score=your_score,
                    created_by=topic.created_by,
                    updated_by=topic.updated_by,
                )
            )

        return topic_responses

    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
