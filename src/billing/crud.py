from datetime import datetime

import stripe
import stripe.error
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from src.billing.models import Invoice, Payment, Plan, Subscription
from src.billing.schemas import PlanRequest
from src.config import Config
from src.user.models import User

stripe.api_key = Config.STRIPE_API_KEY


class StripeService:
    @staticmethod
    def create_customer(db: Session, user: User):
        if not user.customer_id:
            customer = stripe.Customer.create(email=user.email)
            user.customer_id = customer.id
            db.commit()
            db.refresh(user)

        return user.customer_id

    @staticmethod
    def create_product_and_price(db: Session, obj_in: PlanRequest, created_by: str):
        obj_in_data = jsonable_encoder(obj_in)
        product = stripe.Product.create(
            name=obj_in_data["name"], description=obj_in_data["description"]
        )

        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(obj_in_data["amount"] * 100),
            currency=obj_in_data["currency"],
            recurring={"interval": obj_in_data["interval"]},
        )
        db_obj = Plan(
            name=obj_in_data["name"],
            description=obj_in_data["description"],
            product_id=product.id,
            price_id=price.id,
            amount=obj_in_data["amount"],
            currency=obj_in_data["currency"],
            interval=obj_in_data["interval"],
            allowed_conversations=obj_in_data["allowed_conversations"],
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def create_checkout_session(db: Session, obj_in: str, customer_id: str):
        obj_in_data = jsonable_encoder(obj_in)
        plan = db.query(Plan).filter(Plan.name == obj_in_data["plan_name"]).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
            )

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer=customer_id,
            line_items=[
                {
                    "price": plan.price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=Config.STRIPE_SUCCESS_URL,
            cancel_url=Config.STRIPE_CANCEL_URL,
        )
        return session

    @staticmethod
    def verify_webhook_signature(payload: bytes, sig_header: str):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
            )
            return event

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
            )

        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
            )

    @staticmethod
    def add_subscription(db: Session, subscription_id: str):
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription["items"]["data"][0]["price"]["id"]
        current_period_end = datetime.fromtimestamp(subscription.current_period_end)

        user = db.query(User).filter(User.customer_id == subscription.customer).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        created_by = user.email
        plan = db.query(Plan).filter(Plan.price_id == price_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
            )

        db_obj = Subscription(
            subscription_id=subscription_id,
            status=subscription.status,
            current_period_end=current_period_end,
            user_id=user.id,
            plan_id=plan.id,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def add_invoice(db: Session, invoice: dict):
        invoice_id = invoice["id"]
        subscription_id = invoice["subscription"]
        amount_due = invoice["amount_due"]
        amount_paid = invoice["amount_paid"]
        status = invoice["status"]
        customer = invoice["customer"]

        subscription = (
            db.query(Subscription)
            .filter(Subscription.subscription_id == subscription_id)
            .first()
        )

        user = db.query(User).filter(User.customer_id == customer).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        created_by = user.email

        db_obj = Invoice(
            invoice_id=invoice_id,
            subscription_id=subscription.id,
            user_id=user.id,
            amount_due=amount_due,
            amount_paid=amount_paid,
            status=status,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def add_payment(db: Session, session: dict, subscription_id):
        invoice_id = session["invoice"]
        invoice = stripe.Invoice.retrieve(invoice_id)
        payment_id = invoice["payment_intent"]
        payment_intent = stripe.PaymentIntent.retrieve(payment_id)
        amount = payment_intent["amount_received"]
        currency = payment_intent["currency"]
        status = payment_intent["status"]
        customer = session["customer"]

        subscription = (
            db.query(Subscription)
            .filter(Subscription.subscription_id == subscription_id)
            .first()
        )
        user = db.query(User).filter(User.customer_id == customer).first()
        created_by = user.email

        db_obj = Payment(
            payment_id=payment_id,
            user_id=user.id,
            subscription_id=subscription.id,
            amount=amount,
            currency=currency,
            status=status,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


stripe_service = StripeService()
