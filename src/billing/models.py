from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from utils.db.base import ModelBase


class Plan(ModelBase):
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    product_id = Column(String, nullable=False, unique=True)
    price_id = Column(String, nullable=False, unique=True)
    amount = Column(Integer)
    currency = Column(String, default="usd")
    interval = Column(String, default="month")
    allowed_conversations = Column(Integer, nullable=True)


class Subscription(ModelBase):
    subscription_id = Column(String, unique=True)
    status = Column(String)
    current_period_end = Column(DateTime)

    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    plan_id = Column(String, ForeignKey("plan.id"))

    customer = relationship("src.user.models.User", back_populates="subscription")
    plan = relationship("Plan")


class Payment(ModelBase):
    payment_id = Column(String, unique=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    subscription_id = Column(String, ForeignKey("subscription.id"))
    amount = Column(Integer)
    status = Column(String)
    currency = Column(String)

    customer = relationship("src.user.models.User", back_populates="payment")
    subscription = relationship("Subscription")


class Invoice(ModelBase):
    invoice_id = Column(String, unique=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    subscription_id = Column(String, ForeignKey("subscription.id"))
    amount_due = Column(Integer)
    amount_paid = Column(Integer)
    status = Column(String)

    customer = relationship("src.user.models.User", back_populates="invoice")
    subscription = relationship("Subscription")
