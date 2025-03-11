from typing import Any, Dict, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from src.conversation.models import ConversationSession, Report
from src.user.models import User
from src.user.schemas import UserBase, UserStatsResponse, UserUpdate
from utils.crud.base import CRUDBase


# user crud
class UserCRUD(CRUDBase[User, UserBase, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserBase) -> User:
        obj_in_data: dict = jsonable_encoder(obj_in, exclude_unset=True)
        password = obj_in_data.pop("password", None)
        db_obj = self.model(**obj_in_data)
        if password:
            db_obj.set_password(password)
        db.add(db_obj)
        db.commit()
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        obj_data: dict = jsonable_encoder(db_obj, exclude_unset=True)
        password = obj_data.pop("password", None)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        if password:
            db_obj.set_password(password)
        db.add(db_obj)
        db.commit()
        return db_obj

    def get_user_stats(self, db: Session, user_id: str) -> UserStatsResponse:
        total_session = db.query(ConversationSession).filter_by(user_id=user_id).count()

        avg_score = (
            db.query(func.avg(Report.score))
            .join(ConversationSession)
            .filter(ConversationSession.user_id == user_id)
            .scalar()
            or 0
        )

        high_score = (
            db.query(func.max(Report.score))
            .join(ConversationSession)
            .filter(ConversationSession.user_id == user_id)
            .scalar()
            or 0
        )

        return UserStatsResponse(
            total_session=total_session,
            avg_score=round(avg_score, 2),
            high_score=round(high_score, 2),
        )


user_crud = UserCRUD(User)
