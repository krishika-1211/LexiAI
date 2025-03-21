import os
from datetime import datetime

import stripe
import stripe.error
from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from src.billing.models import Invoice, Payment, Plan, Subscription
from src.billing.schemas import PlanRequest
from src.user.models import User

load_dotenv()


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
success_url = os.getenv("STRIPE_SUCCESS_URL")
cancel_url = os.getenv("STRIPE_CANCEL_URL")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


class StripeService:
    def __init__(self):
        pass

    def create_customer(self, email: str):
        customer = stripe.Customer.create(email=email)
        return customer

    def create_product_and_price(
        self, db: Session, obj_in: PlanRequest, created_by: str
    ):
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

    def create_checkout_session(self, db: Session, obj_in: str, customer_id: str):
        obj_in_data = jsonable_encoder(obj_in)
        plan = db.query(Plan).filter(Plan.name == obj_in_data["plan_name"]).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
            )

        user = db.query(User).filter(User.customer_id == customer_id).first()

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer_email=user.email,
            line_items=[
                {
                    "price": plan.price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session

    def verify_webhook_signature(self, payload: bytes, sig_header: str):
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            return event

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
            )

        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
            )

    def add_subscription(self, db: Session, subscription_id: str):
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

    def add_invoice(self, db: Session, invoice: dict):
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

    def add_payment(self, db: Session, session: dict, subscription_id):
        subscription = (
            db.query(Subscription)
            .filter(Subscription.subscription_id == subscription_id)
            .first()
        )

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
