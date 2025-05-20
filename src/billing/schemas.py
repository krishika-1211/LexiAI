from datetime import datetime

from pydantic import BaseModel


class PlanRequest(BaseModel):
    name: str
    description: str
    amount: int
    currency: str = "usd"
    interval: str = "month"
    allowed_conversations: int


class PlanResponse(PlanRequest):
    id: str
    product_id: str
    price_id: str


class SubscriptionRequest(BaseModel):
    plan_name: str


class SubscriptionResponse(BaseModel):
    subscription_id: str
    status: str
    customer_period_end: datetime
