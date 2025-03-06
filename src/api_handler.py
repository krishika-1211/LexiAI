from fastapi import APIRouter

from src.category.api import category_router
from src.conversation.api import session_router
from src.user.api import user_router

# Router
api_router = APIRouter()

# User
api_router.include_router(user_router, include_in_schema=True, tags=["User APIs"])

# Category
api_router.include_router(
    category_router, include_in_schema=True, tags=["Category APIs"]
)
api_router.include_router(session_router, include_in_schema=True, tags=["User_Stats"])
