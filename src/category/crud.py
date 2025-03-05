from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.category.models import Category, Topic
from src.category.schemas import (
    CategoryRequest,
    CategoryResponse,
    TopicRequest,
    TopicResponse,
)
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


topic_crud = TopicCRUD(Topic)
