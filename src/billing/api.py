from fastapi import APIRouter, HTTPException, Request, status

from src.billing.crud import stripe_service
from src.billing.schemas import PlanRequest, PlanResponse, SubscriptionRequest
from src.user.utils.deps import authenticated_user
from utils.db.session import get_db

billing_router = APIRouter()


@billing_router.post(
    "/product", response_model=PlanResponse, status_code=status.HTTP_201_CREATED
)
def create_product(request: PlanRequest, authenticated: authenticated_user):
    user, db = authenticated
    product = stripe_service.create_product_and_price(
        db=db, obj_in=request, created_by=user.email
    )
    return product


@billing_router.post("/checkout-session", status_code=status.HTTP_200_OK)
def checkout_session(request: SubscriptionRequest, authenticated: authenticated_user):
    user, db = authenticated
    session = stripe_service.create_checkout_session(
        db=db, obj_in=request, customer_id=user.customer_id
    )
    return {"checkout_url": session.url, "session_id": session.id}


@billing_router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request, db: get_db):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe_service.verify_webhook_signature(payload, sig_header)
        print(event)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            subscription_id = session["subscription"]

            stripe_service.add_subscription(db, subscription_id)
            stripe_service.add_payment(db, session, subscription_id)

        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]

            stripe_service.add_invoice(db, invoice)

        return {"message": "success"}
    except HTTPException as e:
        print("Webhook Error : ", e.detail)
        raise e
