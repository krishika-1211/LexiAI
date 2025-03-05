from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String

from utils.db.base import ModelBase


class Topic(ModelBase):
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    category_id = Column(String, ForeignKey("category.id", ondelete="CASCADE"))

    category = relationship("Category", back_populates="topic")
    session = relationship(
        "src.conversation.models.ConversationSession",
        back_populates="topic",
        cascade="all, delete",
    )


class Category(ModelBase):
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    topic = relationship("Topic", back_populates="category", cascade="all, delete")
