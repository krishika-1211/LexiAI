import random
import smtplib
import string
import uuid
from email.message import EmailMessage

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.config import Config
from src.user.crud import user_crud
from src.user.schemas import UserBase


def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def get_sso_user(db: Session, email: str, given_name: str, family_name: str):
    # check if user already exists
    email = email.lower()
    user = user_crud.get_by_email(db, email)
    if user:
        return user

    # create user if not exists
    user_id = str(uuid.uuid4())
    user = user_crud.create(
        db,
        obj_in=UserBase(
            id=user_id,
            email=email,
            email_verified=True,
            password=generate_random_password(),
            firstname=given_name,
            lastname=family_name,
            created_by=user_id,
            updated_by=user_id,
        ),
    )

    return user


def send_reset_email(email: str, token: str):
    reset_link = f"http://localhost:3000/reset-password/{token}"

    subject = "Password Reset Request"
    body = (
        f"Click the link below to reset your password:\n{reset_link}\n\ntoken:{token}"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = Config.FROM_MAIL
    msg["To"] = email
    msg.set_content(body)

    try:
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.login(Config.SMTP_USER, Config.SMTP_PASS)
            server.send_message(msg)

    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to send email through MailMug SMTP service."
        )
