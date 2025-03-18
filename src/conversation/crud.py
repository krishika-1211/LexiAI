from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.billing.models import Plan, Subscription
from src.user.models import User


class ConversationCrud:
    def __init__(self):
        pass

    def check_conversation_permission(self, db: Session, user_id: str):
        subscription = (
            db.query(Subscription).filter(Subscription.user_id == user_id).first()
        )
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have subscription",
            )

        plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan with the subscription not found",
            )

        allowed_conversations = plan.allowed_conversations

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.used_conversations >= allowed_conversations:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You exceeded allowed conversations for the subscription plan",
            )

        user.used_conversations += 1
        db.commit()
        db.refresh(user)

        return {
            "message": "Permission granted",
            "remaining_conversations": allowed_conversations - user.used_conversations,
        }


conversation_crud = ConversationCrud()
