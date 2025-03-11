from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from src.category.models import Category, Topic
from src.category.schemas import (
    CategoryRequest,
    CategoryResponse,
    TopicRequest,
    TopicResponse,
)
from src.conversation.models import Report
from utils.crud.base import CRUDBase


class CategoryCRUD(CRUDBase[Category, CategoryRequest, CategoryResponse]):
    def create(self, db: Session, obj_in: CategoryRequest, created_by: str) -> Category:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Category(**obj_in_data, created_by=created_by, updated_by=created_by)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


category_crud = CategoryCRUD(Category)


class TopicCRUD(CRUDBase[Topic, TopicRequest, TopicResponse]):
    def create(self, db: Session, obj_in: TopicRequest, created_by: str) -> Topic:
        category_name = obj_in.category
        category = db.query(Category).filter(Category.name == category_name).first()

        if not category:
            return NoResultFound(f"Category name with {category_name} is not found")

        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data.pop("category", None)

        db_obj = Topic(
            **obj_in_data,
            category_id=category.id,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_category(
        self, db: Session, category_name: Optional[str] = None
    ) -> List[Topic]:
        if category_name:
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                raise NoResultFound(f"Category '{category_name}' not found")
            return db.query(Topic).filter(Topic.category_id == category.id).all()

        return db.query(Topic).all()

    def get_high_score(self, db: Session, topic_name: str) -> Optional[float]:
        topic = db.query(Topic).filter(Topic.name == topic_name).first()
        if not topic:
            raise NoResultFound(f"Topic '{topic_name}' not found")

        high_score = (
            db.query(func.max(Report.score))
            .filter(Report.topic_id == topic.id)
            .scalar()
        )
        return high_score

    def get_user_score(
        self, db: Session, user_id: str, topic_id: str
    ) -> Optional[float]:
        user_score = (
            db.query(func.max(Report.score))
            .filter(Report.topic_id == topic_id, Report.user_id == user_id)
            .scalar()
        )
        return user_score


topic_crud = TopicCRUD(Topic)
